"""TravelGuide Aggregateのドメインサービス"""

from datetime import datetime

from app.domain.travel_guide.entity import TravelGuide
from app.domain.travel_guide.exceptions import InvalidTravelGuideError
from app.domain.travel_guide.value_objects import Checkpoint, HistoricalEvent, SpotDetail


class TravelGuideComposer:
    """TravelGuideを構成するドメインサービス"""

    def compose(
        self,
        plan_id: str,
        overview: str,
        timeline: list[HistoricalEvent],
        spot_details: list[SpotDetail],
        checkpoints: list[Checkpoint],
        *,
        allowed_related_spots: set[str] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> TravelGuide:
        """TravelGuideを生成する

        Raises:
            InvalidTravelGuideError: データ整合性が取れない場合
        """
        spot_names = [detail.spot_name for detail in spot_details]
        if len(set(spot_names)) != len(spot_names):
            raise InvalidTravelGuideError("spot_details contains duplicate spot_name.")

        spot_name_set = set(spot_names)

        for checkpoint in checkpoints:
            if checkpoint.spot_name not in spot_name_set:
                raise InvalidTravelGuideError(
                    f"checkpoint spot_name not found in spot_details: {checkpoint.spot_name}"
                )

        allowed_spot_names = spot_name_set | (allowed_related_spots or set())
        for event in timeline:
            missing = set(event.related_spots) - allowed_spot_names
            if missing:
                raise InvalidTravelGuideError(
                    f"timeline related_spots contains unsupported names: {sorted(missing)}"
                )

        return TravelGuide(
            plan_id=plan_id,
            overview=overview,
            timeline=timeline,
            spot_details=spot_details,
            checkpoints=checkpoints,
            created_at=created_at,
            updated_at=updated_at,
        )
