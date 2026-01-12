"""TravelPlan Aggregateの値オブジェクト"""

from dataclasses import dataclass
from enum import Enum

from app.domain.shared.value_object import ValueObject


class PlanStatus(str, Enum):
    """旅行計画のステータス"""

    PLANNING = "planning"
    COMPLETED = "completed"


@dataclass(frozen=True)
class Location(ValueObject):
    """地理的位置（緯度経度）"""

    lat: float
    lng: float

    def __post_init__(self) -> None:
        """バリデーション

        早期失敗: 緯度経度の範囲チェック
        """
        # 緯度の範囲チェック（-90度〜90度）
        if not -90 <= self.lat <= 90:
            raise ValueError(f"Invalid latitude: {self.lat}. Must be between -90 and 90.")

        # 経度の範囲チェック（-180度〜180度）
        if not -180 <= self.lng <= 180:
            raise ValueError(f"Invalid longitude: {self.lng}. Must be between -180 and 180.")
