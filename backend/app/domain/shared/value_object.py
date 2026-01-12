"""共通値オブジェクト基底クラス."""

from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject(ABC):  # noqa: B024
    """値オブジェクトの基底クラス.

    値オブジェクトは属性によって識別される不変のドメインオブジェクト。
    同一性は属性の値によって判断される。
    """

    pass
