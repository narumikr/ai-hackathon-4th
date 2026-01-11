"""値オブジェクトのテスト."""

import pytest

from app.domain.travel_plan.value_objects import Location, PlanStatus, TouristSpot


def test_create_location():
    """前提条件: 有効な緯度経度データ
    実行: Location作成
    検証: プロパティが正しく設定されている
    """
    # 前提条件: 有効な緯度経度（京都清水寺の座標）
    lat = 34.9949
    lng = 135.785

    # 実行: Location作成
    location = Location(lat=lat, lng=lng)

    # 検証: プロパティが正しく設定されている
    assert location.lat == lat
    assert location.lng == lng


def test_location_immutability():
    """前提条件: Locationオブジェクト
    実行: プロパティの変更を試みる
    検証: 不変性が保証されている（エラーが発生）
    """
    # 前提条件: Locationオブジェクト
    location = Location(lat=34.9949, lng=135.785)

    # 実行 & 検証: プロパティは変更できない（frozenなdataclass）
    with pytest.raises(Exception):  # FrozenInstanceError
        location.lat = 35.0  # type: ignore


def test_location_with_invalid_latitude():
    """前提条件: 無効な緯度データ（範囲外）
    実行: Location作成を試みる
    検証: ValueErrorが発生
    """
    # 前提条件: 無効な緯度（-90度〜90度の範囲外）
    invalid_lat = 91.0

    # 実行 & 検証: ValueErrorが発生
    with pytest.raises(ValueError, match="Invalid latitude"):
        Location(lat=invalid_lat, lng=135.785)


def test_location_with_invalid_longitude():
    """前提条件: 無効な経度データ（範囲外）
    実行: Location作成を試みる
    検証: ValueErrorが発生
    """
    # 前提条件: 無効な経度（-180度〜180度の範囲外）
    invalid_lng = 181.0

    # 実行 & 検証: ValueErrorが発生
    with pytest.raises(ValueError, match="Invalid longitude"):
        Location(lat=34.9949, lng=invalid_lng)


def test_create_tourist_spot():
    """前提条件: 有効な観光スポットデータ
    実行: TouristSpot作成
    検証: プロパティが正しく設定されている
    """
    # 前提条件: 有効な観光スポットデータ
    name = "清水寺"
    location = Location(lat=34.9949, lng=135.785)
    description = "京都を代表する寺院"
    user_notes = "早朝訪問予定"

    # 実行: TouristSpot作成
    spot = TouristSpot(
        name=name,
        location=location,
        description=description,
        user_notes=user_notes,
    )

    # 検証: プロパティが正しく設定されている
    assert spot.name == name
    assert spot.location == location
    assert spot.description == description
    assert spot.user_notes == user_notes


def test_tourist_spot_with_empty_name():
    """前提条件: 空の名前
    実行: TouristSpot作成を試みる
    検証: ValueErrorが発生
    """
    # 前提条件: 空の名前
    empty_name = ""
    location = Location(lat=34.9949, lng=135.785)

    # 実行 & 検証: ValueErrorが発生
    with pytest.raises(ValueError, match="Tourist spot name is required"):
        TouristSpot(name=empty_name, location=location)


def test_tourist_spot_with_whitespace_only_name():
    """前提条件: 空白文字のみの名前
    実行: TouristSpot作成を試みる
    検証: ValueErrorが発生
    """
    # 前提条件: 空白文字のみの名前
    whitespace_name = "   "
    location = Location(lat=34.9949, lng=135.785)

    # 実行 & 検証: ValueErrorが発生
    with pytest.raises(ValueError, match="Tourist spot name is required"):
        TouristSpot(name=whitespace_name, location=location)


def test_plan_status_enum():
    """前提条件: なし
    実行: PlanStatusのEnum値を確認
    検証: 期待される値が定義されている
    """
    # 検証: PlanStatusの値が定義されている
    assert PlanStatus.PLANNING.value == "planning"
    assert PlanStatus.COMPLETED.value == "completed"
