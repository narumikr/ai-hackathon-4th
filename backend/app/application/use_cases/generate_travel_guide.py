"""旅行ガイド生成ユースケース"""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import ValidationError

from app.application.dto.travel_guide_dto import TravelGuideDTO
from app.application.ports.ai_service import IAIService
from app.application.use_cases.travel_plan_helpers import validate_required_str
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
from app.prompts import render_template

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

logger = logging.getLogger(__name__)


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
        composer: TravelGuideComposer | None = None,
    ) -> None:
        """ユースケースを初期化する

        Args:
            plan_repository: TravelPlanリポジトリ
            guide_repository: TravelGuideリポジトリ
            ai_service: AIサービス
            composer: TravelGuideComposer（省略時はデフォルトを使用）
        """
        self._plan_repository = plan_repository
        self._guide_repository = guide_repository
        self._ai_service = ai_service
        self._composer = composer or TravelGuideComposer()

    async def execute(self, plan_id: str, *, commit: bool = True) -> TravelGuideDTO:
        """旅行ガイドを生成する

        Args:
            plan_id: 旅行計画ID
            commit: Trueの場合はトランザクションをコミットする

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
        except Exception:
            logger.exception(
                "Travel guide generation failed in use case",
                extra={"plan_id": plan_id},
            )
            failed_plan = self._plan_repository.find_by_id(travel_plan.id) or travel_plan
            failed_plan.update_generation_statuses(guide_status=GenerationStatus.FAILED)
            self._plan_repository.save(failed_plan, commit=commit)
            raise

        travel_plan.update_generation_statuses(guide_status=GenerationStatus.SUCCEEDED)
        self._plan_repository.save(travel_plan, commit=commit)
        logger.debug(
            "Guide status set to succeeded in use case",
            extra={"plan_id": plan_id},
        )

        return TravelGuideDTO.from_entity(saved_guide)

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
        spot_evaluations = evaluation.get("spotEvaluations", [])
        has_historical_comparison = evaluation.get("hasHistoricalComparison", False)
        all_spots_included = evaluation.get("allSpotsIncluded", False)

        # 全てのスポットが含まれ、全てのスポットに出典があり、歴史的対比もある場合のみ合格
        all_spots_have_citation = all(spot.get("hasCitation", False) for spot in spot_evaluations)

        return all_spots_included and all_spots_have_citation and has_historical_comparison

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

        # 出典チェック
        spot_evaluations = evaluation.get("spotEvaluations", [])
        missing_citations = [
            spot.get("spotName", "")
            for spot in spot_evaluations
            if not spot.get("hasCitation", False)
        ]

        if missing_citations:
            reasons.append(f"出典が不足しているスポット: {', '.join(missing_citations)}")

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
    return "指定なし（目的地に基づいておすすめの観光スポットを提案してください）"


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
