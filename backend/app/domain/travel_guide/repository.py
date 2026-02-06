"""TravelGuide Aggregateのリポジトリインターフェース"""

from abc import ABC, abstractmethod

from app.domain.travel_guide.entity import TravelGuide


class ITravelGuideRepository(ABC):
    """TravelGuideリポジトリのインターフェース

    ドメイン層でのリポジトリインターフェース定義
    実装はインフラ層で提供される
    """

    @abstractmethod
    def save(self, travel_guide: TravelGuide, *, commit: bool = True) -> TravelGuide:
        """TravelGuideを保存する

        Args:
            travel_guide: 保存するTravelGuideエンティティ
            commit: Trueの場合はトランザクションをコミットする

        Returns:
            TravelGuide: 保存されたTravelGuide（IDが割り当てられている）
        """
        pass

    @abstractmethod
    def find_by_id(self, guide_id: str) -> TravelGuide | None:
        """IDでTravelGuideを検索する

        Args:
            guide_id: 旅行ガイドID

        Returns:
            TravelGuide | None: 見つかった場合はTravelGuide、見つからない場合はNone
        """
        pass

    @abstractmethod
    def find_by_plan_id(self, plan_id: str) -> TravelGuide | None:
        """旅行計画IDでTravelGuideを検索する

        Args:
            plan_id: 旅行計画ID

        Returns:
            TravelGuide | None: 見つかった場合はTravelGuide、見つからない場合はNone
        """
        pass

    @abstractmethod
    def delete(self, guide_id: str) -> None:
        """TravelGuideを削除する

        Args:
            guide_id: 削除する旅行ガイドID
        """
        pass

    @abstractmethod
    def update_spot_image_status(
        self,
        plan_id: str,
        spot_name: str,
        image_url: str | None,
        image_status: str,
        *,
        commit: bool = True,
    ) -> None:
        """特定スポットの画像情報のみを更新する"""
        pass
