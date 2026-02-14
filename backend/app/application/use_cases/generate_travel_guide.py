"""旅行ガイド生成ユースケース"""

from __future__ import annotations

import ast
import asyncio
import hashlib
import logging
import re
import time
from typing import Any
from urllib.parse import urlparse

from pydantic import ValidationError

from app.application.dto.travel_guide_dto import TravelGuideDTO
from app.application.ports.ai_service import IAIService
from app.application.ports.spot_image_job_repository import ISpotImageJobRepository
from app.application.ports.spot_image_task_dispatcher import ISpotImageTaskDispatcher
from app.application.use_cases.travel_plan_helpers import validate_required_str
from app.config.settings import get_settings
from app.domain.travel_guide.repository import ITravelGuideRepository
from app.domain.travel_guide.services import TravelGuideComposer
from app.domain.travel_guide.value_objects import (
    Checkpoint,
    HistoricalEvent,
    SpotDetail,
)
from app.domain.travel_plan.entity import TouristSpot, TravelPlan
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.repository import ITravelPlanRepository
from app.domain.travel_plan.value_objects import GenerationStatus
from app.infrastructure.ai.schemas.travel_guide import TravelGuideResponseSchema
from app.prompts import load_template, render_template

_TRAVEL_GUIDE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "overview": {
            "type": "string",
            "description": "旅行全体の概要。以下の4要素を含む充実した概要文（200-400文字程度）: 1) 旅行のテーマや目的、2) 訪問スポットの関連性、3) 歴史的時代背景、4) おすすめポイント",
            "minLength": 100,
        },
        "timeline": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer"},
                    "event": {"type": "string"},
                    "significance": {"type": "string"},
                    "relatedSpots": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                },
                "required": ["year", "event", "significance", "relatedSpots"],
            },
            "minItems": 1,
        },
        "spotDetails": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "spotName": {"type": "string"},
                    "historicalBackground": {"type": "string"},
                    "highlights": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "recommendedVisitTime": {"type": "string"},
                    "historicalSignificance": {"type": "string"},
                },
                "required": [
                    "spotName",
                    "historicalBackground",
                    "highlights",
                    "recommendedVisitTime",
                    "historicalSignificance",
                ],
            },
            "minItems": 1,
        },
        "checkpoints": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "spotName": {"type": "string"},
                    "checkpoints": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "historicalContext": {"type": "string"},
                },
                "required": ["spotName", "checkpoints", "historicalContext"],
            },
            "minItems": 1,
        },
    },
    "required": ["overview", "timeline", "spotDetails", "checkpoints"],
}

_FACT_EXTRACTION_PROMPT_TEMPLATE = "travel_guide_fact_extraction_prompt.txt"
_TRAVEL_GUIDE_PROMPT_TEMPLATE = "travel_guide_prompt.txt"
_FACT_EXTRACTION_SYSTEM_INSTRUCTION_TEMPLATE = "travel_guide_fact_extraction_system_instruction.txt"
_TRAVEL_GUIDE_SYSTEM_INSTRUCTION_TEMPLATE = "travel_guide_system_instruction.txt"
_NO_SPOTS_TEXT_TEMPLATE = "travel_guide_no_spots_text.txt"

logger = logging.getLogger(__name__)
_URL_REGEX = re.compile(r"https?://[^\s)\]}>\"']+")
_VALIDATED_SOURCE_MARKER_REGEX = re.compile(r"\[\s*検証\s*[:：]\s*valid\s*\]", flags=re.IGNORECASE)
_MAX_FACT_EXTRACTION_ROUNDS = 4
_MIN_EXTRACTED_URLS_FOR_FACTS = 3
_MAX_GUIDE_REGENERATIONS_ON_UNKNOWN_RELATED_SPOTS = 1


def _normalize_spot_name(spot_name: str) -> str:
    """スポット名を正規化する（空白文字のトリミングのみ）

    Args:
        spot_name: 正規化するスポット名

    Returns:
        正規化されたスポット名（前後の空白文字をトリミング）
    """
    return spot_name.strip()


def _detect_new_spots(
    spot_details: list[SpotDetail], existing_spots: list[TouristSpot]
) -> list[str]:
    """新規スポット名を検出する

    spotDetailsから既存の旅行計画スポットに含まれない新規スポットを検出する。
    spotDetails内の重複は最初の出現のみを保持する。

    Args:
        spot_details: AIが生成したスポット詳細リスト
        existing_spots: 既存の旅行計画スポットリスト

    Returns:
        新規スポット名のリスト（spotDetailsの出現順序を保持）
    """
    # 既存スポット名を正規化してセットに格納
    existing_normalized = {_normalize_spot_name(spot.name) for spot in existing_spots}

    new_spot_names: list[str] = []
    seen_new_normalized: set[str] = set()

    for detail in spot_details:
        normalized = _normalize_spot_name(detail.spot_name)
        # 既存スポットに含まれず、かつ新規リストにも含まれない場合
        if normalized not in existing_normalized and normalized not in seen_new_normalized:
            new_spot_names.append(detail.spot_name)
            seen_new_normalized.add(normalized)

    return new_spot_names


def _create_tourist_spots(new_spot_names: list[str]) -> list[TouristSpot]:
    """新規スポット名からTouristSpotエンティティを作成する

    Args:
        new_spot_names: 新規スポット名のリスト

    Returns:
        TouristSpotエンティティのリスト
    """
    import uuid

    new_spots: list[TouristSpot] = []

    for spot_name in new_spot_names:
        spot_id = str(uuid.uuid4())
        new_spot = TouristSpot(
            id=spot_id,
            name=spot_name,
            description=None,
            user_notes=None,
        )
        new_spots.append(new_spot)

    return new_spots


