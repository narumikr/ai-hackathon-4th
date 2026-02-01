"""ReflectionPamphlet生成ユースケースのテスト"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import pytest
from sqlalchemy.orm import Session

from app.application.ports.ai_service import IAIService
from app.application.use_cases.generate_reflection import GenerateReflectionPamphletUseCase
from app.domain.travel_plan.value_objects import GenerationStatus
from app.infrastructure.repositories.reflection_repository import ReflectionRepository
from app.infrastructure.repositories.travel_guide_repository import TravelGuideRepository
from app.infrastructure.repositories.travel_plan_repository import TravelPlanRepository

if TYPE_CHECKING:
    from app.infrastructure.ai.schemas.base import GeminiResponseSchema

T = TypeVar("T", bound="GeminiResponseSchema")


class FakeAIService(IAIService):
    """テスト用のAIサービス"""

    def __init__(self, structured_data: dict[str, Any] | list[Any]) -> None:
        self.structured_data = structured_data

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
        raise NotImplementedError

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

    async def evaluate_travel_guide(
        self,
        guide_content: dict,
        evaluation_schema: dict,
        evaluation_prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict:
        """旅行ガイドの評価（テスト用：常に合格を返す）"""
        return {
            "spotEvaluations": [
                {
                    "spotName": spot["spotName"],
                    "hasCitation": True,
                    "citationExample": "テスト用出典",
                }
                for spot in guide_content.get("spotDetails", [])
            ],
            "hasHistoricalComparison": True,
            "historicalComparisonExample": "テスト用歴史的対比",
        }

    async def generate_structured_data(
        self,
        prompt: str,
        response_schema: type[T],
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        return self.structured_data  # type: ignore[return-value]


def _structured_reflection_payload() -> dict[str, Any]:
    return {
        "travelSummary": "歴史的な背景を学びながら巡る充実した旅でした。",
        "spotReflections": [
            {"spotName": "清水寺", "reflection": "舞台からの眺めが印象的だった。"},
            {"spotName": "金閣寺", "reflection": "金色の輝きと庭園の調和が美しい。"},
        ],
        "nextTripSuggestions": ["奈良の古都を巡る旅", "鎌倉の寺社を巡る旅"],
    }


@pytest.mark.asyncio
async def test_generate_reflection_pamphlet_use_case_updates_status_succeeded(
    db_session: Session,
    sample_travel_plan,
    sample_travel_guide,
    sample_reflection,
) -> None:
    """前提条件: 旅行計画/旅行ガイド/振り返りが存在する。
    実行: 振り返りパンフレットを生成する。
    検証: 生成ステータスがsucceededになる。
    """
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    reflection_repository = ReflectionRepository(db_session)
    ai_service = FakeAIService(structured_data=_structured_reflection_payload())

    use_case = GenerateReflectionPamphletUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        reflection_repository=reflection_repository,
        ai_service=ai_service,
    )
    dto = await use_case.execute(
        plan_id=sample_travel_plan.id,
        user_id=sample_travel_plan.user_id,
    )

    assert dto.plan_id == sample_travel_plan.id
    assert dto.travel_summary

    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    assert plan.reflection_generation_status == GenerationStatus.SUCCEEDED

    saved_reflection = reflection_repository.find_by_plan_id(sample_travel_plan.id)
    assert saved_reflection is not None
    assert saved_reflection.pamphlet is not None
    assert saved_reflection.pamphlet.travel_summary == dto.travel_summary


@pytest.mark.asyncio
async def test_generate_reflection_pamphlet_use_case_sets_failed_status_on_structured_error(
    db_session: Session,
    sample_travel_plan,
    sample_travel_guide,
    sample_reflection,
) -> None:
    """前提条件: 構造化データが不正。
    実行: 振り返りパンフレットを生成する。
    検証: 生成ステータスがfailedになる。
    """
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    reflection_repository = ReflectionRepository(db_session)
    ai_service = FakeAIService(structured_data=[])

    use_case = GenerateReflectionPamphletUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        reflection_repository=reflection_repository,
        ai_service=ai_service,
    )
    with pytest.raises(ValueError):
        await use_case.execute(
            plan_id=sample_travel_plan.id,
            user_id=sample_travel_plan.user_id,
        )

    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    assert plan.reflection_generation_status == GenerationStatus.FAILED
