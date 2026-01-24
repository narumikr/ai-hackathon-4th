"""TravelPlan関連のDTO"""

from dataclasses import dataclass
from datetime import datetime

from app.domain.travel_plan.entity import TravelPlan


@dataclass
class TravelPlanDTO:
    """TravelPlanのデータ転送オブジェクト

    ドメインエンティティとインターフェース層の間でデータを転送するために使用。
    """

    id: str
    user_id: str
    title: str
    destination: str
    spots: list[dict]
    status: str
    guide_generation_status: str
    reflection_generation_status: str
    guide: dict | None
    reflection: dict | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_entity(
        entity: TravelPlan,
        *,
        guide: dict | None = None,
        reflection: dict | None = None,
    ) -> "TravelPlanDTO":
        """ドメインエンティティからDTOを生成する

        Args:
            entity: TravelPlanエンティティ

        Returns:
            TravelPlanDTO: 生成されたDTO
        """
        return TravelPlanDTO(
            id=entity.id or "",
            user_id=entity.user_id,
            title=entity.title,
            destination=entity.destination,
            spots=[
                {
                    "id": spot.id,
                    "name": spot.name,
                    "description": spot.description,
                    "userNotes": spot.user_notes,
                }
                for spot in entity.spots
            ],
            status=entity.status.value,
            guide_generation_status=entity.guide_generation_status.value,
            reflection_generation_status=entity.reflection_generation_status.value,
            guide=guide,
            reflection=reflection,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
