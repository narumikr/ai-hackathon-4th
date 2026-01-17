"""旅行計画更新ユースケース"""

from app.application.dto.travel_plan_dto import TravelPlanDTO
from app.application.use_cases.travel_plan_helpers import (
    build_tourist_spots,
    validate_required_str,
)
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.repository import ITravelPlanRepository


class UpdateTravelPlanUseCase:
    """旅行計画更新ユースケース

    既存の旅行計画を更新する
    """

    def __init__(self, repository: ITravelPlanRepository):
        """ユースケースを初期化する

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
        """旅行計画を更新する

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
        # 早期失敗: 必須フィールドの検証
        validate_required_str(plan_id, "plan_id")

        # 既存のエンティティを取得
        travel_plan = self._repository.find_by_id(plan_id)
        if travel_plan is None:
            raise TravelPlanNotFoundError(plan_id)

        # 観光スポットの変換
        tourist_spots = None
        if spots is not None:
            tourist_spots = build_tourist_spots(spots, allow_empty=True)

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
