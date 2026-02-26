"""写真分析ユースケースのテスト。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import pytest

from app.application.ports.ai_service import IAIService
from app.application.use_cases.analyze_photos import AnalyzePhotosUseCase
from app.domain.reflection.entity import Reflection
from app.domain.reflection.repository import IReflectionRepository
from app.domain.travel_plan.entity import TouristSpot, TravelPlan
from app.domain.travel_plan.repository import ITravelPlanRepository
from app.domain.travel_plan.value_objects import PlanStatus

if TYPE_CHECKING:
    from app.infrastructure.ai.schemas.base import GeminiResponseSchema

T = TypeVar("T", bound="GeminiResponseSchema")


class FakePlanRepository(ITravelPlanRepository):
    """テスト用のTravelPlanリポジトリ。"""

    def __init__(self, plan: TravelPlan) -> None:
        self._plan = plan

    def save(self, travel_plan: TravelPlan, *, commit: bool = True) -> TravelPlan:
        self._plan = travel_plan
        return travel_plan

    def find_by_id(self, plan_id: str) -> TravelPlan | None:
        if self._plan.id == plan_id:
            return self._plan
        return None

    def find_by_user_id(self, user_id: str) -> list[TravelPlan]:
        if self._plan.user_id == user_id:
            return [self._plan]
        return []

    def delete(self, plan_id: str) -> None:
        return None

    def begin_nested(self):
        raise NotImplementedError


class FakeReflectionRepository(IReflectionRepository):
    """テスト用のReflectionリポジトリ。"""

    def __init__(self, existing: Reflection | None = None) -> None:
        self._reflection = existing
        self.save_count = 0

    def save(self, reflection: Reflection) -> Reflection:
        self._reflection = reflection
        self.save_count += 1
        return reflection

    def find_by_id(self, reflection_id: str) -> Reflection | None:
        if self._reflection and self._reflection.id == reflection_id:
            return self._reflection
        return None

    def find_by_plan_id(self, plan_id: str) -> Reflection | None:
        if self._reflection and self._reflection.plan_id == plan_id:
            return self._reflection
        return None

    def delete(self, reflection_id: str) -> None:
        return None


class FakeAIService(IAIService):
    """テスト用のAIサービス。"""

    def __init__(self) -> None:
        self.call_counts_by_uri: dict[str, int] = {}

    async def generate_text(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        raise NotImplementedError

    async def generate_with_search(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        raise NotImplementedError

    async def analyze_image(
        self,
        prompt: str,
        image_uri: str,
        *,
        system_instruction: str | None = None,
        tools: list[str] | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        count = self.call_counts_by_uri.get(image_uri, 0) + 1
        self.call_counts_by_uri[image_uri] = count

        if image_uri.endswith("always-fail.jpg"):
            raise ValueError("analysis failed")
        if image_uri.endswith("retry-success.jpg") and count == 1:
            raise ValueError("temporary failure")
        return f"分析結果: {image_uri}"

    async def analyze_image_structured(
        self,
        prompt: str,
        image_uri: str,
        response_schema: type[T],
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    async def generate_structured_data(
        self,
        prompt: str,
        response_schema: type[T],
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    async def evaluate_travel_guide(
        self,
        guide_content: dict,
        evaluation_schema: type[T],
        evaluation_prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict:
        raise NotImplementedError


@pytest.mark.asyncio
async def test_execute_keeps_success_when_all_photos_fail() -> None:
    """前提条件: 全写真の分析が失敗する。
    実行: AnalyzePhotosUseCase.execute。
    検証: 例外を送出せずNoneを返し、Reflectionを保存しない。
    """
    plan = TravelPlan(
        id="plan-001",
        user_id="user-001",
        title="京都旅行",
        destination="京都",
        spots=[TouristSpot(id="spot-001", name="清水寺")],
        status=PlanStatus.PLANNING,
    )
    plan_repository = FakePlanRepository(plan)
    reflection_repository = FakeReflectionRepository(existing=None)
    ai_service = FakeAIService()

    use_case = AnalyzePhotosUseCase(
        plan_repository=plan_repository,
        reflection_repository=reflection_repository,
        ai_service=ai_service,
    )

    result = await use_case.execute(
        plan_id="plan-001",
        user_id="user-001",
        photos=[
            {
                "id": "photo-001",
                "spotId": "spot-001",
                "url": "https://example.com/always-fail.jpg",
            }
        ],
    )

    assert result is None
    assert reflection_repository.save_count == 0


@pytest.mark.asyncio
async def test_execute_retries_only_failed_photos_and_saves_successful_ones() -> None:
    """前提条件: 1枚は初回失敗後に成功し、もう1枚は初回から成功する。
    実行: AnalyzePhotosUseCase.execute。
    検証: 失敗した1枚だけ再試行され、成功分のみ保存される。
    """
    plan = TravelPlan(
        id="plan-002",
        user_id="user-001",
        title="京都旅行",
        destination="京都",
        spots=[TouristSpot(id="spot-001", name="清水寺")],
        status=PlanStatus.PLANNING,
    )
    plan_repository = FakePlanRepository(plan)
    reflection_repository = FakeReflectionRepository(existing=None)
    ai_service = FakeAIService()

    use_case = AnalyzePhotosUseCase(
        plan_repository=plan_repository,
        reflection_repository=reflection_repository,
        ai_service=ai_service,
    )

    result = await use_case.execute(
        plan_id="plan-002",
        user_id="user-001",
        photos=[
            {
                "id": "photo-001",
                "spotId": "spot-001",
                "url": "https://example.com/retry-success.jpg",
            },
            {
                "id": "photo-002",
                "spotId": "spot-001",
                "url": "https://example.com/success.jpg",
            },
        ],
    )

    assert result is not None
    assert len(result.photos) == 2
    assert ai_service.call_counts_by_uri["https://example.com/retry-success.jpg"] == 2
    assert ai_service.call_counts_by_uri["https://example.com/success.jpg"] == 1
    assert reflection_repository.save_count == 1
