"""値オブジェクトのテスト."""

from app.domain.travel_plan.value_objects import PlanStatus


def test_plan_status_enum():
    """前提条件: なし
    実行: PlanStatusのEnum値を確認
    検証: 期待される値が定義されている
    """
    # 検証: PlanStatusの値が定義されている
    assert PlanStatus.PLANNING.value == "planning"
    assert PlanStatus.COMPLETED.value == "completed"
