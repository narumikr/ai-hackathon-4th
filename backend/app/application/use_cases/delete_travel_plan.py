"""旅行計画削除ユースケース."""

from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.repository import ITravelPlanRepository


class DeleteTravelPlanUseCase:
    """旅行計画削除ユースケース.

    既存の旅行計画を削除する。
    """

    def __init__(self, repository: ITravelPlanRepository):
        """ユースケースを初期化する.

        Args:
            repository: TravelPlanリポジトリ
        """
        self._repository = repository

    def execute(self, plan_id: str) -> None:
        """旅行計画を削除する.

        Args:
            plan_id: 旅行計画ID

        Raises:
            TravelPlanNotFoundError: 旅行計画が見つからない場合
        """
        travel_plan = self._repository.find_by_id(plan_id)
        if travel_plan is None:
            raise TravelPlanNotFoundError(plan_id)

        self._repository.delete(plan_id)
