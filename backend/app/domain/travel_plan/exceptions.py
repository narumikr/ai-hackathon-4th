"""TravelPlan Aggregateのドメイン例外"""


class TravelPlanDomainError(Exception):
    """TravelPlan Aggregateのドメインエラー基底クラス"""

    pass


class TravelPlanNotFoundError(TravelPlanDomainError):
    """TravelPlanが見つからない"""

    def __init__(self, plan_id: str):
        """TravelPlanNotFoundErrorを初期化する

        Args:
            plan_id: 見つからなかった旅行計画ID
        """
        self.plan_id = plan_id
        super().__init__(f"TravelPlan not found: {plan_id}")


class InvalidTravelPlanError(TravelPlanDomainError):
    """TravelPlanのバリデーションエラー"""

    pass
