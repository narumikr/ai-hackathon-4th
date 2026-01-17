"""振り返りパンフレット生成ユースケース"""

from __future__ import annotations

from typing import Any

from app.application.dto.reflection_dto import ReflectionDTO, ReflectionPamphletDTO
from app.application.ports.ai_service import IAIService
from app.application.use_cases.travel_plan_helpers import validate_required_str
from app.domain.reflection.exceptions import ReflectionNotFoundError
from app.domain.reflection.repository import IReflectionRepository
from app.domain.reflection.services import ReflectionAnalyzer
from app.domain.reflection.value_objects import SpotReflection
from app.domain.travel_guide.exceptions import TravelGuideNotFoundError
from app.domain.travel_guide.repository import ITravelGuideRepository
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.repository import ITravelPlanRepository

_REFLECTION_PAMPHLET_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "travelSummary": {"type": "string"},
        "spotReflections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "spotName": {"type": "string"},
                    "reflection": {"type": "string"},
                },
                "required": ["spotName", "reflection"],
            },
            "minItems": 1,
        },
        "nextTripSuggestions": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
        },
    },
    "required": ["travelSummary", "spotReflections", "nextTripSuggestions"],
}


def _require_str(value: object, field_name: str) -> str:
    """必須の文字列フィールドを検証する"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string.")
    return value.strip()


def _require_list(value: object, field_name: str) -> list:
    """必須の配列フィールドを検証する"""
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list.")
    return value


def _build_spot_reflections(
    items: list,
    plan_spot_names: set[str],
) -> list[SpotReflection]:
    """スポット振り返りのリストを構築する"""
    spot_reflections: list[SpotReflection] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"spotReflections[{index}] must be a dict.")

        spot_name = _require_str(item.get("spotName"), f"spotReflections[{index}].spotName")
        if spot_name not in plan_spot_names:
            raise ValueError(
                f"spotReflections[{index}].spotName is not in travel plan spots: {spot_name}"
            )

        reflection = _require_str(item.get("reflection"), f"spotReflections[{index}].reflection")

        spot_reflections.append(
            {
                "spot_name": spot_name,
                "reflection": reflection,
            }
        )

    spot_names = {item["spot_name"] for item in spot_reflections}
    missing = sorted(plan_spot_names - spot_names)
    if missing:
        raise ValueError(f"spotReflections is missing travel plan spots: {missing}")

    return spot_reflections


def _build_next_trip_suggestions(items: list) -> list[str]:
    """次回旅行の提案を構築する"""
    suggestions: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"nextTripSuggestions[{index}] must be a non-empty string.")
        suggestions.append(item.strip())
    return suggestions


def _build_reflection_prompt(
    destination: str,
    travel_title: str,
    spot_names: list[str],
    guide_overview: str,
    guide_timeline: list[dict],
    guide_spot_details: list[dict],
    guide_checkpoints: list[dict],
    photos: list[dict],
    user_notes: str,
) -> str:
    """振り返りパンフレット生成のプロンプトを構築する"""
    spots_text = "\n".join([f"- {spot}" for spot in spot_names])
    timeline_text = "\n".join(
        [f"- {item['year']}: {item['event']} ({item['significance']})" for item in guide_timeline]
    )
    spot_detail_text = "\n".join(
        [
            (
                f"- {detail['spotName']}: {detail['historicalBackground']} | "
                f"Highlights: {', '.join(detail['highlights'])} | "
                f"Significance: {detail['historicalSignificance']}"
            )
            for detail in guide_spot_details
        ]
    )
    checkpoint_text = "\n".join(
        [
            (
                f"- {checkpoint['spotName']}: {', '.join(checkpoint['checkpoints'])} | "
                f"Context: {checkpoint['historicalContext']}"
            )
            for checkpoint in guide_checkpoints
        ]
    )
    photo_text = "\n".join(
        [
            (
                f"- url: {photo['url']}\n"
                f"  detectedSpots: {', '.join(photo['analysis']['detectedSpots'])}\n"
                f"  historicalElements: {', '.join(photo['analysis']['historicalElements'])}\n"
                f"  landmarks: {', '.join(photo['analysis']['landmarks'])}\n"
                f"  userDescription: {photo.get('userDescription') or 'なし'}"
            )
            for photo in photos
        ]
    )

    return (
        "以下の旅行前情報と旅行後情報を統合し、振り返りパンフレットを作成してください。\n"
        "出力はJSONスキーマに準拠した内容のみを返してください。\n\n"
        "旅行前情報:\n"
        f"- 旅行タイトル: {travel_title}\n"
        f"- 旅行先: {destination}\n"
        "観光スポット:\n"
        f"{spots_text}\n\n"
        "旅行ガイド概要:\n"
        f"{guide_overview}\n\n"
        "年表:\n"
        f"{timeline_text}\n\n"
        "スポット詳細:\n"
        f"{spot_detail_text}\n\n"
        "チェックポイント:\n"
        f"{checkpoint_text}\n\n"
        "旅行後情報:\n"
        "写真分析:\n"
        f"{photo_text}\n\n"
        "ユーザーの感想:\n"
        f"{user_notes}\n"
    )


class GenerateReflectionPamphletUseCase:
    """振り返りパンフレット生成ユースケース"""

    def __init__(
        self,
        plan_repository: ITravelPlanRepository,
        guide_repository: ITravelGuideRepository,
        reflection_repository: IReflectionRepository,
        ai_service: IAIService,
        analyzer: ReflectionAnalyzer | None = None,
    ) -> None:
        """ユースケースを初期化する

        Args:
            plan_repository: TravelPlanリポジトリ
            guide_repository: TravelGuideリポジトリ
            reflection_repository: Reflectionリポジトリ
            ai_service: AIサービス
            analyzer: ReflectionAnalyzer（省略時はデフォルトを使用）
        """
        self._plan_repository = plan_repository
        self._guide_repository = guide_repository
        self._reflection_repository = reflection_repository
        self._ai_service = ai_service
        self._analyzer = analyzer or ReflectionAnalyzer()

    async def execute(
        self,
        plan_id: str,
        user_id: str,
        user_notes: str,
    ) -> ReflectionPamphletDTO:
        """振り返りパンフレットを生成する

        Args:
            plan_id: 旅行計画ID
            user_id: ユーザーID
            user_notes: ユーザーの感想

        Returns:
            ReflectionPamphletDTO: 生成されたパンフレット

        Raises:
            TravelPlanNotFoundError: 旅行計画が見つからない場合
            TravelGuideNotFoundError: 旅行ガイドが見つからない場合
            ReflectionNotFoundError: 振り返りが見つからない場合
            ValueError: バリデーションエラー
        """
        validate_required_str(plan_id, "plan_id")
        validate_required_str(user_id, "user_id")
        validate_required_str(user_notes, "user_notes")

        travel_plan = self._plan_repository.find_by_id(plan_id)
        if travel_plan is None:
            raise TravelPlanNotFoundError(plan_id)

        if travel_plan.user_id != user_id:
            raise ValueError("user_id does not match the travel plan owner.")

        reflection = self._reflection_repository.find_by_plan_id(plan_id)
        if reflection is None:
            raise ReflectionNotFoundError(plan_id)

        if reflection.user_id != user_id:
            raise ValueError("user_id does not match the reflection owner.")

        if not reflection.photos:
            raise ValueError("photos must be a non-empty list.")

        travel_guide = self._guide_repository.find_by_plan_id(plan_id)
        if travel_guide is None:
            raise TravelGuideNotFoundError(plan_id)

        if not travel_plan.spots:
            raise ValueError("travel plan spots must be a non-empty list.")

        reflection_dto = ReflectionDTO.from_entity(reflection)

        prompt = _build_reflection_prompt(
            destination=travel_plan.destination,
            travel_title=travel_plan.title,
            spot_names=[spot.name for spot in travel_plan.spots],
            guide_overview=travel_guide.overview,
            guide_timeline=[
                {
                    "year": event.year,
                    "event": event.event,
                    "significance": event.significance,
                }
                for event in travel_guide.timeline
            ],
            guide_spot_details=[
                {
                    "spotName": detail.spot_name,
                    "historicalBackground": detail.historical_background,
                    "highlights": list(detail.highlights),
                    "historicalSignificance": detail.historical_significance,
                }
                for detail in travel_guide.spot_details
            ],
            guide_checkpoints=[
                {
                    "spotName": checkpoint.spot_name,
                    "checkpoints": list(checkpoint.checkpoints),
                    "historicalContext": checkpoint.historical_context,
                }
                for checkpoint in travel_guide.checkpoints
            ],
            photos=reflection_dto.photos,
            user_notes=user_notes,
        )

        structured = await self._ai_service.generate_structured_data(
            prompt=prompt,
            response_schema=_REFLECTION_PAMPHLET_SCHEMA,
            system_instruction=(
                "Return JSON that exactly matches the response schema. "
                "Use Japanese for narrative fields."
            ),
        )
        if not isinstance(structured, dict):
            raise ValueError("structured response must be a dict.")

        travel_summary = _require_str(structured.get("travelSummary"), "travelSummary")
        spot_reflection_items = _require_list(structured.get("spotReflections"), "spotReflections")
        next_trip_items = _require_list(
            structured.get("nextTripSuggestions"), "nextTripSuggestions"
        )

        plan_spot_names = {spot.name for spot in travel_plan.spots}
        spot_reflections = _build_spot_reflections(spot_reflection_items, plan_spot_names)
        next_trip_suggestions = _build_next_trip_suggestions(next_trip_items)

        pamphlet = self._analyzer.build_pamphlet(
            photos=reflection.photos,
            travel_summary=travel_summary,
            spot_reflections=spot_reflections,
            next_trip_suggestions=next_trip_suggestions,
        )

        reflection.update_notes(user_notes)
        saved_reflection = self._reflection_repository.save(reflection)

        return ReflectionPamphletDTO.from_pamphlet(
            pamphlet,
            reflection_id=saved_reflection.id or "",
            plan_id=saved_reflection.plan_id,
        )
