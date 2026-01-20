"""振り返り集約のリポジトリインターフェース"""

from abc import ABC, abstractmethod

from app.domain.reflection.entity import Reflection


class IReflectionRepository(ABC):
    """振り返りリポジトリのインターフェース

    ドメイン層でのリポジトリインターフェース定義
    実装はインフラ層で提供される
    """

    @abstractmethod
    def save(self, reflection: Reflection) -> Reflection:
        """振り返りを保存する

        Args:
            reflection: 保存する振り返りエンティティ

        Returns:
            Reflection: 保存された振り返り（IDが割り当てられている）
        """
        pass

    @abstractmethod
    def find_by_id(self, reflection_id: str) -> Reflection | None:
        """IDで振り返りを検索する

        Args:
            reflection_id: 振り返りID

        Returns:
            Reflection | None: 見つかった場合は振り返り、見つからない場合はNone
        """
        pass

    @abstractmethod
    def find_by_plan_id(self, plan_id: str) -> Reflection | None:
        """旅行計画IDで振り返りを検索する

        Args:
            plan_id: 旅行計画ID

        Returns:
            Reflection | None: 見つかった場合は振り返り、見つからない場合はNone
        """
        pass

    @abstractmethod
    def delete(self, reflection_id: str) -> None:
        """振り返りを削除する

        Args:
            reflection_id: 削除する振り返りID
        """
        pass
