"""Reflection Aggregateのドメインサービス"""

from app.domain.reflection.entity import Photo
from app.domain.reflection.exceptions import InvalidReflectionError
from app.domain.reflection.value_objects import ReflectionPamphlet, SpotReflection


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

        if not isinstance(spot_reflections, (list, tuple)) or not spot_reflections:
            raise InvalidReflectionError("spot_reflections must be a non-empty list.")

        spot_names: list[str] = []
        for item in spot_reflections:
            if not isinstance(item, dict):
                raise InvalidReflectionError("spot_reflections must contain dict items.")

            spot_name = item.get("spot_name")
            reflection = item.get("reflection")

            if not isinstance(spot_name, str) or not spot_name.strip():
                raise InvalidReflectionError(
                    "spot_reflections.spot_name must be a non-empty string."
                )

            if not isinstance(reflection, str) or not reflection.strip():
                raise InvalidReflectionError(
                    "spot_reflections.reflection must be a non-empty string."
                )

            spot_names.append(spot_name)

        if len(set(spot_names)) != len(spot_names):
            raise InvalidReflectionError("spot_reflections contains duplicate spot_name.")

        if not isinstance(next_trip_suggestions, (list, tuple)) or not next_trip_suggestions:
            raise InvalidReflectionError("next_trip_suggestions must be a non-empty list.")

        normalized_spot_reflections = tuple(spot_reflections)
        normalized_next_trip_suggestions = tuple(next_trip_suggestions)

        return ReflectionPamphlet(
            travel_summary=travel_summary,
            spot_reflections=normalized_spot_reflections,
            next_trip_suggestions=normalized_next_trip_suggestions,
        )
