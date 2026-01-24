"""TravelPlanエンティティのテスト."""

from datetime import datetime

import pytest

from app.domain.travel_plan.entity import TouristSpot, TravelPlan
from app.domain.travel_plan.value_objects import GenerationStatus, PlanStatus


def test_create_travel_plan():
    """前提条件: 有効な旅行計画データ
    実行: TravelPlan作成
    検証: プロパティが正しく設定されている
    """
    # 前提条件: 有効な旅行計画データ
    user_id = "test_user_001"
    title = "京都歴史ツアー"
    destination = "京都"
    spot = TouristSpot(
        id="spot-001",
        name="清水寺",
        description="京都を代表する寺院",
        user_notes="早朝訪問予定",
    )

    # 実行: TravelPlan作成
    plan = TravelPlan(
        user_id=user_id,
        title=title,
        destination=destination,
        spots=[spot],
    )

    # 検証: プロパティが正しく設定されている
    assert plan.user_id == user_id
    assert plan.title == title
    assert plan.destination == destination
    assert len(plan.spots) == 1
    assert plan.spots[0].name == "清水寺"
    assert plan.status == PlanStatus.PLANNING
    assert plan.guide_generation_status == GenerationStatus.NOT_STARTED
    assert plan.reflection_generation_status == GenerationStatus.NOT_STARTED
    assert isinstance(plan.created_at, datetime)
    assert isinstance(plan.updated_at, datetime)


def test_create_travel_plan_with_empty_user_id():
    """前提条件: 空のuser_id
    実行: TravelPlan作成を試みる
    検証: ValueErrorが発生
    """
    # 前提条件: 空のuser_id
    spot = TouristSpot(
        id="spot-001",
        name="清水寺",
    )

    # 実行 & 検証: ValueErrorが発生
    with pytest.raises(ValueError, match="user_id is required"):
        TravelPlan(
            user_id="",
            title="京都歴史ツアー",
            destination="京都",
            spots=[spot],
        )


def test_create_travel_plan_with_empty_title():
    """前提条件: 空のtitle
    実行: TravelPlan作成を試みる
    検証: ValueError が発生
    """
    # 前提条件: 空のtitle
    spot = TouristSpot(
        id="spot-001",
        name="清水寺",
    )

    # 実行 & 検証: ValueErrorが発生
    with pytest.raises(ValueError, match="title is required"):
        TravelPlan(
            user_id="test_user_001",
            title="",
            destination="京都",
            spots=[spot],
        )


def test_create_travel_plan_with_empty_destination():
    """前提条件: 空のdestination
    実行: TravelPlan作成を試みる
    検証: ValueErrorが発生
    """
    # 前提条件: 空のdestination
    spot = TouristSpot(
        id="spot-001",
        name="清水寺",
    )

    # 実行 & 検証: ValueErrorが発生
    with pytest.raises(ValueError, match="destination is required"):
        TravelPlan(
            user_id="test_user_001",
            title="京都歴史ツアー",
            destination="",
            spots=[spot],
        )


def test_update_travel_plan():
    """前提条件: 既存のTravelPlan
    実行: タイトルを更新
    検証: タイトルが更新され、updated_atも更新されている
    """
    # 前提条件: 既存のTravelPlan
    spot = TouristSpot(
        id="spot-001",
        name="清水寺",
    )
    plan = TravelPlan(
        user_id="test_user_001",
        title="京都歴史ツアー",
        destination="京都",
        spots=[spot],
    )
    original_updated_at = plan.updated_at

    # 実行: タイトルを更新
    new_title = "京都歴史探訪の旅"
    plan.update_plan(title=new_title)

    # 検証: タイトルが更新され、updated_atも更新されている
    assert plan.title == new_title
    assert plan.updated_at > original_updated_at