def _require_str(value: object, field_name: str) -> str:
    """必須の文字列フィールドを検証する"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string.")
    return value.strip()


def _require_min_length(value: str, field_name: str, min_length: int) -> None:
    """文字列の最小長を検証する"""
    if len(value) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters.")


def _require_list(value: object, field_name: str) -> list[Any]:
    """必須の配列フィールドを検証する"""
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} is required and must be a non-empty list.")
    return value


def _require_int(value: object, field_name: str) -> int:
    """整数フィールドの検証"""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be an int.")
    return value


def _extract_urls(text: str) -> set[str]:
    """テキストからURLを抽出する。"""
    urls: set[str] = set()
    for match in _URL_REGEX.findall(text):
        url = match.rstrip(".,;:!?。、）】＞")
        if url:
            urls.add(url)
    return urls


def _extract_validated_urls(text: str) -> set[str]:
    """`[検証: valid]`付き行のURLのみ抽出する。"""
    validated_urls: set[str] = set()
    for line in text.splitlines():
        if not _VALIDATED_SOURCE_MARKER_REGEX.search(line):
            continue
        validated_urls.update(_extract_urls(line))
    return validated_urls


def _collect_urls_from_guide_payload(guide_data: dict[str, Any]) -> set[str]:
    """旅行ガイド構造化データからURLを収集する。"""
    urls: set[str] = set()

    overview = guide_data.get("overview")
    if isinstance(overview, str):
        urls.update(_extract_urls(overview))

    timeline = guide_data.get("timeline")
    if isinstance(timeline, list):
        for item in timeline:
            if not isinstance(item, dict):
                continue
            for key in ("event", "significance"):
                value = item.get(key)
                if isinstance(value, str):
                    urls.update(_extract_urls(value))

    spot_details = guide_data.get("spotDetails")
    if isinstance(spot_details, list):
        for item in spot_details:
            if not isinstance(item, dict):
                continue
            for key in ("historicalBackground", "historicalSignificance", "recommendedVisitTime"):
                value = item.get(key)
                if isinstance(value, str):
                    urls.update(_extract_urls(value))
            highlights = item.get("highlights")
            if isinstance(highlights, list):
                for highlight in highlights:
                    if isinstance(highlight, str):
                        urls.update(_extract_urls(highlight))

    checkpoints = guide_data.get("checkpoints")
    if isinstance(checkpoints, list):
        for item in checkpoints:
            if not isinstance(item, dict):
                continue
            historical_context = item.get("historicalContext")
            if isinstance(historical_context, str):
                urls.update(_extract_urls(historical_context))
            checkpoint_items = item.get("checkpoints")
            if isinstance(checkpoint_items, list):
                for checkpoint in checkpoint_items:
                    if isinstance(checkpoint, str):
                        urls.update(_extract_urls(checkpoint))

    return urls


def _summarize_url_quality(urls: set[str]) -> dict[str, Any]:
    """URLセットの品質情報を集計する。"""
    parsed_pairs = [(url, urlparse(url)) for url in urls]

    malformed_urls = sorted(url for url, parsed in parsed_pairs if not parsed.netloc)
    non_https_urls = sorted(url for url, parsed in parsed_pairs if parsed.scheme.lower() != "https")

    possibly_expiring_urls = sorted(
        url
        for url, parsed in parsed_pairs
        if any(
            token in parsed.query.lower()
            for token in ("x-goog-expires", "x-amz-expires", "x-goog-signature", "token=")
        )
    )
    grounding_redirect_urls = sorted(
        url
        for url, parsed in parsed_pairs
        if parsed.netloc == "vertexaisearch.cloud.google.com"
        and "grounding-api-redirect" in parsed.path
    )
    domains = {parsed.netloc for _, parsed in parsed_pairs if parsed.netloc}

    return {
        "url_count": len(urls),
        "domain_count": len(domains),
        "domains": sorted(domains),
        "malformed_urls": malformed_urls,
        "non_https_urls": non_https_urls,
        "possibly_expiring_urls": possibly_expiring_urls,
        "grounding_redirect_urls": grounding_redirect_urls,
    }


def _spot_has_validated_source_in_facts(spot_name: str, extracted_facts: str) -> bool:
    """抽出事実テキスト内で、スポットに紐づく検証済み出典URLがあるかを判定する。"""
    for line in extracted_facts.splitlines():
        if (
            spot_name in line
            and _URL_REGEX.search(line)
            and _VALIDATED_SOURCE_MARKER_REGEX.search(line)
        ):
            return True
    return False


def _assess_fact_extraction_coverage(
    *,
    extracted_facts: str,
    spot_names: list[str],
) -> dict[str, Any]:
    """StepAの出典充足度を判定する。"""
    extracted_urls = _extract_urls(extracted_facts)
    validated_urls = _extract_validated_urls(extracted_facts)
    missing_spot_sources = [
        spot_name
        for spot_name in spot_names
        if not _spot_has_validated_source_in_facts(spot_name, extracted_facts)
    ]
    min_required_urls = max(_MIN_EXTRACTED_URLS_FOR_FACTS, len(spot_names))
    has_min_urls = len(validated_urls) >= min_required_urls
    sufficient = has_min_urls and not missing_spot_sources

    return {
        "sufficient": sufficient,
        "raw_url_count": len(extracted_urls),
        "validated_url_count": len(validated_urls),
        "min_required_urls": min_required_urls,
        "missing_spot_sources": missing_spot_sources,
    }


def _build_fact_extraction_retry_prompt(
    *,
    base_prompt: str,
    previous_extracted_facts: str,
    missing_spot_sources: list[str],
    min_required_urls: int,
    feedback_round: int,
) -> str:
    """出典不足を補うための再抽出プロンプトを作成する。"""
    validated_urls = sorted(_extract_validated_urls(previous_extracted_facts))
    validated_url_count = len(validated_urls)
    has_enough_validated_urls = validated_url_count >= min_required_urls

    missing_spots_text = "\n".join([f"- {spot_name}" for spot_name in missing_spot_sources])
    if not missing_spots_text:
        missing_spots_text = "- なし"

    reusable_urls_text = "\n".join([f"- {url}" for url in validated_urls[:10]])
    if not reusable_urls_text:
        reusable_urls_text = "- なし"

    if has_enough_validated_urls:
        url_count_instruction = (
            f"前回結果には有効な出典URLが {validated_url_count} 件あり、必要件数（{min_required_urls}件）を満たしています。\n"
            "前回の有効URLを再利用し、新しいURLは原則として追加しないでください。\n"
        )
    else:
        additional_needed = min_required_urls - validated_url_count
        url_count_instruction = (
            f"前回結果の有効な出典URLは {validated_url_count} 件です。最低でも {min_required_urls} 件以上にしてください。\n"
            f"不足している {additional_needed} 件分のみ、必要最小限で新しいURLを追加してください。\n"
        )

    missing_spot_instruction = (
        "次のスポットは特に出典不足です。可能な限り前回の有効URLを再利用し、"
        "不足を補えない場合に限って新しいURLを追加してください。\n"
    )
    if feedback_round <= 1:
        search_expansion_instruction = "検索クエリには同義語・旧称・英語表記を追加し、同一観点の検索語を繰り返さないでください。\n"
    elif feedback_round == 2:
        search_expansion_instruction = (
            "検索クエリに年代・自治体名・施設種別を追加し、前回未使用ドメインを優先してください。\n"
        )
    else:
        search_expansion_instruction = (
            "3回目以降の再試行です。公式機関ドメイン（自治体・博物館・文化財）を優先し、"
            "各スポットで最低1件は別ドメインの新規URLを提示してください。\n"
        )
    blocked_host_instruction = (
        "以下のリダイレクトURLは有効期限付きになりやすいため出典として使用禁止です。\n"
        "- vertexaisearch.cloud.google.com/grounding-api-redirect\n"
    )

    return (
        f"{base_prompt}\n\n"
        "<retry_instructions>\n"
        "前回の抽出結果では出典が不足しています。\n"
        f"{url_count_instruction}"
        "URL出典には必ず `[検証: valid]` を付けてください。\n"
        "前回の有効URL候補（再利用推奨）:\n"
        f"{reusable_urls_text}\n"
        f"{missing_spot_instruction}"
        f"{missing_spots_text}\n"
        f"{blocked_host_instruction}"
        f"{search_expansion_instruction}"
        "前回結果:\n"
        f"{previous_extracted_facts}\n"
        "</retry_instructions>"
    )


def _log_fact_extraction_link_diagnostics(*, plan_id: str, extracted_facts: str) -> None:
    """Step Aの抽出URL品質をログ出力する。"""
    extracted_urls = _extract_urls(extracted_facts)
    validated_urls = _extract_validated_urls(extracted_facts)
    summary = _summarize_url_quality(extracted_urls)

    logger.info(
        "Fact extraction link diagnostics: extracted_urls=%d validated_urls=%d domains=%d malformed=%d non_https=%d expiring=%d grounding_redirect=%d",
        summary["url_count"],
        len(validated_urls),
        summary["domain_count"],
        len(summary["malformed_urls"]),
        len(summary["non_https_urls"]),
        len(summary["possibly_expiring_urls"]),
        len(summary["grounding_redirect_urls"]),
        extra={
            "plan_id": plan_id,
            "extracted_url_count": summary["url_count"],
            "validated_url_count": len(validated_urls),
            "extracted_domain_count": summary["domain_count"],
            "malformed_url_count": len(summary["malformed_urls"]),
            "non_https_url_count": len(summary["non_https_urls"]),
            "possibly_expiring_url_count": len(summary["possibly_expiring_urls"]),
            "grounding_redirect_url_count": len(summary["grounding_redirect_urls"]),
            "extracted_url_samples": sorted(extracted_urls)[:5],
            "malformed_url_samples": summary["malformed_urls"][:5],
            "non_https_url_samples": summary["non_https_urls"][:5],
            "possibly_expiring_url_samples": summary["possibly_expiring_urls"][:5],
            "grounding_redirect_url_samples": summary["grounding_redirect_urls"][:5],
        },
    )


def _log_link_quality_diagnostics(
    *,
    plan_id: str,
    stage: str,
    extracted_facts: str,
    guide_data: dict[str, Any],
) -> None:
    """抽出結果と生成ガイドのURL整合性をログ出力する。"""
    extracted_urls = _extract_urls(extracted_facts)
    guide_urls = _collect_urls_from_guide_payload(guide_data)

    extracted_summary = _summarize_url_quality(extracted_urls)
    guide_summary = _summarize_url_quality(guide_urls)
    unmatched_urls = sorted(guide_urls - extracted_urls)
    matched_url_count = len(guide_urls & extracted_urls)
    grounding_coverage = (
        (matched_url_count / guide_summary["url_count"]) if guide_summary["url_count"] > 0 else 1.0
    )
    step_b_urls_fully_grounded = len(unmatched_urls) == 0

    logger.info(
        "Guide link diagnostics: stage=%s extracted_urls=%d guide_urls=%d matched=%d unmatched=%d coverage=%.3f fully_grounded=%s non_https=%d",
        stage,
        extracted_summary["url_count"],
        guide_summary["url_count"],
        matched_url_count,
        len(unmatched_urls),
        grounding_coverage,
        step_b_urls_fully_grounded,
        len(guide_summary["non_https_urls"]),
        extra={
            "plan_id": plan_id,
            "stage": stage,
            "extracted_url_count": extracted_summary["url_count"],
            "guide_url_count": guide_summary["url_count"],
            "matched_url_count": matched_url_count,
            "unmatched_url_count": len(unmatched_urls),
            "grounding_coverage": grounding_coverage,
            "step_b_urls_fully_grounded": step_b_urls_fully_grounded,
            "non_https_url_count": len(guide_summary["non_https_urls"]),
            "malformed_url_count": len(guide_summary["malformed_urls"]),
            "possibly_expiring_url_count": len(guide_summary["possibly_expiring_urls"]),
            "grounding_redirect_url_count": len(guide_summary["grounding_redirect_urls"]),
            "extracted_domain_count": extracted_summary["domain_count"],
            "guide_domain_count": guide_summary["domain_count"],
            "unmatched_url_samples": unmatched_urls[:5],
            "guide_url_samples": sorted(guide_urls)[:5],
            "possibly_expiring_url_samples": guide_summary["possibly_expiring_urls"][:5],
        },
    )

    if unmatched_urls:
        logger.warning(
            "Guide contains URLs not found in extracted facts: stage=%s unmatched=%d samples=%s",
            stage,
            len(unmatched_urls),
            unmatched_urls[:5],
            extra={
                "plan_id": plan_id,
                "stage": stage,
                "unmatched_url_count": len(unmatched_urls),
                "unmatched_url_samples": unmatched_urls[:5],
            },
        )

    if guide_summary["non_https_urls"]:
        logger.warning(
            "Guide contains non-HTTPS URLs: stage=%s count=%d samples=%s",
            stage,
            len(guide_summary["non_https_urls"]),
            guide_summary["non_https_urls"][:5],
            extra={
                "plan_id": plan_id,
                "stage": stage,
                "non_https_url_count": len(guide_summary["non_https_urls"]),
                "non_https_url_samples": guide_summary["non_https_urls"][:5],
            },
        )

    if guide_summary["possibly_expiring_urls"]:
        logger.warning(
            "Guide contains possibly expiring URLs: stage=%s count=%d samples=%s",
            stage,
            len(guide_summary["possibly_expiring_urls"]),
            guide_summary["possibly_expiring_urls"][:5],
            extra={
                "plan_id": plan_id,
                "stage": stage,
                "possibly_expiring_url_count": len(guide_summary["possibly_expiring_urls"]),
                "possibly_expiring_url_samples": guide_summary["possibly_expiring_urls"][:5],
            },
        )


def _build_timeline(items: list, allowed_spot_names: set[str]) -> list[HistoricalEvent]:
    """年表データを値オブジェクトに変換する"""
    timeline: list[HistoricalEvent] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"timeline[{index}] must be a dict.")
        year = _require_int(item.get("year"), f"timeline[{index}].year")
        event = _require_str(item.get("event"), f"timeline[{index}].event")
        significance = _require_str(item.get("significance"), f"timeline[{index}].significance")
        related_spots = _require_list(item.get("relatedSpots"), f"timeline[{index}].relatedSpots")
        related_spot_names = [
            _require_str(spot, f"timeline[{index}].relatedSpots") for spot in related_spots
        ]
        related_spot_set = set(related_spot_names)
        if not related_spot_set.issubset(allowed_spot_names):
            missing = sorted(related_spot_set - allowed_spot_names)
            raise ValueError(
                f"timeline[{index}].relatedSpots contains unknown spot names: {missing}"
            )
        timeline.append(
            HistoricalEvent(
                year=year,
                event=event,
                significance=significance,
                related_spots=tuple(related_spot_names),
            )
        )
    return timeline


def _extract_unknown_related_spot_names(error: ValueError) -> list[str]:
    """relatedSpots不整合エラーから未知スポット名を抽出する。"""
    message = str(error)
    if "relatedSpots contains unknown spot names:" not in message:
        return []
    match = re.search(r"relatedSpots contains unknown spot names: (\[.*\])", message)
    if not match:
        return []
    try:
        parsed = ast.literal_eval(match.group(1))
    except (ValueError, SyntaxError):
        return []
    if not isinstance(parsed, list):
        return []
    return [name for name in parsed if isinstance(name, str) and name.strip()]


def _build_spot_details(items: list, plan_spot_names: set[str]) -> list[SpotDetail]:
    """スポット詳細データを値オブジェクトに変換する"""
    spot_details: list[SpotDetail] = []
    seen_spot_names: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"spotDetails[{index}] must be a dict.")
        spot_name = _require_str(item.get("spotName"), f"spotDetails[{index}].spotName")
        if spot_name in seen_spot_names:
            raise ValueError(f"spotDetails contains duplicate spotName: {spot_name}")
        seen_spot_names.add(spot_name)
        historical_background = _require_str(
            item.get("historicalBackground"),
            f"spotDetails[{index}].historicalBackground",
        )
        highlights = _require_list(item.get("highlights"), f"spotDetails[{index}].highlights")
        highlight_texts = [
            _require_str(value, f"spotDetails[{index}].highlights") for value in highlights
        ]
        recommended_visit_time = _require_str(
            item.get("recommendedVisitTime"),
            f"spotDetails[{index}].recommendedVisitTime",
        )
        historical_significance = _require_str(
            item.get("historicalSignificance"),
            f"spotDetails[{index}].historicalSignificance",
        )
        spot_details.append(
            SpotDetail(
                spot_name=spot_name,
                historical_background=historical_background,
                highlights=tuple(highlight_texts),
                recommended_visit_time=recommended_visit_time,
                historical_significance=historical_significance,
            )
        )
    detail_spot_names = {detail.spot_name for detail in spot_details}
    missing = sorted(plan_spot_names - detail_spot_names)
    if missing:
        raise ValueError(f"spotDetails is missing travel plan spots: {missing}")
    return spot_details


def _build_checkpoints(items: list, allowed_spot_names: set[str]) -> list[Checkpoint]:
    """チェックポイントデータを値オブジェクトに変換する"""
    checkpoints: list[Checkpoint] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"checkpoints[{index}] must be a dict.")
        spot_name = _require_str(item.get("spotName"), f"checkpoints[{index}].spotName")
        if spot_name not in allowed_spot_names:
            raise ValueError(f"checkpoints[{index}].spotName is not in spotDetails: {spot_name}")
        checkpoint_list = _require_list(
            item.get("checkpoints"), f"checkpoints[{index}].checkpoints"
        )
        checkpoint_texts = [
            _require_str(value, f"checkpoints[{index}].checkpoints") for value in checkpoint_list
        ]
        historical_context = _require_str(
            item.get("historicalContext"), f"checkpoints[{index}].historicalContext"
        )
        checkpoints.append(
            Checkpoint(
                spot_name=spot_name,
                checkpoints=tuple(checkpoint_texts),
                historical_context=historical_context,
            )
        )
    return checkpoints


class GenerateTravelGuideUseCase:
    """旅行ガイド生成ユースケース

    旅行計画を取得し、外部AI/検索サービスを用いて旅行ガイドを生成する。
    """

    def __init__(
        self,
        plan_repository: ITravelPlanRepository,
        guide_repository: ITravelGuideRepository,
        ai_service: IAIService,
        job_repository: ISpotImageJobRepository,
        task_dispatcher: ISpotImageTaskDispatcher | None = None,
        composer: TravelGuideComposer | None = None,
    ) -> None:
        """ユースケースを初期化する

        Args:
            plan_repository: TravelPlanリポジトリ
            guide_repository: TravelGuideリポジトリ
            ai_service: AIサービス
            job_repository: スポット画像生成ジョブリポジトリ
            task_dispatcher: スポット画像タスクディスパッチャ
            composer: TravelGuideComposer（省略時はデフォルトを使用）
        """
        self._plan_repository = plan_repository
        self._guide_repository = guide_repository
        self._ai_service = ai_service
        self._job_repository = job_repository
        self._task_dispatcher = task_dispatcher
        self._composer = composer or TravelGuideComposer()

    async def execute(
        self,
        plan_id: str,
        *,
        commit: bool = True,
        task_target_url: str | None = None,
    ) -> TravelGuideDTO:
        """旅行ガイドを生成する

        Args:
            plan_id: 旅行計画ID
            commit: Trueの場合はトランザクションをコミットする
            task_target_url: Cloud Tasks実行先URL（cloud_tasksモード時）

        Returns:
            TravelGuideDTO: 生成された旅行ガイド

        Raises:
            TravelPlanNotFoundError: 旅行計画が見つからない場合
            ValueError: 入力や生成結果が不正な場合

        """
        execute_started_at = time.perf_counter()
        phase_timings_sec: dict[str, float] = {
            "load_plan": 0.0,
            "set_processing_status": 0.0,
            "fact_extraction_total": 0.0,
            "guide_structured_generation": 0.0,
            "guide_payload_validation": 0.0,
            "guide_persistence": 0.0,
            "spot_image_job_registration": 0.0,
            "spot_image_task_enqueue": 0.0,
            "set_succeeded_status": 0.0,
            "set_failed_status": 0.0,
        }
        generation_outcome = "started"

        logger.debug("GenerateTravelGuideUseCase started", extra={"plan_id": plan_id})
        validate_required_str(plan_id, "plan_id")

        load_plan_start = time.perf_counter()
        travel_plan = self._plan_repository.find_by_id(plan_id)
        phase_timings_sec["load_plan"] = time.perf_counter() - load_plan_start
        if travel_plan is None:
            raise TravelPlanNotFoundError(plan_id)

        if not travel_plan.id:
            raise ValueError("plan_id is required and must not be empty.")

        plan_spot_names = [spot.name for spot in travel_plan.spots]
        logger.debug(
            "Travel plan validated for guide generation",
            extra={
                "plan_id": plan_id,
                "destination": travel_plan.destination,
                "spot_count": len(plan_spot_names),
            },
        )
        duplicate_spots = {
            spot_name for spot_name in plan_spot_names if plan_spot_names.count(spot_name) > 1
        }
        if duplicate_spots:
            raise ValueError(f"duplicate spot names are not allowed: {sorted(duplicate_spots)}")

        set_processing_start = time.perf_counter()
        travel_plan.update_generation_statuses(guide_status=GenerationStatus.PROCESSING)
        self._plan_repository.save(travel_plan, commit=commit)
        phase_timings_sec["set_processing_status"] = time.perf_counter() - set_processing_start
        logger.debug(
            "Guide status set to processing in use case",
            extra={"plan_id": plan_id},
        )

        try:
            with self._plan_repository.begin_nested():
                # Step A: 事実抽出（出典候補付き）
                logger.debug(
                    "Starting fact extraction",
                    extra={"plan_id": plan_id},
                )
                fact_extraction_prompt_base = _build_fact_extraction_prompt(travel_plan)
                fact_extraction_system_instruction = render_template(
                    _FACT_EXTRACTION_SYSTEM_INSTRUCTION_TEMPLATE
                )
                fact_extraction_prompt = fact_extraction_prompt_base
                extracted_facts = ""
                coverage_summary: dict[str, Any] | None = None

                fact_extraction_total_start = time.perf_counter()
                for round_index in range(_MAX_FACT_EXTRACTION_ROUNDS):
                    round_start = time.perf_counter()
                    extracted_facts = await self._ai_service.generate_with_search(
                        prompt=fact_extraction_prompt,
                        system_instruction=fact_extraction_system_instruction,
                    )
                    round_elapsed_sec = time.perf_counter() - round_start

                    if not extracted_facts or not extracted_facts.strip():
                        raise ValueError("extracted_facts must be a non-empty string.")

                    coverage_summary = _assess_fact_extraction_coverage(
                        extracted_facts=extracted_facts,
                        spot_names=plan_spot_names,
                    )
                    logger.info(
                        "Fact extraction round completed: round=%d/%d elapsed_sec=%.3f raw_url_count=%d validated_url_count=%d min_required_urls=%d missing_spot_sources=%d sufficient=%s",
                        round_index + 1,
                        _MAX_FACT_EXTRACTION_ROUNDS,
                        round_elapsed_sec,
                        coverage_summary["raw_url_count"],
                        coverage_summary["validated_url_count"],
                        coverage_summary["min_required_urls"],
                        len(coverage_summary["missing_spot_sources"]),
                        coverage_summary["sufficient"],
                        extra={
                            "plan_id": plan_id,
                            "round": round_index + 1,
                            "max_rounds": _MAX_FACT_EXTRACTION_ROUNDS,
                            "round_elapsed_sec": round_elapsed_sec,
                            "raw_url_count": coverage_summary["raw_url_count"],
                            "validated_url_count": coverage_summary["validated_url_count"],
                            "min_required_urls": coverage_summary["min_required_urls"],
                            "missing_spot_sources": coverage_summary["missing_spot_sources"],
                            "sufficient": coverage_summary["sufficient"],
                        },
                    )
                    _log_fact_extraction_link_diagnostics(
                        plan_id=plan_id,
                        extracted_facts=extracted_facts,
                    )

                    if coverage_summary["sufficient"]:
                        break

                    if round_index >= _MAX_FACT_EXTRACTION_ROUNDS - 1:
                        logger.warning(
                            "Fact extraction reached max rounds with insufficient citations.",
                            extra={
                                "plan_id": plan_id,
                                "max_rounds": _MAX_FACT_EXTRACTION_ROUNDS,
                                "raw_url_count": coverage_summary["raw_url_count"],
                                "validated_url_count": coverage_summary["validated_url_count"],
                                "min_required_urls": coverage_summary["min_required_urls"],
                                "missing_spot_sources": coverage_summary["missing_spot_sources"],
                            },
                        )
                        break

                    fact_extraction_prompt = _build_fact_extraction_retry_prompt(
                        base_prompt=fact_extraction_prompt_base,
                        previous_extracted_facts=extracted_facts,
                        missing_spot_sources=coverage_summary["missing_spot_sources"],
                        min_required_urls=coverage_summary["min_required_urls"],
                        feedback_round=round_index + 1,
                    )
                    await asyncio.sleep(0.3 * (round_index + 1))

                phase_timings_sec["fact_extraction_total"] = (
                    time.perf_counter() - fact_extraction_total_start
                )
                logger.debug(
                    "Fact extraction completed",
                    extra={"plan_id": plan_id, "facts_length": len(extracted_facts)},
                )

                # 初回生成（Step Aの出力を使用）
                logger.debug(
                    "Starting travel guide generation",
                    extra={"plan_id": plan_id},
                )
                guide_structured_generation_start = time.perf_counter()
                structured = {}
                guide_retry_feedback: str | None = None
                for guide_generation_attempt in range(
                    _MAX_GUIDE_REGENERATIONS_ON_UNKNOWN_RELATED_SPOTS + 1
                ):
                    structured = await self._generate_guide_data(
                        travel_plan,
                        extracted_facts,
                        related_spots_retry_feedback=guide_retry_feedback,
                    )
                    logger.debug(
                        "Travel guide generation completed",
                        extra={
                            "plan_id": plan_id,
                            "attempt": guide_generation_attempt + 1,
                            "structured_keys": sorted(structured.keys()),
                        },
                    )
                    _log_link_quality_diagnostics(
                        plan_id=plan_id,
                        stage="initial_generation"
                        if guide_generation_attempt == 0
                        else f"retry_{guide_generation_attempt}",
                        extracted_facts=extracted_facts,
                        guide_data=structured,
                    )
                    # レスポンスバリデーション
                    payload_validation_start = time.perf_counter()
                    try:
                        TravelGuideResponseSchema.model_validate(structured)
                    except ValidationError as e:
                        raise ValueError(f"Invalid AI response structure: {e}") from e

                    overview = _require_str(structured.get("overview"), "overview")
                    _require_min_length(overview, "overview", 100)
                    timeline_items = _require_list(structured.get("timeline"), "timeline")
                    spot_detail_items = _require_list(structured.get("spotDetails"), "spotDetails")
                    checkpoint_items = _require_list(structured.get("checkpoints"), "checkpoints")

                    plan_spot_name_set = set(plan_spot_names)
                    spot_details = _build_spot_details(spot_detail_items, plan_spot_name_set)
                    spot_detail_name_set = {detail.spot_name for detail in spot_details}
                    checkpoints = _build_checkpoints(checkpoint_items, spot_detail_name_set)
                    allowed_related_spots_for_timeline = spot_detail_name_set | {
                        travel_plan.destination
                    }
                    try:
                        timeline = _build_timeline(
                            timeline_items, allowed_related_spots_for_timeline
                        )
                    except ValueError as e:
                        unknown_spot_names = _extract_unknown_related_spot_names(e)
                        can_retry = (
                            bool(unknown_spot_names)
                            and guide_generation_attempt
                            < _MAX_GUIDE_REGENERATIONS_ON_UNKNOWN_RELATED_SPOTS
                        )
                        if not can_retry:
                            raise
                        allowed_names_text = ", ".join(sorted(allowed_related_spots_for_timeline))
                        unknown_names_text = ", ".join(unknown_spot_names)
                        guide_retry_feedback = (
                            "前回の出力では timeline.relatedSpots に未許可スポット名が含まれていました。\n"
                            f"未許可スポット名: {unknown_names_text}\n"
                            "次のルールを厳守して再生成してください。\n"
                            f"- relatedSpots は次の名称のみ使用可: {allowed_names_text}\n"
                            "- spotDetails に存在しない名称を relatedSpots に入れないこと。\n"
                            "- 追加スポットを使う場合は、spotDetails と checkpoints に同名を必ず追加すること。"
                        )
                        logger.warning(
                            "Retrying guide structured generation due to unknown related spots.",
                            extra={
                                "plan_id": plan_id,
                                "attempt": guide_generation_attempt + 1,
                                "unknown_related_spot_names": unknown_spot_names,
                                "allowed_related_spot_names": sorted(
                                    allowed_related_spots_for_timeline
                                ),
                            },
                        )
                        continue

                    # 新規スポット検出と追加
                    new_spot_names = _detect_new_spots(spot_details, travel_plan.spots)
                    if new_spot_names:
                        new_spots = _create_tourist_spots(new_spot_names)
                        updated_spots = travel_plan.spots + new_spots
                        travel_plan.update_plan(spots=updated_spots)
                        # commit=Falseで保存（最終的なステータス更新時に一括コミット）
                        self._plan_repository.save(travel_plan, commit=False)
                        logger.debug(
                            "New spots detected and added",
                            extra={"plan_id": plan_id, "new_spot_count": len(new_spot_names)},
                        )
                    break

                phase_timings_sec["guide_structured_generation"] = (
                    time.perf_counter() - guide_structured_generation_start
                )
                phase_timings_sec["guide_payload_validation"] = (
                    time.perf_counter() - payload_validation_start
                )

                allowed_related_spots_for_compose = {travel_plan.destination}
                guide_persistence_start = time.perf_counter()
                generated_guide = self._composer.compose(
                    plan_id=travel_plan.id,
                    overview=overview,
                    timeline=timeline,
                    spot_details=spot_details,
                    checkpoints=checkpoints,
                    allowed_related_spots=allowed_related_spots_for_compose,
                )

                existing = self._guide_repository.find_by_plan_id(travel_plan.id)
                if existing is None:
                    saved_guide = self._guide_repository.save(generated_guide, commit=False)
                else:
                    existing.update_guide(
                        overview=generated_guide.overview,
                        timeline=generated_guide.timeline,
                        spot_details=generated_guide.spot_details,
                        checkpoints=generated_guide.checkpoints,
                    )
                    saved_guide = self._guide_repository.save(existing, commit=False)
                register_jobs_start = time.perf_counter()
                created_jobs = self._register_spot_image_jobs(
                    plan_id=plan_id,
                    spot_details=saved_guide.spot_details,
                    commit=False,
                )
                phase_timings_sec["spot_image_job_registration"] = (
                    time.perf_counter() - register_jobs_start
                )
                enqueue_tasks_start = time.perf_counter()
                self._enqueue_spot_image_tasks(
                    plan_id=plan_id,
                    spot_details=saved_guide.spot_details,
                    task_target_url=task_target_url,
                )
                phase_timings_sec["spot_image_task_enqueue"] = (
                    time.perf_counter() - enqueue_tasks_start
                )
                phase_timings_sec["guide_persistence"] = (
                    time.perf_counter() - guide_persistence_start
                )
                logger.info(
                    "Spot image jobs registered",
                    extra={"plan_id": plan_id, "created_jobs": created_jobs},
                )

            set_succeeded_start = time.perf_counter()
            travel_plan.update_generation_statuses(guide_status=GenerationStatus.SUCCEEDED)
            self._plan_repository.save(travel_plan, commit=commit)
            phase_timings_sec["set_succeeded_status"] = time.perf_counter() - set_succeeded_start
            generation_outcome = "succeeded"
            logger.debug(
                "Guide status set to succeeded in use case",
                extra={"plan_id": plan_id},
            )
        except Exception:
            generation_outcome = "failed"
            logger.exception(
                "Travel guide generation failed in use case",
                extra={"plan_id": plan_id},
            )
            failed_status_start = time.perf_counter()
            failed_plan = self._plan_repository.find_by_id(travel_plan.id) or travel_plan
            failed_plan.update_generation_statuses(guide_status=GenerationStatus.FAILED)
            self._plan_repository.save(failed_plan, commit=commit)
            phase_timings_sec["set_failed_status"] = time.perf_counter() - failed_status_start
            raise
        finally:
            total_elapsed_sec = time.perf_counter() - execute_started_at
            logger.info(
                "Travel guide generation timing summary: outcome=%s total_sec=%.3f phases=%s",
                generation_outcome,
                total_elapsed_sec,
                phase_timings_sec,
                extra={
                    "plan_id": plan_id,
                    "outcome": generation_outcome,
                    "total_elapsed_sec": total_elapsed_sec,
                    "phase_timings_sec": phase_timings_sec,
                },
            )

        return TravelGuideDTO.from_entity(saved_guide)

    def _register_spot_image_jobs(
        self,
        plan_id: str,
        spot_details: list[SpotDetail],
        *,
        commit: bool,
    ) -> int:
        """スポット画像生成ジョブを登録する"""
        target_spots = [
            detail.spot_name
            for detail in spot_details
            if not (detail.image_status == "succeeded" and detail.image_url)
        ]
        if not target_spots:
            return 0
        return self._job_repository.create_jobs(
            plan_id=plan_id,
            spot_names=target_spots,
            max_attempts=3,
            commit=commit,
        )

    def _enqueue_spot_image_tasks(
        self,
        plan_id: str,
        spot_details: list[SpotDetail],
        *,
        task_target_url: str | None = None,
    ) -> None:
        settings = get_settings()
        if settings.image_execution_mode == "local_worker":
            return

        if settings.image_execution_mode != "cloud_tasks":
            raise ValueError(f"Unsupported IMAGE_EXECUTION_MODE: {settings.image_execution_mode}")
        if self._task_dispatcher is None:
            raise ValueError("task_dispatcher is required when IMAGE_EXECUTION_MODE=cloud_tasks.")

        target_spots = [
            detail.spot_name
            for detail in spot_details
            if not (detail.image_status == "succeeded" and detail.image_url)
        ]
        for spot_name in target_spots:
            digest = hashlib.sha1(
                f"{plan_id}:{_normalize_spot_name(spot_name)}".encode()
            ).hexdigest()
            task_idempotency_key = f"spot-image-{digest}"
            self._task_dispatcher.enqueue_spot_image_task(
                plan_id=plan_id,
                spot_name=spot_name,
                task_idempotency_key=task_idempotency_key,
                target_url=task_target_url,
            )

    async def _generate_guide_data(
        self,
        travel_plan: TravelPlan,
        extracted_facts: str,
        *,
        related_spots_retry_feedback: str | None = None,
    ) -> dict[str, Any]:
        """旅行ガイドデータを生成する

        Args:
            travel_plan: 旅行計画
            extracted_facts: 事実抽出結果

        Returns:
            生成された構造化データ
        """
        logger.debug(
            "Generating guide data with AI",
            extra={
                "destination": travel_plan.destination,
                "spot_count": len(travel_plan.spots),
                "facts_length": len(extracted_facts),
            },
        )
        guide_prompt = _build_travel_guide_prompt(
            travel_plan,
            extracted_facts,
            related_spots_retry_feedback=related_spots_retry_feedback,
        )
        structured = await self._ai_service.generate_structured_data(
            prompt=guide_prompt,
            response_schema=TravelGuideResponseSchema,
            system_instruction=render_template(_TRAVEL_GUIDE_SYSTEM_INSTRUCTION_TEMPLATE),
        )
        if not isinstance(structured, dict):
            raise ValueError("structured response must be a dict.")
        return structured


def _build_spots_text(travel_plan: TravelPlan) -> str:
    """スポットテキストを生成する

    スポットが指定されている場合はリスト形式、未指定の場合は
    目的地に基づいておすすめスポットを提案するよう指示するテキストを返す。
    """
    if travel_plan.spots:
        return "\n".join([f"- {spot.name}" for spot in travel_plan.spots])
    return load_template(_NO_SPOTS_TEXT_TEMPLATE).strip()


def _build_fact_extraction_prompt(travel_plan: TravelPlan) -> str:
    """事実抽出用のプロンプトを生成する（Step A）"""
    return render_template(
        _FACT_EXTRACTION_PROMPT_TEMPLATE,
        destination=travel_plan.destination,
        spots_text=_build_spots_text(travel_plan),
    )


def _build_spot_source_constraints_text(travel_plan: TravelPlan, extracted_facts: str) -> str:
    """StepB向けにスポット別の利用可能URL制約を構築する。"""
    spot_names = [spot.name for spot in travel_plan.spots]
    validated_urls_by_spot: dict[str, list[str]] = {spot_name: [] for spot_name in spot_names}
    seen_urls_by_spot: dict[str, set[str]] = {spot_name: set() for spot_name in spot_names}
    in_spot_section = False
    current_spot: str | None = None

    for raw_line in extracted_facts.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if re.match(r"^##\s+", line):
            in_spot_section = "スポット別の事実" in line
            if not in_spot_section:
                current_spot = None

        if in_spot_section and re.match(r"^###\s+", line):
            heading_text = line[3:].strip()
            bracket_match = re.match(r"^\[(.+?)\]$", heading_text)
            if bracket_match:
                heading_text = bracket_match.group(1).strip()
            current_spot = heading_text if heading_text in validated_urls_by_spot else None
            continue

        if not _VALIDATED_SOURCE_MARKER_REGEX.search(line):
            continue

        urls = _extract_urls(line)
        if not urls:
            continue

        target_spots: list[str] = []
        if current_spot:
            target_spots.append(current_spot)
        for spot_name in spot_names:
            if spot_name in line and spot_name not in target_spots:
                target_spots.append(spot_name)

        if not target_spots:
            continue

        for spot_name in target_spots:
            for url in urls:
                if url in seen_urls_by_spot[spot_name]:
                    continue
                seen_urls_by_spot[spot_name].add(url)
                validated_urls_by_spot[spot_name].append(url)

    lines = [
        "以下はスポット別の利用可能URL（StepAで [検証: valid] 判定済み）です。",
        "各スポットの本文では、そのスポットに割り当てられたURLのみを出典として使用してください。",
        "割り当てがないスポットは、出典不足として扱い、無関係なURLを流用しないでください。",
        "",
    ]

    for spot_name in spot_names:
        lines.append(f"- {spot_name}:")
        urls = validated_urls_by_spot[spot_name]
        if not urls:
            lines.append("  - URLなし（出典不足）")
            continue
        for url in urls:
            lines.append(f"  - {url}")

    return "\n".join(lines)


def _build_allowed_related_spots_text(travel_plan: TravelPlan) -> str:
    """StepB向けにrelatedSpotsで使用可能な名称を列挙する。"""
    allowed_names = sorted({travel_plan.destination, *[spot.name for spot in travel_plan.spots]})
    lines = [
        "relatedSpotsで使用可能な名称一覧です。",
        "この一覧にない名称は relatedSpots に入れてはいけません。",
    ]
    for name in allowed_names:
        lines.append(f"- {name}")
    return "\n".join(lines)


def _build_travel_guide_prompt(
    travel_plan: TravelPlan,
    extracted_facts: str,
    *,
    related_spots_retry_feedback: str | None = None,
) -> str:
    """旅行ガイド生成用のプロンプトを生成する（Step B）"""
    return render_template(
        _TRAVEL_GUIDE_PROMPT_TEMPLATE,
        destination=travel_plan.destination,
        spots_text=_build_spots_text(travel_plan),
        extracted_facts=extracted_facts,
        spot_source_constraints=_build_spot_source_constraints_text(travel_plan, extracted_facts),
        allowed_related_spots=_build_allowed_related_spots_text(travel_plan),
        related_spots_retry_feedback=related_spots_retry_feedback or "なし",
    )
