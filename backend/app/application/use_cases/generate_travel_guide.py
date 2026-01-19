"""旅行ガイド生成ユースケース"""

from __future__ import annotations

from typing import Any

from app.application.dto.travel_guide_dto import TravelGuideDTO
from app.application.ports.ai_service import IAIService
from app.application.use_cases.travel_plan_helpers import validate_required_str
from app.domain.travel_guide.repository import ITravelGuideRepository
from app.domain.travel_guide.services import TravelGuideComposer
from app.domain.travel_guide.value_objects import (
    Checkpoint,
    HistoricalEvent,
    MapData,
    MapMarker,
    SpotDetail,
)
from app.domain.travel_plan.entity import TravelPlan
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.repository import ITravelPlanRepository
from app.domain.travel_plan.value_objects import GenerationStatus

_TRAVEL_GUIDE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "overview": {"type": "string"},
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
        "mapData": {
            "type": "object",
            "properties": {
                "center": {
                    "type": "object",
                    "properties": {"lat": {"type": "number"}, "lng": {"type": "number"}},
                    "required": ["lat", "lng"],
                },
                "zoom": {"type": "integer"},
                "markers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "lat": {"type": "number"},
                            "lng": {"type": "number"},
                            "label": {"type": "string"},
                        },
                        "required": ["lat", "lng", "label"],
                    },
                    "minItems": 1,
                },
            },
            "required": ["center", "zoom", "markers"],
        },
    },
    "required": ["overview", "timeline", "spotDetails", "checkpoints", "mapData"],
}


def _require_str(value: object, field_name: str) -> str:
    """必須の文字列フィールドを検証する"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string.")
    return value.strip()


def _require_list(value: object, field_name: str) -> list[Any]:
    """必須の配列フィールドを検証する"""
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} is required and must be a non-empty list.")
    return value


def _require_dict(value: object, field_name: str) -> dict[str, Any]:
    """必須の辞書フィールドを検証する"""
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{field_name} is required and must be a non-empty dict.")
    return value


def _require_number(value: object, field_name: str) -> float:
    """数値フィールドの検証"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number.")
    return float(value)


def _require_int(value: object, field_name: str) -> int:
    """整数フィールドの検証"""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be an int.")
    return value


def _build_timeline(items: list, spot_names: set[str]) -> list[HistoricalEvent]:
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
        if not related_spot_set.issubset(spot_names):
            missing = sorted(related_spot_set - spot_names)
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
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"spotDetails[{index}] must be a dict.")
        spot_name = _require_str(item.get("spotName"), f"spotDetails[{index}].spotName")
        if spot_name not in plan_spot_names:
            raise ValueError(
                f"spotDetails[{index}].spotName is not in travel plan spots: {spot_name}"
            )
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


def _build_checkpoints(items: list, plan_spot_names: set[str]) -> list[Checkpoint]:
    """チェックポイントデータを値オブジェクトに変換する"""
    checkpoints: list[Checkpoint] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"checkpoints[{index}] must be a dict.")
        spot_name = _require_str(item.get("spotName"), f"checkpoints[{index}].spotName")
        if spot_name not in plan_spot_names:
            raise ValueError(
                f"checkpoints[{index}].spotName is not in travel plan spots: {spot_name}"
            )
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


