"""旅行計画更新ユースケース."""

import uuid

from app.application.dto.travel_plan_dto import TravelPlanDTO
from app.domain.travel_plan.entity import TouristSpot
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.repository import ITravelPlanRepository
from app.domain.travel_plan.value_objects import Location


class UpdateTravelPlanUseCase:
    """旅行計画更新ユースケース.

    既存の旅行計画を更新する。
    """

    def __init__(self, repository: ITravelPlanRepository):
        """ユースケースを初期化する.

        Args:
            repository: TravelPlanリポジトリ
        """
        self._repository = repository

    def execute(
        self,
        plan_id: str,
        title: str | None = None,
        destination: str | None = None,
        spots: list[dict] | None = None,
    ) -> TravelPlanDTO:
        """旅行計画を更新する.

        Args:
            plan_id: 旅行計画ID
            title: 旅行タイトル（オプション）
            destination: 目的地（オプション）
            spots: 観光スポットリスト（オプション、辞書形式）

        Returns:
            TravelPlanDTO: 更新された旅行計画

        Raises:
            TravelPlanNotFoundError: 旅行計画が見つからない場合
            ValueError: バリデーションエラー
        """
        # 既存のエンティティを取得
        travel_plan = self._repository.find_by_id(plan_id)
        if travel_plan is None:
            raise TravelPlanNotFoundError(plan_id)

        # 観光スポットの変換
        tourist_spots = None
        if spots is not None:
            tourist_spots = []
            for spot in spots:
                spot_id = spot.get("id")
                if not spot_id or (isinstance(spot_id, str) and not spot_id.strip()):
                    spot_id = str(uuid.uuid4())

                tourist_spots.append(
                    TouristSpot(
                        id=str(spot_id),
                        name=spot["name"],
                        location=Location(
                            lat=spot["location"]["lat"],
                            lng=spot["location"]["lng"],
                        ),
                        description=spot.get("description"),
                        user_notes=spot.get("userNotes"),
                    )
                )

        # エンティティの更新
        travel_plan.update_plan(
            title=title,
            destination=destination,
            spots=tourist_spots,
        )

        # 永続化
        updated_plan = self._repository.save(travel_plan)

        # DTOに変換して返す
        return TravelPlanDTO.from_entity(updated_plan)
