"""旅行計画作成ユースケース."""

import uuid

from app.application.dto.travel_plan_dto import TravelPlanDTO
from app.domain.travel_plan.entity import TouristSpot, TravelPlan
from app.domain.travel_plan.repository import ITravelPlanRepository
from app.domain.travel_plan.value_objects import Location


class CreateTravelPlanUseCase:
    """旅行計画作成ユースケース.

    新しい旅行計画を作成し、リポジトリに保存する。
    """

    def __init__(self, repository: ITravelPlanRepository):
        """ユースケースを初期化する.

        Args:
            repository: TravelPlanリポジトリ
        """
        self._repository = repository

    def execute(
        self,
        user_id: str,
        title: str,
        destination: str,
        spots: list[dict],
    ) -> TravelPlanDTO:
        """旅行計画を作成する.

        Args:
            user_id: ユーザーID
            title: 旅行タイトル
            destination: 目的地
            spots: 観光スポットリスト（辞書形式）

        Returns:
            TravelPlanDTO: 作成された旅行計画

        Raises:
            ValueError: バリデーションエラー
        """
        # 辞書 → エンティティ変換
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

        # ドメインエンティティの生成
        travel_plan = TravelPlan(
            user_id=user_id,
            title=title,
            destination=destination,
            spots=tourist_spots,
        )

        # 永続化
        saved_plan = self._repository.save(travel_plan)

        # DTOに変換して返す
        return TravelPlanDTO.from_entity(saved_plan)
