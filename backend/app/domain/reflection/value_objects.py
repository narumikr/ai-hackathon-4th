"""振り返り集約の値オブジェクト"""

from dataclasses import dataclass
from typing import TypedDict

from app.domain.reflection.exceptions import InvalidReflectionError
from app.domain.shared.value_object import ValueObject


class SpotReflection(TypedDict):
    """スポットごとの振り返り"""

    spot_name: str
    reflection: str


def _normalize_str_list(
    value: list[str] | tuple[str, ...],
    field_name: str,
    *,
    allow_empty: bool,
) -> tuple[str, ...]:
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

    if not normalized and not allow_empty:
        raise ValueError(f"{field_name} must not be empty.")

    if any(not isinstance(item, str) or not item.strip() for item in normalized):
        raise ValueError(f"{field_name} must contain non-empty strings only.")

    return normalized


def _normalize_spot_reflections(
    value: list[SpotReflection] | tuple[SpotReflection, ...],
) -> tuple[SpotReflection, ...]:
    """スポット振り返りリストをタプルに正規化する

    Raises:
        InvalidReflectionError: 型や内容が不正な場合
    """
    if isinstance(value, list):
        normalized = tuple(value)
    elif isinstance(value, tuple):
        normalized = value
    else:
        raise InvalidReflectionError("spot_reflections must be a list or tuple.")

    if not normalized:
        raise InvalidReflectionError("spot_reflections must be a non-empty list")

    for item in normalized:
        if not isinstance(item, dict):
            raise InvalidReflectionError("spot_reflections must contain dict items.")

        spot_name = item.get("spot_name")
        reflection = item.get("reflection")

        if not isinstance(spot_name, str) or not spot_name.strip():
            raise InvalidReflectionError("spot_reflections.spot_name must be a non-empty string.")

        if not isinstance(reflection, str) or not reflection.strip():
            raise InvalidReflectionError("spot_reflections.reflection must be a non-empty string.")

    return normalized


@dataclass(frozen=True)
class ImageAnalysis(ValueObject):
    """画像分析結果"""

    detected_spots: tuple[str, ...]
    historical_elements: tuple[str, ...]
    landmarks: tuple[str, ...]
    confidence: float

    def __post_init__(self) -> None:
        """バリデーション

        早期失敗: 画像分析結果の検証
        """
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be a number.")

        if not 0 <= float(self.confidence) <= 1:
            raise ValueError("confidence must be between 0 and 1.")

        detected_spots = _normalize_str_list(
            self.detected_spots,
            "detected_spots",
            allow_empty=True,
        )
        historical_elements = _normalize_str_list(
            self.historical_elements,
            "historical_elements",
            allow_empty=True,
        )
        landmarks = _normalize_str_list(
            self.landmarks,
            "landmarks",
            allow_empty=True,
        )

        if not (detected_spots or historical_elements or landmarks):
            raise ValueError("image analysis must detect at least one item.")

        object.__setattr__(self, "detected_spots", detected_spots)
        object.__setattr__(self, "historical_elements", historical_elements)
        object.__setattr__(self, "landmarks", landmarks)


@dataclass(frozen=True)
class ReflectionPamphlet(ValueObject):
    """振り返りパンフレット"""

    travel_summary: str
    spot_reflections: tuple[SpotReflection, ...]
    next_trip_suggestions: tuple[str, ...]

    def __post_init__(self) -> None:
        """バリデーション

        早期失敗: パンフレット内容の検証
        """
        if not self.travel_summary or not self.travel_summary.strip():
            raise ValueError("travel_summary is required and must not be empty.")

        spot_reflections = _normalize_spot_reflections(self.spot_reflections)
        next_trip_suggestions = _normalize_str_list(
            self.next_trip_suggestions,
            "next_trip_suggestions",
            allow_empty=False,
        )

        object.__setattr__(self, "spot_reflections", spot_reflections)
        object.__setattr__(self, "next_trip_suggestions", next_trip_suggestions)
