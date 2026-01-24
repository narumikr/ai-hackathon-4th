"""TravelGuide生成ユースケースのテスト"""

from __future__ import annotations

from typing import Any

import pytest
from sqlalchemy.orm import Session

from app.application.ports.ai_service import IAIService
from app.application.use_cases.generate_travel_guide import GenerateTravelGuideUseCase
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.value_objects import GenerationStatus
from app.infrastructure.persistence.models import TravelPlanModel
from app.infrastructure.repositories.travel_guide_repository import TravelGuideRepository
from app.infrastructure.repositories.travel_plan_repository import TravelPlanRepository


class FakeAIService(IAIService):
    """テスト用のAIサービス"""

    def __init__(self, historical_info: str, structured_data: dict[str, Any]) -> None:
        self.historical_info = historical_info
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
        return self.historical_info

    async def analyze_image(
        self,
        prompt: str,
        image_uri: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        raise NotImplementedError

    async def generate_structured_data(
        self,
        prompt: str,
        response_schema: dict[str, Any],
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        return self.structured_data


def _structured_guide_payload() -> dict[str, Any]:
    return {
        "overview": "京都の代表的な寺院を巡りながら歴史の流れを学ぶ旅行ガイド。",
        "timeline": [
            {
                "year": 778,
                "event": "清水寺創建",
                "significance": "奈良時代から続く歴史的寺院の始まり。",
                "relatedSpots": ["清水寺"],
            },
            {
                "year": 1397,
                "event": "金閣寺創建",
                "significance": "室町時代の文化を象徴する建築。",
                "relatedSpots": ["金閣寺"],
            },
        ],
        "spotDetails": [
            {
                "spotName": "清水寺",
                "historicalBackground": "奈良時代末期に創建された古刹。",
                "highlights": ["清水の舞台", "音羽の滝"],
                "recommendedVisitTime": "早朝",
                "historicalSignificance": "平安京遷都以前の歴史を持つ。",
            },
            {
                "spotName": "金閣寺",
                "historicalBackground": "足利義満の別荘として建立された寺院。",
                "highlights": ["金箔の舎利殿", "鏡湖池"],
                "recommendedVisitTime": "午後",
                "historicalSignificance": "室町文化の象徴。",
            },
        ],
        "checkpoints": [
            {
                "spotName": "清水寺",
                "checkpoints": ["清水の舞台の高さを確認", "音羽の滝の由来を学ぶ"],
                "historicalContext": "断崖に建つ舞台は江戸時代の信仰文化を示す。",
            },
            {
                "spotName": "金閣寺",
                "checkpoints": ["金箔装飾の意味を学ぶ", "庭園の構成を確認"],
                "historicalContext": "将軍文化が色濃く反映された空間構成。",
            },
        ],
    }


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_creates_guide(
    db_session: Session, sample_travel_plan
) -> None:
    """前提条件: 旅行計画が存在する。
    実行: 旅行ガイドを生成する。
    検証: DTOと永続化結果が一致する。
    """
    # 前提条件: 旅行計画が存在する。
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        historical_info="京都の歴史情報を検索結果から取得。",
        structured_data=_structured_guide_payload(),
    )

    # 実行: 旅行ガイドを生成する。
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
    )
    dto = await use_case.execute(plan_id=sample_travel_plan.id)

    # 検証: DTOと永続化結果が一致する。
    assert dto.plan_id == sample_travel_plan.id
    assert dto.overview
    assert len(dto.timeline) == 2
    assert len(dto.spot_details) == 2
    assert len(dto.checkpoints) == 2

    saved = guide_repository.find_by_plan_id(sample_travel_plan.id)
    assert saved is not None
    assert saved.overview == dto.overview

    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    assert plan.guide_generation_status == GenerationStatus.SUCCEEDED


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_updates_existing_guide(
    db_session: Session, sample_travel_plan, sample_travel_guide
) -> None:
    """前提条件: 既存の旅行ガイドが存在する。
    実行: 旅行ガイドを再生成する。
    検証: 既存ガイドが更新される。
    """
    # 前提条件: 既存の旅行ガイドが存在する。
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        historical_info="再生成用の歴史情報を取得。",
        structured_data=_structured_guide_payload(),
    )

    # 実行: 旅行ガイドを再生成する。
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
    )
    dto = await use_case.execute(plan_id=sample_travel_plan.id)

    # 検証: 既存ガイドが更新される。
    assert dto.id == sample_travel_guide.id
    assert dto.overview == _structured_guide_payload()["overview"]


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_plan_not_found(db_session: Session) -> None:
    """前提条件: 存在しない旅行計画ID。
    実行: 旅行ガイドを生成する。
    検証: TravelPlanNotFoundErrorが発生する。
    """
    # 前提条件: 存在しない旅行計画ID。
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        historical_info="京都の歴史情報を検索結果から取得。",
        structured_data=_structured_guide_payload(),
    )

    # 実行 & 検証: TravelPlanNotFoundErrorが発生する。
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
    )
    with pytest.raises(TravelPlanNotFoundError):
        await use_case.execute(plan_id="non-existent-id")


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_rejects_duplicate_spot_names(
    db_session: Session,
) -> None:
    """前提条件: 旅行計画に同名スポットが含まれる。
    実行: 旅行ガイドを生成する。
    検証: ValueErrorが発生する。
    """
    # 前提条件: 旅行計画に同名スポットが含まれる。
    duplicate_plan = TravelPlanModel(
        user_id="test_user_002",
        title="重複スポットテスト",
        destination="京都",
        spots=[
            {
                "id": "spot-dup-001",
                "name": "清水寺",
                "description": "重複テスト用",
                "userNotes": "1回目",
            },
            {
                "id": "spot-dup-002",
                "name": "清水寺",
                "description": "重複テスト用",
                "userNotes": "2回目",
            },
        ],
        status="planning",
    )
    db_session.add(duplicate_plan)
    db_session.commit()
    db_session.refresh(duplicate_plan)

    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        historical_info="重複スポットの歴史情報。",
        structured_data=_structured_guide_payload(),
    )

    # 実行 & 検証: ValueErrorが発生する。
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
    )
    with pytest.raises(ValueError):
        await use_case.execute(plan_id=duplicate_plan.id)


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_rejects_non_dict_structured_response(
    db_session: Session, sample_travel_plan
) -> None:
    """前提条件: AIサービスが辞書以外の構造化データを返す。
    実行: 旅行ガイドを生成する。
    検証: ValueErrorが発生する。
    """
    # 前提条件: AIサービスが辞書以外の構造化データを返す。
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        historical_info="京都の歴史情報を検索結果から取得。",
        structured_data=[],
    )

    # 実行 & 検証: ValueErrorが発生する。
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
    )
    with pytest.raises(ValueError):
        await use_case.execute(plan_id=sample_travel_plan.id)

    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    assert plan.guide_generation_status == GenerationStatus.FAILED