def test_update_travel_plan_with_empty_title():
    """前提条件: 既存のTravelPlan
    実行: 空のタイトルで更新を試みる
    検証: ValueErrorが発生
    """
    # 前提条件: 既存のTravelPlan
    spot = TouristSpot(
        id="spot-001",
        name="清水寺",
    )
    plan = TravelPlan(
        user_id="test_user_001",
        title="京都歴史ツアー",
        destination="京都",
        spots=[spot],
    )

    # 実行 & 検証: ValueErrorが発生
    with pytest.raises(ValueError, match="title cannot be empty"):
        plan.update_plan(title="")


def test_update_travel_plan_spots():
    """前提条件: 既存のTravelPlan
    実行: spotsを更新
    検証: spotsが更新されている
    """
    # 前提条件: 既存のTravelPlan
    spot1 = TouristSpot(
        id="spot-001",
        name="清水寺",
    )
    plan = TravelPlan(
        user_id="test_user_001",
        title="京都歴史ツアー",
        destination="京都",
        spots=[spot1],
    )

    # 実行: spotsを更新（金閣寺を追加）
    spot2 = TouristSpot(
        id="spot-002",
        name="金閣寺",
    )
    plan.update_plan(spots=[spot1, spot2])

    # 検証: spotsが更新されている
    assert len(plan.spots) == 2
    assert plan.spots[1].name == "金閣寺"


def test_complete_travel_plan():
    """前提条件: 既存のTravelPlan
    実行: complete()を呼び出す
    検証: statusがCOMPLETEDになる
    """
    # 前提条件: 既存のTravelPlan（planning状態）
    spot = TouristSpot(
        id="spot-001",
        name="清水寺",
    )
    plan = TravelPlan(
        user_id="test_user_001",
        title="京都歴史ツアー",
        destination="京都",
        spots=[spot],
    )
    original_updated_at = plan.updated_at

    # 実行: complete()を呼び出す
    plan.complete()

    # 検証: statusがCOMPLETEDになり、updated_atも更新されている
    assert plan.status == PlanStatus.COMPLETED
    assert plan.updated_at > original_updated_at


def test_update_travel_plan_status():
    """前提条件: 既存のTravelPlan
    実行: statusを更新
    検証: statusが更新される
    """
    # 前提条件: 既存のTravelPlan
    spot = TouristSpot(
        id="spot-001",
        name="清水寺",
    )
    plan = TravelPlan(
        user_id="test_user_001",
        title="京都歴史ツアー",
        destination="京都",
        spots=[spot],
    )

    # 実行: statusを更新
    plan.update_status(PlanStatus.COMPLETED)

    # 検証: statusが更新される
    assert plan.status == PlanStatus.COMPLETED


def test_update_generation_statuses():
    """前提条件: 既存のTravelPlan
    実行: 生成ステータスを更新
    検証: 各ステータスが更新される
    """
    # 前提条件: 既存のTravelPlan
    spot = TouristSpot(
        id="spot-001",
        name="清水寺",
    )
    plan = TravelPlan(
        user_id="test_user_001",
        title="京都歴史ツアー",
        destination="京都",
        spots=[spot],
    )

    # 実行: 生成ステータスを更新
    plan.update_generation_statuses(
        guide_status=GenerationStatus.PROCESSING,
        reflection_status=GenerationStatus.FAILED,
    )

    # 検証: 各ステータスが更新される
    assert plan.guide_generation_status == GenerationStatus.PROCESSING
    assert plan.reflection_generation_status == GenerationStatus.FAILED


def test_travel_plan_spots_defensive_copy():
    """前提条件: 既存のTravelPlan
    実行: spots取得後、外部からリストを変更
    検証: 元のTravelPlanは変更されない（防御的コピー）
    """
    # 前提条件: 既存のTravelPlan
    spot = TouristSpot(
        id="spot-001",
        name="清水寺",
    )
    plan = TravelPlan(
        user_id="test_user_001",
        title="京都歴史ツアー",
        destination="京都",
        spots=[spot],
    )

    # 実行: spots取得後、外部からリストを変更
    spots_copy = plan.spots
    spots_copy.append(
        TouristSpot(
            id="spot-002",
            name="金閣寺",
        )
    )

    # 検証: 元のTravelPlanは変更されない
    assert len(plan.spots) == 1
    assert len(spots_copy) == 2
