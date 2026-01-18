"""Reflection関連のDTO"""

from dataclasses import dataclass
from datetime import datetime

from app.domain.reflection.entity import Reflection
from app.domain.reflection.value_objects import ReflectionPamphlet


@dataclass
class ReflectionDTO:
    """Reflectionのデータ転送オブジェクト"""

    id: str
    plan_id: str
    user_id: str
    photos: list[dict]
    user_notes: str | None
    created_at: datetime

    @staticmethod
    def from_entity(entity: Reflection) -> "ReflectionDTO":
        """ドメインエンティティからDTOを生成する

        Args:
            entity: Reflectionエンティティ

        Returns:
            ReflectionDTO: 生成されたDTO
        """
        return ReflectionDTO(
            id=entity.id or "",
            plan_id=entity.plan_id,
            user_id=entity.user_id,
            photos=[
                {
                    "id": photo.id,
                    "url": photo.url,
                    "analysis": {
                        "detectedSpots": list(photo.analysis.detected_spots),
                        "historicalElements": list(photo.analysis.historical_elements),
                        "landmarks": list(photo.analysis.landmarks),
                        "confidence": photo.analysis.confidence,
                    },
                    "userDescription": photo.user_description,
                }
                for photo in entity.photos
            ],
            user_notes=entity.user_notes,
            created_at=entity.created_at,
        )


@dataclass
class ReflectionPamphletDTO:
    """ReflectionPamphletのデータ転送オブジェクト"""

    reflection_id: str
    plan_id: str
    travel_summary: str
    spot_reflections: list[dict]
    next_trip_suggestions: list[str]

    @staticmethod
    def from_pamphlet(
        pamphlet: ReflectionPamphlet,
        *,
        reflection_id: str,
        plan_id: str,
    ) -> "ReflectionPamphletDTO":
        """ReflectionPamphletからDTOを生成する

        Args:
            pamphlet: ReflectionPamphlet値オブジェクト
            reflection_id: 振り返りID
            plan_id: 旅行計画ID

        Returns:
            ReflectionPamphletDTO: 生成されたDTO
        """
        return ReflectionPamphletDTO(
            reflection_id=reflection_id,
            plan_id=plan_id,
            travel_summary=pamphlet.travel_summary,
            spot_reflections=[
                {
                    "spotName": item["spot_name"],
                    "reflection": item["reflection"],
                }
                for item in pamphlet.spot_reflections
            ],
            next_trip_suggestions=list(pamphlet.next_trip_suggestions),
        )
