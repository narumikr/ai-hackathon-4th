"""旅行計画取得ユースケース"""

from app.application.dto.reflection_dto import ReflectionDTO, ReflectionPamphletDTO
from app.application.dto.travel_guide_dto import TravelGuideDTO
from app.application.dto.travel_plan_dto import TravelPlanDTO
from app.application.use_cases.travel_plan_helpers import validate_required_str
from app.domain.reflection.repository import IReflectionRepository
from app.domain.travel_guide.repository import ITravelGuideRepository
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.repository import ITravelPlanRepository


class GetTravelPlanUseCase:
    """旅行計画取得ユースケース

    IDを指定して単一の旅行計画を取得する
    """

    def __init__(
        self,
        repository: ITravelPlanRepository,
        guide_repository: ITravelGuideRepository | None = None,
        reflection_repository: IReflectionRepository | None = None,
    ):
        """ユースケースを初期化する

        Args:
            repository: TravelPlanリポジトリ
            guide_repository: TravelGuideリポジトリ
        """
        self._repository = repository
        self._guide_repository = guide_repository
        self._reflection_repository = reflection_repository

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

        guide_data: dict | None = None
        if self._guide_repository is not None:
            guide = self._guide_repository.find_by_plan_id(plan_id)
            if guide is not None:
                guide_data = TravelGuideDTO.from_entity(guide).__dict__

        reflection_data: dict | None = None
        pamphlet_data: dict | None = None
        if self._reflection_repository is not None:
            reflection = self._reflection_repository.find_by_plan_id(plan_id)
            if reflection is not None:
                reflection_data = ReflectionDTO.from_entity(reflection).__dict__
                if reflection.pamphlet is not None:
                    pamphlet_data = ReflectionPamphletDTO.from_pamphlet(
                        reflection.pamphlet,
                        reflection_id=reflection.id or "",
                        plan_id=reflection.plan_id,
                    ).__dict__

        return TravelPlanDTO.from_entity(
            travel_plan,
            guide=guide_data,
            reflection=reflection_data,
            pamphlet=pamphlet_data,
        )


class ListTravelPlansUseCase:
    """旅行計画一覧取得ユースケース

    ユーザーIDを指定して旅行計画の一覧を取得する
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