def _build_map_data(map_data: dict) -> MapData:
    """地図データを検証して構築する"""
    center = _require_dict(map_data.get("center"), "mapData.center")
    lat = _require_number(center.get("lat"), "mapData.center.lat")
    lng = _require_number(center.get("lng"), "mapData.center.lng")
    zoom = _require_int(map_data.get("zoom"), "mapData.zoom")
    markers = _require_list(map_data.get("markers"), "mapData.markers")

    marker_dicts: list[MapMarker] = []
    for index, marker in enumerate(markers):
        if not isinstance(marker, dict):
            raise ValueError(f"mapData.markers[{index}] must be a dict.")
        marker_lat = _require_number(marker.get("lat"), f"mapData.markers[{index}].lat")
        marker_lng = _require_number(marker.get("lng"), f"mapData.markers[{index}].lng")
        label = _require_str(marker.get("label"), f"mapData.markers[{index}].label")
        marker_dicts.append({"lat": marker_lat, "lng": marker_lng, "label": label})

    return {
        "center": {"lat": lat, "lng": lng},
        "zoom": zoom,
        "markers": marker_dicts,
    }


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
        validate_required_str(plan_id, "plan_id")

        travel_plan = self._plan_repository.find_by_id(plan_id)
        if travel_plan is None:
            raise TravelPlanNotFoundError(plan_id)

        if not travel_plan.id:
            raise ValueError("plan_id is required and must not be empty.")

        if not travel_plan.spots:
            raise ValueError("spots must not be empty.")

        plan_spot_names = [spot.name for spot in travel_plan.spots]
        duplicate_spots = {
            spot_name for spot_name in plan_spot_names if plan_spot_names.count(spot_name) > 1
        }
        if duplicate_spots:
            raise ValueError(f"duplicate spot names are not allowed: {sorted(duplicate_spots)}")

        travel_plan.update_generation_statuses(guide_status=GenerationStatus.PROCESSING)
        self._plan_repository.save(travel_plan, commit=commit)

        try:
            historical_prompt = _build_historical_info_prompt(travel_plan)
            historical_info = await self._ai_service.generate_with_search(
                prompt=historical_prompt,
                system_instruction="Collect concise historical information using search results.",
            )
            if not historical_info or not historical_info.strip():
                raise ValueError("historical_info must be a non-empty string.")

            guide_prompt = _build_travel_guide_prompt(travel_plan, historical_info)
            structured = await self._ai_service.generate_structured_data(
                prompt=guide_prompt,
                response_schema=_TRAVEL_GUIDE_SCHEMA,
                system_instruction=(
                    "Return JSON that exactly matches the response schema. "
                    "Use Japanese for narrative fields."
                ),
            )
            if not isinstance(structured, dict):
                raise ValueError("structured response must be a dict.")

            overview = _require_str(structured.get("overview"), "overview")
            timeline_items = _require_list(structured.get("timeline"), "timeline")
            spot_detail_items = _require_list(structured.get("spotDetails"), "spotDetails")
            checkpoint_items = _require_list(structured.get("checkpoints"), "checkpoints")
            map_data_raw = _require_dict(structured.get("mapData"), "mapData")

            plan_spot_name_set = set(plan_spot_names)
            spot_details = _build_spot_details(spot_detail_items, plan_spot_name_set)
            checkpoints = _build_checkpoints(checkpoint_items, plan_spot_name_set)
            timeline = _build_timeline(timeline_items, plan_spot_name_set)
            map_data = _build_map_data(map_data_raw)

            generated_guide = self._composer.compose(
                plan_id=travel_plan.id,
                overview=overview,
                timeline=timeline,
                spot_details=spot_details,
                checkpoints=checkpoints,
                map_data=map_data,
            )

            existing = self._guide_repository.find_by_plan_id(travel_plan.id)
            if existing is None:
                saved_guide = self._guide_repository.save(generated_guide, commit=commit)
            else:
                existing.update_guide(
                    overview=generated_guide.overview,
                    timeline=generated_guide.timeline,
                    spot_details=generated_guide.spot_details,
                    checkpoints=generated_guide.checkpoints,
                    map_data=generated_guide.map_data,
                )
                saved_guide = self._guide_repository.save(existing, commit=commit)
        except Exception:
            travel_plan.update_generation_statuses(guide_status=GenerationStatus.FAILED)
            self._plan_repository.save(travel_plan, commit=commit)
            raise

        travel_plan.update_generation_statuses(guide_status=GenerationStatus.SUCCEEDED)
        self._plan_repository.save(travel_plan, commit=commit)

        return TravelGuideDTO.from_entity(saved_guide)


def _build_historical_info_prompt(travel_plan: TravelPlan) -> str:
    """歴史情報収集用のプロンプトを生成する"""
    spots_text = "\n".join(
        [
            f"- {spot.name} (lat: {spot.location.lat}, lng: {spot.location.lng})"
            for spot in travel_plan.spots
        ]
    )
    return (
        "以下の旅行先と観光スポットについて、信頼できる歴史情報をまとめてください。\n"
        f"旅行先: {travel_plan.destination}\n"
        "観光スポット:\n"
        f"{spots_text}\n"
    )


def _build_travel_guide_prompt(travel_plan: TravelPlan, historical_info: str) -> str:
    """旅行ガイド生成用のプロンプトを生成する"""
    spots_text = "\n".join(
        [
            f"- {spot.name} (lat: {spot.location.lat}, lng: {spot.location.lng})"
            for spot in travel_plan.spots
        ]
    )
    return (
        "以下の旅行計画と歴史情報から旅行ガイドを生成してください。\n"
        "旅行計画:\n"
        f"- 目的地: {travel_plan.destination}\n"
        f"- 観光スポット:\n{spots_text}\n"
        "歴史情報:\n"
        f"{historical_info}\n"
    )
