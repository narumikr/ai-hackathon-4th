"""TravelPlan Aggregateのリポジトリインターフェース"""

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager

from app.domain.travel_plan.entity import TravelPlan


class ITravelPlanRepository(ABC):
    """TravelPlanリポジトリのインターフェース

    ドメイン層でのリポジトリインターフェース定義
    実装はインフラ層で提供される
    """

    @abstractmethod
    def save(self, travel_plan: TravelPlan, *, commit: bool = True) -> TravelPlan:
        """TravelPlanを保存する

        Args:
            travel_plan: 保存するTravelPlanエンティティ
            commit: Trueの場合はトランザクションをコミットする

        Returns:
            TravelPlan: 保存されたTravelPlan（IDが割り当てられている）
        """
        pass

    @abstractmethod
    def find_by_id(self, plan_id: str) -> TravelPlan | None:
        """IDでTravelPlanを検索する

        Args:
            plan_id: 旅行計画ID

        Returns:
            TravelPlan | None: 見つかった場合はTravelPlan、見つからない場合はNone
        """
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> list[TravelPlan]:
        """ユーザーIDでTravelPlanを検索する

        Args:
            user_id: ユーザーID

        Returns:
            list[TravelPlan]: ユーザーの旅行計画リスト（見つからない場合は空リスト）
        """
        pass

    @abstractmethod
    def delete(self, plan_id: str) -> None:
        """TravelPlanを削除する

        Args:
            plan_id: 削除する旅行計画ID
        """
        pass

    @abstractmethod
    def begin_nested(self) -> AbstractContextManager[None]:
        """ネストされたトランザクション（セーブポイント）を開始する"""
        pass
