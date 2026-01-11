"""TouristSpotエンティティのテスト."""

import pytest

from app.domain.travel_plan.entity import TouristSpot
from app.domain.travel_plan.value_objects import Location


def test_create_tourist_spot():
    """前提条件: 有効な観光スポットデータ
    実行: TouristSpot作成
    検証: プロパティが正しく設定されている
    """
    spot = TouristSpot(
        id="spot-001",
        name="清水寺",
        location=Location(lat=34.9949, lng=135.785),
        description="京都を代表する寺院",
        user_notes="早朝訪問予定",
    )

    assert spot.id == "spot-001"
    assert spot.name == "清水寺"
    assert spot.location.lat == 34.9949
    assert spot.location.lng == 135.785
    assert spot.description == "京都を代表する寺院"
    assert spot.user_notes == "早朝訪問予定"


def test_tourist_spot_with_empty_id():
    """前提条件: 空のid
    実行: TouristSpot作成を試みる
    検証: ValueErrorが発生
    """
    with pytest.raises(ValueError, match="id is required"):
        TouristSpot(
            id="",
            name="清水寺",
            location=Location(lat=34.9949, lng=135.785),
        )


def test_tourist_spot_with_empty_name():
    """前提条件: 空の名前
    実行: TouristSpot作成を試みる
    検証: ValueErrorが発生
    """
    with pytest.raises(ValueError, match="Tourist spot name is required"):
        TouristSpot(
            id="spot-001",
            name="",
            location=Location(lat=34.9949, lng=135.785),
        )


def test_tourist_spot_with_invalid_location_type():
    """前提条件: 不正なLocation型
    実行: TouristSpot作成を試みる
    検証: ValueErrorが発生
    """
    with pytest.raises(ValueError, match="location must be a Location instance"):
        TouristSpot(
            id="spot-001",
            name="清水寺",
            location="invalid",  # type: ignore[arg-type]
        )
