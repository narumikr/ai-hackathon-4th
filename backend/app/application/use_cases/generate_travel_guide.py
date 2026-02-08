"""旅行ガイド生成ユースケース"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
import ssl
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

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
from app.infrastructure.ai.schemas.evaluation import TravelGuideEvaluationSchema
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
_EVALUATION_PROMPT_TEMPLATE = "travel_guide_evaluation_prompt.txt"
_EVALUATION_SYSTEM_INSTRUCTION_TEMPLATE = "travel_guide_evaluation_system_instruction.txt"
_NO_SPOTS_TEXT_TEMPLATE = "travel_guide_no_spots_text.txt"

logger = logging.getLogger(__name__)
_URL_REGEX = re.compile(r"https?://[^\s)\]}>\"']+")
_MARKDOWN_LINK_REGEX_TEMPLATE = r"\[(?P<label>[^\]]+)\]\(\s*{url}\s*\)"
_URL_CHECK_TIMEOUT_SECONDS = 10
_CERT_CHECK_TIMEOUT_SECONDS = 5

UrlAccessChecker = Callable[[str], Awaitable["URLAccessCheckResult"]]


@dataclass(frozen=True)
class URLAccessCheckResult:
    """URL到達性チェック結果。"""

    url: str
    reachable: bool
    status_code: int | None = None
    content_type: str | None = None
    final_url: str | None = None
    reason: str | None = None


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


def _sanitize_text_by_urls(text: str, rejected_urls: set[str]) -> str:
    """テキストから無効URLを除去する。"""
    sanitized = text
    for url in sorted(rejected_urls, key=len, reverse=True):
        escaped_url = re.escape(url)
        markdown_pattern = _MARKDOWN_LINK_REGEX_TEMPLATE.format(url=escaped_url)
        sanitized = re.sub(markdown_pattern, r"\g<label>", sanitized)
        sanitized = sanitized.replace(f"<{url}>", "")
        sanitized = sanitized.replace(url, "")

    sanitized = re.sub(r"\(\s*\)", "", sanitized)
    sanitized = re.sub(r"\s{2,}", " ", sanitized)
    sanitized = re.sub(r"\s+([、。,.!?])", r"\1", sanitized)
    return sanitized.strip()


def _sanitize_guide_payload_urls(
    guide_data: dict[str, Any], rejected_urls: set[str]
) -> dict[str, Any]:
    """旅行ガイド構造化データから無効URLを除去する。"""
    if not rejected_urls:
        return guide_data

    sanitized = json.loads(json.dumps(guide_data, ensure_ascii=False))

    if isinstance(sanitized.get("overview"), str):
        sanitized["overview"] = _sanitize_text_by_urls(sanitized["overview"], rejected_urls)

    timeline = sanitized.get("timeline")
    if isinstance(timeline, list):
        for item in timeline:
            if not isinstance(item, dict):
                continue
            for key in ("event", "significance"):
                if isinstance(item.get(key), str):
                    item[key] = _sanitize_text_by_urls(item[key], rejected_urls)

    spot_details = sanitized.get("spotDetails")
    if isinstance(spot_details, list):
        for item in spot_details:
            if not isinstance(item, dict):
                continue
            for key in ("historicalBackground", "historicalSignificance", "recommendedVisitTime"):
                if isinstance(item.get(key), str):
                    item[key] = _sanitize_text_by_urls(item[key], rejected_urls)
            highlights = item.get("highlights")
            if isinstance(highlights, list):
                item["highlights"] = [
                    _sanitize_text_by_urls(highlight, rejected_urls)
                    if isinstance(highlight, str)
                    else highlight
                    for highlight in highlights
                ]

    checkpoints = sanitized.get("checkpoints")
    if isinstance(checkpoints, list):
        for item in checkpoints:
            if not isinstance(item, dict):
                continue
            if isinstance(item.get("historicalContext"), str):
                item["historicalContext"] = _sanitize_text_by_urls(
                    item["historicalContext"], rejected_urls
                )
            checkpoint_items = item.get("checkpoints")
            if isinstance(checkpoint_items, list):
                item["checkpoints"] = [
                    _sanitize_text_by_urls(checkpoint, rejected_urls)
                    if isinstance(checkpoint, str)
                    else checkpoint
                    for checkpoint in checkpoint_items
                ]

    return sanitized


def _extract_html_title(html: str) -> str:
    """HTMLからtitleを抽出する。"""
    matched = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if not matched:
        return ""
    title = re.sub(r"\s+", " ", matched.group(1))
    return title.strip()


def _extract_og_url(html: str) -> str:
    """HTMLからog:urlを抽出する。"""
    matched = re.search(
        r'<meta[^>]+property=["\']og:url["\'][^>]+content=["\']([^"\']+)["\']',
        html,
        flags=re.IGNORECASE,
    )
    if not matched:
        return ""
    return matched.group(1).strip()


def _is_soft_404_html(html: str, final_url: str | None) -> tuple[bool, str | None]:
    """HTML本文からソフト404を判定する。"""
    lowered = html.lower()
    title = _extract_html_title(html)
    og_url = _extract_og_url(html)
    title_lower = title.lower()
    og_url_lower = og_url.lower()
    final_url_lower = (final_url or "").lower()

    if any(token in final_url_lower for token in ("/404", "404.html", "notfound", "not-found")):
        return True, "soft_404_final_url"

    if og_url and any(token in og_url_lower for token in ("/404", "404.html", "notfound")):
        return True, "soft_404_og_url"

    soft_404_tokens = (
        "404",
        "not found",
        "お探しのページ",
        "見つかりません",
        "ページが存在しません",
        "統合しました",
        "移転しました",
    )
    if any(token in title_lower for token in soft_404_tokens):
        return True, "soft_404_title"
    if any(token in lowered for token in soft_404_tokens):
        return True, "soft_404_body"

    return False, None


def _check_url_accessibility_sync(url: str) -> URLAccessCheckResult:
    """URL到達性を同期的に確認する。"""
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https":
        return URLAccessCheckResult(
            url=url,
            reachable=False,
            reason="non_https_scheme",
        )

    try:
        request = Request(
            url,
            headers={"User-Agent": "HistoricalTravelAgent/1.0 (URL validation)"},
            method="GET",
        )
        with urlopen(request, timeout=_URL_CHECK_TIMEOUT_SECONDS) as response:  # noqa: S310
            status_code = response.getcode()
            content_type = response.headers.get("Content-Type")
            final_url = response.geturl()
            body_bytes = response.read(65536)
            body_text = body_bytes.decode("utf-8", errors="ignore")

            if status_code < 200 or status_code >= 300:
                return URLAccessCheckResult(
                    url=url,
                    reachable=False,
                    status_code=status_code,
                    content_type=content_type,
                    final_url=final_url,
                    reason="http_status_error",
                )

            if parsed.path.lower().endswith(".pdf") and (
                content_type is None or "application/pdf" not in content_type.lower()
            ):
                return URLAccessCheckResult(
                    url=url,
                    reachable=False,
                    status_code=status_code,
                    content_type=content_type,
                    final_url=final_url,
                    reason="unexpected_content_type_for_pdf",
                )

            if content_type and "text/html" in content_type.lower():
                is_soft_404, soft_404_reason = _is_soft_404_html(body_text, final_url)
                if is_soft_404:
                    return URLAccessCheckResult(
                        url=url,
                        reachable=False,
                        status_code=status_code,
                        content_type=content_type,
                        final_url=final_url,
                        reason=soft_404_reason or "soft_404_html",
                    )

            return URLAccessCheckResult(
                url=url,
                reachable=True,
                status_code=status_code,
                content_type=content_type,
                final_url=final_url,
            )
    except HTTPError as exc:
        return URLAccessCheckResult(
            url=url,
            reachable=False,
            status_code=exc.code,
            reason="http_error",
        )
    except (URLError, TimeoutError, ValueError) as exc:
        return URLAccessCheckResult(
            url=url,
            reachable=False,
            reason=f"network_error:{type(exc).__name__}",
        )


async def _check_url_accessibility(url: str) -> URLAccessCheckResult:
    """URL到達性を非同期で確認する。"""
    return await asyncio.to_thread(_check_url_accessibility_sync, url)


def _is_certificate_error_reason(reason: object) -> bool:
    """証明書エラーの例外理由か判定する。"""
    reason_text = str(reason).lower()
    tokens = (
        "certificate has expired",
        "certificate verify failed",
        "certificate expired",
        "self signed certificate",
        "hostname mismatch",
    )
    return any(token in reason_text for token in tokens)


def _is_certificate_error_exception(exc: BaseException) -> bool:
    """証明書エラー例外か判定する。"""
    if isinstance(exc, ssl.SSLError):
        return True
    if isinstance(exc, URLError):
        return _is_certificate_error_reason(exc.reason)
    return _is_certificate_error_reason(exc)


def _check_url_certificate_valid_sync(url: str) -> tuple[str, bool]:
    """URLのTLS証明書が有効か軽量確認する。"""
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https":
        return url, True

    try:
        request = Request(
            url,
            headers={"User-Agent": "HistoricalTravelAgent/1.0 (cert check)"},
            method="HEAD",
        )
        with urlopen(request, timeout=_CERT_CHECK_TIMEOUT_SECONDS):  # noqa: S310
            return url, True
    except HTTPError:
        # 証明書が有効ならHTTPエラーは受け入れる（存在判定はここでしない）
        return url, True
    except (URLError, ssl.SSLError, ValueError) as exc:
        if _is_certificate_error_exception(exc):
            return url, False
        return url, True


async def _check_url_certificate_valid(url: str) -> tuple[str, bool]:
    """URLのTLS証明書を非同期で確認する。"""
    return await asyncio.to_thread(_check_url_certificate_valid_sync, url)


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


def _log_fact_extraction_link_diagnostics(*, plan_id: str, extracted_facts: str) -> None:
    """Step Aの抽出URL品質をログ出力する。"""
    extracted_urls = _extract_urls(extracted_facts)
    summary = _summarize_url_quality(extracted_urls)

    logger.info(
        "Fact extraction link diagnostics: extracted_urls=%d domains=%d malformed=%d non_https=%d expiring=%d grounding_redirect=%d",
        summary["url_count"],
        summary["domain_count"],
        len(summary["malformed_urls"]),
        len(summary["non_https_urls"]),
        len(summary["possibly_expiring_urls"]),
        len(summary["grounding_redirect_urls"]),
        extra={
            "plan_id": plan_id,
            "extracted_url_count": summary["url_count"],
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
        url_access_checker: UrlAccessChecker | None = None,
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
        self._url_access_checker = url_access_checker or _check_url_accessibility

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
        logger.debug("GenerateTravelGuideUseCase started", extra={"plan_id": plan_id})
        validate_required_str(plan_id, "plan_id")

        travel_plan = self._plan_repository.find_by_id(plan_id)
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

        travel_plan.update_generation_statuses(guide_status=GenerationStatus.PROCESSING)
        self._plan_repository.save(travel_plan, commit=commit)
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
                fact_extraction_prompt = _build_fact_extraction_prompt(travel_plan)
                extracted_facts = await self._ai_service.generate_with_search(
                    prompt=fact_extraction_prompt,
                    system_instruction=render_template(
                        _FACT_EXTRACTION_SYSTEM_INSTRUCTION_TEMPLATE
                    ),
                )
                if not extracted_facts or not extracted_facts.strip():
                    raise ValueError("extracted_facts must be a non-empty string.")
                logger.debug(
                    "Fact extraction completed",
                    extra={"plan_id": plan_id, "facts_length": len(extracted_facts)},
                )
                _log_fact_extraction_link_diagnostics(
                    plan_id=plan_id,
                    extracted_facts=extracted_facts,
                )

                # 初回生成（Step Aの出力を使用）
                logger.debug(
                    "Starting travel guide generation",
                    extra={"plan_id": plan_id},
                )
                structured = await self._generate_guide_data(travel_plan, extracted_facts)
                logger.debug(
                    "Travel guide generation completed",
                    extra={
                        "plan_id": plan_id,
                        "structured_keys": sorted(structured.keys()),
                    },
                )
                _log_link_quality_diagnostics(
                    plan_id=plan_id,
                    stage="initial_generation",
                    extracted_facts=extracted_facts,
                    guide_data=structured,
                )
                # 評価
                logger.debug(
                    "Starting travel guide evaluation",
                    extra={"plan_id": plan_id},
                )
                evaluation = await self._evaluate_guide_data(structured, plan_spot_names)
                logger.debug(
                    "Travel guide evaluation completed",
                    extra={"plan_id": plan_id},
                )

                # 評価結果を解析
                is_valid = self._check_evaluation_result(evaluation)

                # 不合格の場合は1回だけ再生成
                if not is_valid:
                    failure_reasons = self._get_failure_reasons(evaluation)
                    logger.warning(
                        "Travel guide evaluation failed. Reasons: %s. Retrying once...",
                        "; ".join(failure_reasons),
                    )
                    logger.debug(
                        "Retrying travel guide generation after evaluation failure",
                        extra={"plan_id": plan_id},
                    )
                    structured = await self._generate_guide_data(travel_plan, extracted_facts)
                    _log_link_quality_diagnostics(
                        plan_id=plan_id,
                        stage="retry_generation",
                        extracted_facts=extracted_facts,
                        guide_data=structured,
                    )
                    # 再評価（ログ出力のみ、再生成は行わない）
                    logger.debug(
                        "Re-evaluating travel guide after retry",
                        extra={"plan_id": plan_id},
                    )
                    re_evaluation = await self._evaluate_guide_data(structured, plan_spot_names)
                    re_is_valid = self._check_evaluation_result(re_evaluation)
                    if not re_is_valid:
                        re_failure_reasons = self._get_failure_reasons(re_evaluation)
                        logger.warning(
                            "Travel guide evaluation failed after retry. Reasons: %s. Proceeding anyway.",
                            "; ".join(re_failure_reasons),
                        )
                    else:
                        logger.info("Travel guide evaluation passed after retry.")

                # レスポンスバリデーション
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

                spot_detail_name_set = {detail.spot_name for detail in spot_details}
                checkpoints = _build_checkpoints(checkpoint_items, spot_detail_name_set)
                allowed_related_spots_for_timeline = spot_detail_name_set | {
                    travel_plan.destination
                }
                timeline = _build_timeline(timeline_items, allowed_related_spots_for_timeline)

                allowed_related_spots_for_compose = {travel_plan.destination}
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
                created_jobs = self._register_spot_image_jobs(
                    plan_id=plan_id,
                    spot_details=saved_guide.spot_details,
                    commit=False,
                )
                self._enqueue_spot_image_tasks(
                    plan_id=plan_id,
                    spot_details=saved_guide.spot_details,
                    task_target_url=task_target_url,
                )
                logger.info(
                    "Spot image jobs registered",
                    extra={"plan_id": plan_id, "created_jobs": created_jobs},
                )

            travel_plan.update_generation_statuses(guide_status=GenerationStatus.SUCCEEDED)
            self._plan_repository.save(travel_plan, commit=commit)
            logger.debug(
                "Guide status set to succeeded in use case",
                extra={"plan_id": plan_id},
            )
        except Exception:
            logger.exception(
                "Travel guide generation failed in use case",
                extra={"plan_id": plan_id},
            )
            failed_plan = self._plan_repository.find_by_id(travel_plan.id) or travel_plan
            failed_plan.update_generation_statuses(guide_status=GenerationStatus.FAILED)
            self._plan_repository.save(failed_plan, commit=commit)
            raise

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

    async def _validate_fact_extraction_urls(
        self,
        *,
        plan_id: str,
        extracted_facts: str,
    ) -> tuple[str, set[str]]:
        """Step Aで抽出したURLを検証し、有効URLのみを残す。"""
        extracted_urls = _extract_urls(extracted_facts)
        if not extracted_urls:
            logger.warning(
                "Fact extraction contains no URLs.",
                extra={"plan_id": plan_id},
            )
            return extracted_facts, set()

        summary = _summarize_url_quality(extracted_urls)
        static_rejected_urls = set(
            summary["malformed_urls"]
            + summary["non_https_urls"]
            + summary["possibly_expiring_urls"]
            + summary["grounding_redirect_urls"]
        )
        access_targets = sorted(extracted_urls - static_rejected_urls)

        access_results = await asyncio.gather(
            *[self._url_access_checker(url) for url in access_targets]
        )
        unreachable_urls = {result.url for result in access_results if not result.reachable}
        validated_urls = {result.url for result in access_results if result.reachable}
        rejected_urls = static_rejected_urls | unreachable_urls

        if rejected_urls:
            logger.warning(
                "Fact extraction contains rejected URLs: total=%d rejected=%d",
                len(extracted_urls),
                len(rejected_urls),
                extra={
                    "plan_id": plan_id,
                    "fact_url_count": len(extracted_urls),
                    "fact_url_rejected_count": len(rejected_urls),
                    "fact_url_valid_count": len(validated_urls),
                    "fact_url_rejected_samples": sorted(rejected_urls)[:5],
                },
            )

        sanitized_facts = _sanitize_text_by_urls(extracted_facts, rejected_urls)
        if extracted_urls and not validated_urls:
            logger.warning(
                "No validated URLs remained after fact extraction URL validation.",
                extra={"plan_id": plan_id},
            )
        return sanitized_facts, validated_urls

    async def _sanitize_generated_guide_urls(
        self,
        *,
        plan_id: str,
        stage: str,
        extracted_facts: str,
        guide_data: dict[str, Any],
        validated_fact_urls: set[str],
    ) -> dict[str, Any]:
        """Step Bで生成したURLを検証し、無効URLを除去する。"""
        guide_urls = _collect_urls_from_guide_payload(guide_data)
        if not guide_urls:
            return guide_data

        summary = _summarize_url_quality(guide_urls)
        invalid_urls = set(
            summary["malformed_urls"]
            + summary["non_https_urls"]
            + summary["possibly_expiring_urls"]
            + summary["grounding_redirect_urls"]
        )
        if validated_fact_urls:
            invalid_urls.update(guide_urls - validated_fact_urls)

        # Step Aで検証済みURL以外がある場合は到達性チェックする。
        access_targets = sorted(guide_urls - invalid_urls - validated_fact_urls)
        if access_targets:
            access_results = await asyncio.gather(
                *[self._url_access_checker(url) for url in access_targets]
            )
            invalid_urls.update(result.url for result in access_results if not result.reachable)

        if not invalid_urls:
            return guide_data

        logger.warning(
            "Guide URLs were sanitized: stage=%s total=%d invalid=%d",
            stage,
            len(guide_urls),
            len(invalid_urls),
            extra={
                "plan_id": plan_id,
                "stage": stage,
                "guide_url_count": len(guide_urls),
                "guide_invalid_url_count": len(invalid_urls),
                "guide_invalid_url_samples": sorted(invalid_urls)[:5],
            },
        )

        sanitized = _sanitize_guide_payload_urls(guide_data, invalid_urls)
        _log_link_quality_diagnostics(
            plan_id=plan_id,
            stage=f"{stage}_sanitized",
            extracted_facts=extracted_facts,
            guide_data=sanitized,
        )
        return sanitized

    async def _evaluate_guide_data(
        self, guide_data: dict[str, Any], required_spot_names: list[str]
    ) -> dict[str, Any]:
        """旅行ガイドデータを評価する

        Args:
            guide_data: 評価対象の旅行ガイドデータ
            required_spot_names: 旅行計画に含まれるべきスポット名のリスト

        Returns:
            評価結果
        """
        logger.debug(
            "Evaluating guide data with AI",
            extra={
                "required_spot_count": len(required_spot_names),
                "guide_key_count": len(guide_data.keys()),
            },
        )
        guide_data_json = json.dumps(guide_data, ensure_ascii=False, indent=2)
        required_spots_text = "\n".join([f"- {name}" for name in required_spot_names])
        prompt = render_template(
            _EVALUATION_PROMPT_TEMPLATE,
            guide_data=guide_data_json,
            required_spots=required_spots_text,
        )
        system_instruction = render_template(_EVALUATION_SYSTEM_INSTRUCTION_TEMPLATE)

        return await self._ai_service.generate_structured_data(
            prompt=prompt,
            response_schema=TravelGuideEvaluationSchema,
            system_instruction=system_instruction,
        )

    def _check_evaluation_result(self, evaluation: dict[str, Any]) -> bool:
        """評価結果が合格かどうかをチェックする

        Args:
            evaluation: AIサービスからの評価結果

        Returns:
            合格の場合True
        """
        has_historical_comparison = evaluation.get("hasHistoricalComparison", False)
        all_spots_included = evaluation.get("allSpotsIncluded", False)

        # スポット網羅性と歴史的対比のみを評価基準にする
        return all_spots_included and has_historical_comparison

    def _get_failure_reasons(self, evaluation: dict[str, Any]) -> list[str]:
        """評価結果から不合格の理由を取得する

        Args:
            evaluation: AIサービスからの評価結果

        Returns:
            不合格の理由のリスト
        """
        reasons: list[str] = []

        # スポット漏れチェック
        if not evaluation.get("allSpotsIncluded", False):
            missing_spots = evaluation.get("missingSpots", [])
            if missing_spots:
                reasons.append(f"spotDetailsに含まれていないスポット: {', '.join(missing_spots)}")

        # 歴史的対比チェック
        if not evaluation.get("hasHistoricalComparison", False):
            reasons.append("overviewに歴史の有名な話題との対比が含まれていません")

        return reasons

    async def _generate_guide_data(
        self, travel_plan: TravelPlan, extracted_facts: str
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
        guide_prompt = _build_travel_guide_prompt(travel_plan, extracted_facts)
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


def _build_travel_guide_prompt(travel_plan: TravelPlan, extracted_facts: str) -> str:
    """旅行ガイド生成用のプロンプトを生成する（Step B）"""
    return render_template(
        _TRAVEL_GUIDE_PROMPT_TEMPLATE,
        destination=travel_plan.destination,
        spots_text=_build_spots_text(travel_plan),
        extracted_facts=extracted_facts,
    )
