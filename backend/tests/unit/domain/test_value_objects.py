"""値オブジェクトのテスト."""

import pytest

from app.domain.travel_plan.value_objects import Location, PlanStatus


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




def test_plan_status_enum():
    """前提条件: なし
    実行: PlanStatusのEnum値を確認
    検証: 期待される値が定義されている
    """
    # 検証: PlanStatusの値が定義されている
    assert PlanStatus.PLANNING.value == "planning"
    assert PlanStatus.COMPLETED.value == "completed"
