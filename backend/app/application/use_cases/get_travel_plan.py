"""旅行計画取得ユースケース"""

from app.application.dto.travel_plan_dto import TravelPlanDTO
from app.application.use_cases.travel_plan_helpers import validate_required_str
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.repository import ITravelPlanRepository


class GetTravelPlanUseCase:
    """旅行計画取得ユースケース

    IDを指定して単一の旅行計画を取得する。
    """

    def __init__(self, repository: ITravelPlanRepository):
        """ユースケースを初期化する

        Args:
            repository: TravelPlanリポジトリ
        """
        self._repository = repository

    def execute(self, plan_id: str) -> TravelPlanDTO:
        """旅行計画を取得する

        Args:
            plan_id: 旅行計画ID

        Returns:
            TravelPlanDTO: 旅行計画

        Raises:
            TravelPlanNotFoundError: 旅行計画が見つからない場合
        """
        validate_required_str(plan_id, "plan_id")

        travel_plan = self._repository.find_by_id(plan_id)
        if travel_plan is None:
            raise TravelPlanNotFoundError(plan_id)

        return TravelPlanDTO.from_entity(travel_plan)


class ListTravelPlansUseCase:
    """旅行計画一覧取得ユースケース

    ユーザーIDを指定して旅行計画の一覧を取得する。
    """

    def __init__(self, repository: ITravelPlanRepository):
        """ユースケースを初期化する

        Args:
            repository: TravelPlanリポジトリ
        """
        self._repository = repository

    def execute(self, user_id: str) -> list[TravelPlanDTO]:
        """ユーザーの旅行計画一覧を取得する

        Args:
            user_id: ユーザーID

        Returns:
            list[TravelPlanDTO]: 旅行計画リスト
        """
        validate_required_str(user_id, "user_id")

        travel_plans = self._repository.find_by_user_id(user_id)
        return [TravelPlanDTO.from_entity(plan) for plan in travel_plans]
