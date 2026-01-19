"""振り返り集約のドメインサービス"""

from app.domain.reflection.entity import Photo
from app.domain.reflection.exceptions import InvalidReflectionError
from app.domain.reflection.value_objects import (
    ReflectionPamphlet,
    SpotReflection,
    _normalize_spot_reflections,
)


class ReflectionAnalyzer:
    """振り返り情報を検証・構成するドメインサービス"""

    def build_pamphlet(
        self,
        photos: list[Photo],
        travel_summary: str,
        spot_reflections: list[SpotReflection] | tuple[SpotReflection, ...],
        next_trip_suggestions: list[str] | tuple[str, ...],
    ) -> ReflectionPamphlet:
        """ReflectionPamphletを構成する

        Raises:
            InvalidReflectionError: データ整合性が取れない場合
        """
        if not isinstance(photos, list) or not photos:
            raise InvalidReflectionError("photos must be a non-empty list.")

        if not all(isinstance(photo, Photo) for photo in photos):
            raise InvalidReflectionError("photos must contain Photo items only.")

        normalized_spot_reflections = _normalize_spot_reflections(spot_reflections)

        # 重複チェックを別途実施
        spot_names = [item["spot_name"] for item in normalized_spot_reflections]
        if len(set(spot_names)) != len(spot_names):
            raise InvalidReflectionError("spot_reflections contains duplicate spot_name.")

        if not isinstance(next_trip_suggestions, (list, tuple)) or not next_trip_suggestions:
            raise InvalidReflectionError("next_trip_suggestions must be a non-empty list.")

        normalized_next_trip_suggestions = tuple(next_trip_suggestions)

        return ReflectionPamphlet(
            travel_summary=travel_summary,
            spot_reflections=normalized_spot_reflections,
            next_trip_suggestions=normalized_next_trip_suggestions,
        )
