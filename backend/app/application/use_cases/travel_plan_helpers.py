"""旅行計画ユースケースの共通ヘルパー."""

import uuid

from app.domain.travel_plan.entity import TouristSpot
from app.domain.travel_plan.value_objects import Location


def validate_required_str(value: str, field_name: str) -> None:
    """必須文字列のバリデーション."""
    if value is None or not str(value).strip():
        raise ValueError(f"{field_name} is required and must not be empty.")


def _validate_number(value: object, field_name: str) -> float:
    """数値フィールドの検証."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number.")
    return float(value)


def build_tourist_spots(spots: list[dict], *, allow_empty: bool = False) -> list[TouristSpot]:
    """観光スポット辞書をTouristSpotエンティティに変換する."""
    if spots is None:
        raise ValueError("spots is required.")
    if not isinstance(spots, list):
        raise ValueError("spots must be a list.")
    if not spots and not allow_empty:
        raise ValueError("spots must not be empty.")

    tourist_spots: list[TouristSpot] = []
    for index, spot in enumerate(spots):
        if not isinstance(spot, dict):
            raise ValueError(f"spots[{index}] must be a dict.")

        name = spot.get("name")
        if name is None or not str(name).strip():
            raise ValueError(f"spots[{index}].name is required.")

        location = spot.get("location")
        if not isinstance(location, dict):
            raise ValueError(f"spots[{index}].location is required.")

        lat = location.get("lat")
        lng = location.get("lng")
        if lat is None or lng is None:
            raise ValueError(f"spots[{index}].location.lat and lng are required.")

        spot_id = spot.get("id")
        if spot_id is None or not str(spot_id).strip():
            spot_id = str(uuid.uuid4())

        tourist_spots.append(
            TouristSpot(
                id=str(spot_id),
                name=str(name),
                location=Location(
                    lat=_validate_number(lat, f"spots[{index}].location.lat"),
                    lng=_validate_number(lng, f"spots[{index}].location.lng"),
                ),
                description=spot.get("description"),
                user_notes=spot.get("userNotes"),
            )
        )

    return tourist_spots
