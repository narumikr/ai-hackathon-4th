"""TravelGuide関連のDTO."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.travel_guide.entity import TravelGuide


@dataclass
class TravelGuideDTO:
    """TravelGuideのデータ転送オブジェクト.

    ドメインエンティティとインターフェース層の間でデータを転送するために使用。
    """

    id: str
    plan_id: str
    overview: str
    timeline: list[dict]
    spot_details: list[dict]
    checkpoints: list[dict]
    map_data: dict
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_entity(entity: TravelGuide) -> "TravelGuideDTO":
        """ドメインエンティティからDTOを生成する.

        Args:
            entity: TravelGuideエンティティ

        Returns:
            TravelGuideDTO: 生成されたDTO
        """
        return TravelGuideDTO(
            id=entity.id or "",
            plan_id=entity.plan_id,
            overview=entity.overview,
            timeline=[
                {
                    "year": event.year,
                    "event": event.event,
                    "significance": event.significance,
                    "relatedSpots": list(event.related_spots),
                }
                for event in entity.timeline
            ],
            spot_details=[
                {
                    "spotName": detail.spot_name,
                    "historicalBackground": detail.historical_background,
                    "highlights": list(detail.highlights),
                    "recommendedVisitTime": detail.recommended_visit_time,
                    "historicalSignificance": detail.historical_significance,
                }
                for detail in entity.spot_details
            ],
            checkpoints=[
                {
                    "spotName": checkpoint.spot_name,
                    "checkpoints": list(checkpoint.checkpoints),
                    "historicalContext": checkpoint.historical_context,
                }
                for checkpoint in entity.checkpoints
            ],
            map_data=dict(entity.map_data),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
