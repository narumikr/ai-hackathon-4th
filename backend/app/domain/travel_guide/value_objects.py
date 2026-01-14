"""TravelGuide Aggregateの値オブジェクト"""

from dataclasses import dataclass
from typing import TypedDict

from app.domain.shared.value_object import ValueObject


class MapCenter(TypedDict):
    """地図の中心座標"""

    lat: float
    lng: float


class MapMarker(TypedDict):
    """地図上のマーカー"""

    lat: float
    lng: float
    label: str


class MapData(TypedDict):
    """地図データ"""

    center: MapCenter
    zoom: int
    markers: list[MapMarker]


def _normalize_str_list(value: list[str] | tuple[str, ...], field_name: str) -> tuple[str, ...]:
    """文字列リストをタプルに正規化する

    Raises:
        ValueError: 型や内容が不正な場合
    """
    if isinstance(value, list):
        normalized = tuple(value)
    elif isinstance(value, tuple):
        normalized = value
    else:
        raise ValueError(f"{field_name} must be a list or tuple of strings.")

    if not normalized:
        raise ValueError(f"{field_name} must not be empty.")

    if any(not isinstance(item, str) or not item.strip() for item in normalized):
        raise ValueError(f"{field_name} must contain non-empty strings only.")

    return normalized


@dataclass(frozen=True)
class HistoricalEvent(ValueObject):
    """歴史的イベント"""

    year: int
    event: str
    significance: str
    related_spots: tuple[str, ...]

    def __post_init__(self) -> None:
        """バリデーション

        早期失敗: 必須フィールドの検証
        """
        if not isinstance(self.year, int) or isinstance(self.year, bool):
            raise ValueError("year must be an int.")

        if not self.event or not self.event.strip():
            raise ValueError("event is required and must not be empty.")

        if not self.significance or not self.significance.strip():
            raise ValueError("significance is required and must not be empty.")

        normalized = _normalize_str_list(self.related_spots, "related_spots")
        object.__setattr__(self, "related_spots", normalized)


@dataclass(frozen=True)
class SpotDetail(ValueObject):
    """スポット詳細"""

    spot_name: str
    historical_background: str
    highlights: tuple[str, ...]
    recommended_visit_time: str
    historical_significance: str

    def __post_init__(self) -> None:
        """バリデーション

        早期失敗: 必須フィールドの検証
        """
        if not self.spot_name or not self.spot_name.strip():
            raise ValueError("spot_name is required and must not be empty.")

        if not self.historical_background or not self.historical_background.strip():
            raise ValueError("historical_background is required and must not be empty.")

        if not self.recommended_visit_time or not self.recommended_visit_time.strip():
            raise ValueError("recommended_visit_time is required and must not be empty.")

        if not self.historical_significance or not self.historical_significance.strip():
            raise ValueError("historical_significance is required and must not be empty.")

        normalized = _normalize_str_list(self.highlights, "highlights")
        object.__setattr__(self, "highlights", normalized)


@dataclass(frozen=True)
class Checkpoint(ValueObject):
    """チェックポイント"""

    spot_name: str
    checkpoints: tuple[str, ...]
    historical_context: str

    def __post_init__(self) -> None:
        """バリデーション

        早期失敗: 必須フィールドの検証
        """
        if not self.spot_name or not self.spot_name.strip():
            raise ValueError("spot_name is required and must not be empty.")

        if not self.historical_context or not self.historical_context.strip():
            raise ValueError("historical_context is required and must not be empty.")

        normalized = _normalize_str_list(self.checkpoints, "checkpoints")
        object.__setattr__(self, "checkpoints", normalized)
