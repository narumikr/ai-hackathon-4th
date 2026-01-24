"""TouristSpotエンティティのテスト."""

import pytest

from app.domain.travel_plan.entity import TouristSpot


def test_create_tourist_spot():
    """前提条件: 有効な観光スポットデータ
    実行: TouristSpot作成
    検証: プロパティが正しく設定されている
    """
    spot = TouristSpot(
        id="spot-001",
        name="清水寺",
        description="京都を代表する寺院",
        user_notes="早朝訪問予定",
    )

    assert spot.id == "spot-001"
    assert spot.name == "清水寺"
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
        )
