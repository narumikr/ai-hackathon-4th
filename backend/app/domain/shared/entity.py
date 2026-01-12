"""共通エンティティ基底クラス."""

from abc import ABC
from typing import Any


class Entity(ABC):  # noqa: B024
    """エンティティの基底クラス.

    エンティティは一意のIDによって識別されるドメインオブジェクト。
    同一性は属性ではなくIDによって判断される。
    """

    def __init__(self, id: str | None = None):
        """エンティティを初期化する.

        Args:
            id: エンティティの一意識別子（Noneの場合は新規エンティティ）
        """
        self._id = id

    @property
    def id(self) -> str | None:
        """エンティティのID."""
        return self._id

    def __eq__(self, other: Any) -> bool:
        """エンティティの等価性をIDで判定する."""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """エンティティのハッシュ値をIDから計算する."""
        return hash(self.id)
