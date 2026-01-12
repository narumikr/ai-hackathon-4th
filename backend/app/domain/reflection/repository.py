"""Reflection Aggregateのリポジトリインターフェース"""

from abc import ABC, abstractmethod

from app.domain.reflection.entity import Reflection


class IReflectionRepository(ABC):
    """Reflectionリポジトリのインターフェース

    ドメイン層でのリポジトリインターフェース定義
    実装はインフラ層で提供される
    """

    @abstractmethod
    def save(self, reflection: Reflection) -> Reflection:
        """Reflectionを保存する.

        Args:
            reflection: 保存するReflectionエンティティ

        Returns:
            Reflection: 保存されたReflection（IDが割り当てられている）
        """
        pass

    @abstractmethod
    def find_by_id(self, reflection_id: str) -> Reflection | None:
        """IDでReflectionを検索する.

        Args:
            reflection_id: 振り返りID

        Returns:
            Reflection | None: 見つかった場合はReflection、見つからない場合はNone
        """
        pass

    @abstractmethod
    def find_by_plan_id(self, plan_id: str) -> Reflection | None:
        """旅行計画IDでReflectionを検索する.

        Args:
            plan_id: 旅行計画ID

        Returns:
            Reflection | None: 見つかった場合はReflection、見つからない場合はNone
        """
        pass

    @abstractmethod
    def delete(self, reflection_id: str) -> None:
        """Reflectionを削除する.

        Args:
            reflection_id: 削除する振り返りID
        """
        pass
