"""振り返りAPIのユニットテスト"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.domain.travel_plan.entity import TravelPlan, TouristSpot
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.value_objects import GenerationStatus, PlanStatus
from app.infrastructure.repositories.travel_plan_repository import TravelPlanRepository
from app.interfaces.api.v1.reflections import _update_reflection_status


class TestUpdateReflectionStatus:
    """_update_reflection_status関数のテスト"""

    def test_update_reflection_status_to_processing(self) -> None:
        """前提条件: 旅行計画が存在する
        実行: _update_reflection_status(PROCESSING)
        検証: 振り返り生成ステータスがPROCESSINGになる
        """
        plan = TravelPlan(
            id="plan-京都-001",
            user_id="user-太郎-001",
            title="京都旅行",
            destination="京都",
            spots=[
                TouristSpot(
                    id="spot-清水寺-001",
                    name="清水寺",
                    description="清水の舞台で有名な寺院",
                )
            ],
            status=PlanStatus.PLANNING,
        )

        mock_repository = MagicMock(spec=TravelPlanRepository)
        mock_repository.find_by_id.return_value = plan

        _update_reflection_status(
            mock_repository,
            "plan-京都-001",
            GenerationStatus.PROCESSING,
            commit=False,
        )

        assert plan.reflection_generation_status == GenerationStatus.PROCESSING
        mock_repository.save.assert_called_once_with(plan, commit=False)

    def test_update_reflection_status_to_succeeded(self) -> None:
        """前提条件: 旅行計画が存在する
        実行: _update_reflection_status(SUCCEEDED)
        検証: 振り返り生成ステータスがSUCCEEDEDになる
        """
        plan = TravelPlan(
            id="plan-京都-001",
            user_id="user-太郎-001",
            title="京都旅行",
            destination="京都",
            spots=[
                TouristSpot(
                    id="spot-清水寺-001",
                    name="清水寺",
                    description="清水の舞台で有名な寺院",
                )
            ],
            status=PlanStatus.PLANNING,
        )

        mock_repository = MagicMock(spec=TravelPlanRepository)
        mock_repository.find_by_id.return_value = plan

        _update_reflection_status(
            mock_repository,
            "plan-京都-001",
            GenerationStatus.SUCCEEDED,
            commit=True,
        )

        assert plan.reflection_generation_status == GenerationStatus.SUCCEEDED
        mock_repository.save.assert_called_once_with(plan, commit=True)

    def test_update_reflection_status_to_failed(self) -> None:
        """前提条件: 旅行計画が存在する
        実行: _update_reflection_status(FAILED)
        検証: 振り返り生成ステータスがFAILEDになる
        """
        plan = TravelPlan(
            id="plan-京都-001",
            user_id="user-太郎-001",
            title="京都旅行",
            destination="京都",
            spots=[
                TouristSpot(
                    id="spot-清水寺-001",
                    name="清水寺",
                    description="清水の舞台で有名な寺院",
                )
            ],
            status=PlanStatus.PLANNING,
        )

        mock_repository = MagicMock(spec=TravelPlanRepository)
        mock_repository.find_by_id.return_value = plan

        _update_reflection_status(
            mock_repository,
            "plan-京都-001",
            GenerationStatus.FAILED,
            commit=True,
        )

        assert plan.reflection_generation_status == GenerationStatus.FAILED
        mock_repository.save.assert_called_once_with(plan, commit=True)

    def test_update_reflection_status_raises_on_plan_not_found(self) -> None:
        """前提条件: 旅行計画が存在しない
        実行: _update_reflection_status
        検証: TravelPlanNotFoundErrorが発生する
        """
        mock_repository = MagicMock(spec=TravelPlanRepository)
        mock_repository.find_by_id.return_value = None

        with pytest.raises(TravelPlanNotFoundError):
            _update_reflection_status(
                mock_repository,
                "plan-存在しない-001",
                GenerationStatus.PROCESSING,
            )

        mock_repository.save.assert_not_called()
