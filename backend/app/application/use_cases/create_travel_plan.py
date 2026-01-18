"""旅行計画作成ユースケース"""

from app.application.dto.travel_plan_dto import TravelPlanDTO
from app.application.use_cases.travel_plan_helpers import (
    build_tourist_spots,
    validate_required_str,
)
from app.domain.travel_plan.entity import TravelPlan
from app.domain.travel_plan.repository import ITravelPlanRepository


class CreateTravelPlanUseCase:
    """旅行計画作成ユースケース

    新しい旅行計画を作成し、リポジトリに保存する
    """

    def __init__(self, repository: ITravelPlanRepository):
        """ユースケースを初期化する

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
        """旅行計画を作成する

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
        # 早期失敗: 必須フィールドの検証
        validate_required_str(user_id, "user_id")
        validate_required_str(title, "title")
        validate_required_str(destination, "destination")

        # 辞書 → エンティティ変換
        tourist_spots = build_tourist_spots(spots)

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
