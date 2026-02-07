"""TravelGuide生成ユースケースのテスト"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import pytest
from sqlalchemy.orm import Session

from app.application.ports.ai_service import IAIService
from app.application.use_cases.generate_travel_guide import GenerateTravelGuideUseCase
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.value_objects import GenerationStatus
from app.infrastructure.persistence.models import TravelPlanModel, TravelPlanSpotModel
from app.infrastructure.repositories.travel_guide_repository import TravelGuideRepository
from app.infrastructure.repositories.travel_plan_repository import TravelPlanRepository

if TYPE_CHECKING:
    from app.infrastructure.ai.schemas.base import GeminiResponseSchema

T = TypeVar("T", bound="GeminiResponseSchema")


class FakeAIService(IAIService):
    """テスト用のAIサービス"""

    def __init__(
        self,
        extracted_facts: str,
        structured_data: dict[str, Any] | list[dict[str, Any]],
        evaluation_data: dict[str, Any] | list[dict[str, Any]] | None = None,
    ) -> None:
        self.extracted_facts = extracted_facts
        self.structured_data = structured_data
        self.evaluation_data = evaluation_data
        self.call_count = 0
        self.evaluation_call_count = 0

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
        return self.extracted_facts

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
        evaluation_schema: type[T],
        evaluation_prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict:
        """旅行ガイドの評価"""
        self.evaluation_call_count += 1
        if self.evaluation_data is None:
            # デフォルトの評価結果（全て合格）
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
        if isinstance(self.evaluation_data, list):
            if not self.evaluation_data:
                return self.evaluation_data  # type: ignore[return-value]
            index = min(self.evaluation_call_count - 1, len(self.evaluation_data) - 1)
            return self.evaluation_data[index]
        return self.evaluation_data

    async def generate_structured_data(
        self,
        prompt: str,
        response_schema: type[T],
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        # 評価用のプロンプトかどうかを判定
        if "評価してください" in prompt or "評価基準" in prompt:
            self.evaluation_call_count += 1
            if self.evaluation_data is None:
                # デフォルトの評価結果（全て合格）
                return {
                    "spotEvaluations": [
                        {
                            "spotName": "清水寺",
                            "hasCitation": True,
                            "citationExample": "『京都の歴史』",
                        },
                        {
                            "spotName": "金閣寺",
                            "hasCitation": True,
                            "citationExample": "公式サイト",
                        },
                    ],
                    "hasHistoricalComparison": True,
                    "historicalComparisonExample": "同時期のヨーロッパ",
                    "allSpotsIncluded": True,
                    "missingSpots": [],
                }
            if isinstance(self.evaluation_data, list):
                if not self.evaluation_data:
                    return self.evaluation_data  # type: ignore[return-value]
                index = min(self.evaluation_call_count - 1, len(self.evaluation_data) - 1)
                return self.evaluation_data[index]
            return self.evaluation_data

        # 通常の生成
        self.call_count += 1
        if isinstance(self.structured_data, list):
            # リストの場合は呼び出し回数に応じて返す
            if not self.structured_data:
                # 空のリストの場合はそのまま返す（型エラーを発生させるため）
                return self.structured_data  # type: ignore[return-value]
            index = min(self.call_count - 1, len(self.structured_data) - 1)
            return self.structured_data[index]
        return self.structured_data



def _structured_guide_payload() -> dict[str, Any]:
    return {
        "overview": "京都の代表的な寺院を巡りながら歴史の流れを学ぶ旅行ガイドです。清水寺と金閣寺を中心に、時代ごとの文化や人々の営みを辿り、現地での体験を通じて理解を深められる内容にまとめています。宗教と政治の背景、町の成り立ちや景観の変化にも触れ、旅全体のテーマと学びをはっきり示します。",
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
                "historicalBackground": "奈良時代末期に創建された古刹で、平安京遷都以前から続く歴史的な寺院。",
                "highlights": ["清水の舞台", "音羽の滝"],
                "recommendedVisitTime": "早朝",
                "historicalSignificance": "平安京遷都以前の歴史を持ち、京都最古級の寺院として知られる。",
            },
            {
                "spotName": "金閣寺",
                "historicalBackground": "足利義満の別荘として建立された寺院で、室町時代の文化を象徴する建築物。",
                "highlights": ["金箔の舎利殿", "鏡湖池"],
                "recommendedVisitTime": "午後",
                "historicalSignificance": "室町文化の象徴として、日本建築史上でも重要な位置を占める。",
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


def _structured_guide_payload_with_recommendations() -> dict[str, Any]:
    return {
        "overview": "京都の主要寺院に加えて城郭も巡る旅行ガイドです。寺院文化と武家文化の両面から京都の歴史を俯瞰できるように構成し、各スポットの関係性と時代背景を示しながら、学びのポイントを丁寧に整理しています。宗教施設と城郭の役割の違いを比較し、旅行のハイライトと体験価値が伝わる内容にしています。",
        "timeline": [
            {
                "year": 794,
                "event": "平安京遷都",
                "significance": "京都の歴史的発展の起点となる出来事。",
                "relatedSpots": ["京都"],
            },
            {
                "year": 1603,
                "event": "二条城の築城",
                "significance": "江戸幕府の権威を示す城郭の建立。",
                "relatedSpots": ["二条城"],
            },
            {
                "year": 778,
                "event": "清水寺創建",
                "significance": "奈良時代から続く歴史的寺院の始まり。",
                "relatedSpots": ["清水寺"],
            },
        ],
        "spotDetails": [
            {
                "spotName": "清水寺",
                "historicalBackground": "奈良時代末期に創建された古刹で、平安京遷都以前から続く歴史的な寺院。",
                "highlights": ["清水の舞台", "音羽の滝"],
                "recommendedVisitTime": "早朝",
                "historicalSignificance": "平安京遷都以前の歴史を持ち、京都最古級の寺院として知られる。",
            },
            {
                "spotName": "金閣寺",
                "historicalBackground": "足利義満の別荘として建立された寺院で、室町時代の文化を象徴する建築物。",
                "highlights": ["金箔の舎利殿", "鏡湖池"],
                "recommendedVisitTime": "午後",
                "historicalSignificance": "室町文化の象徴として、日本建築史上でも重要な位置を占める。",
            },
            {
                "spotName": "二条城",
                "historicalBackground": "徳川家康が上洛時の居城として築城した江戸幕府の重要な政治拠点。",
                "highlights": ["二の丸御殿", "唐門"],
                "recommendedVisitTime": "午前",
                "historicalSignificance": "武家政権の権威を示す城郭として、江戸時代の政治史において重要な役割を果たした。",
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
            {
                "spotName": "二条城",
                "checkpoints": ["二の丸御殿の障壁画を観察", "鴬張りの廊下を体験"],
                "historicalContext": "江戸幕府の権威を示す空間構成。",
            },
        ],
    }


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_creates_guide(
    db_session: Session, sample_travel_plan, fake_job_repository
) -> None:
    """前提条件: 旅行計画が存在する。
    実行: 旅行ガイドを生成する。
    検証: DTOと永続化結果が一致する。
    """
    # 前提条件: 旅行計画が存在する。
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        extracted_facts="## スポット別の事実\n\n### 清水寺\n- 778年創建 [出典: 清水寺公式サイト]\n\n### 金閣寺\n- 1397年創建 [出典: 金閣寺公式サイト]",
        structured_data=_structured_guide_payload(),
    )

    # 実行: 旅行ガイドを生成する。
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=fake_job_repository,
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
async def test_generate_travel_guide_use_case_allows_recommended_spots(
    db_session: Session, sample_travel_plan, fake_job_repository
) -> None:
    """前提条件: 旅行計画とおすすめスポットを含む構造化データ。
    実行: 旅行ガイドを生成する。
    検証: 追加スポットと目的地全体の年表イベントが保持される。
    """
    # 前提条件: 旅行計画とおすすめスポットを含む構造化データ。
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        extracted_facts="## スポット別の事実\n\n### 清水寺\n- 778年創建 [出典: 清水寺公式サイト]\n\n### 金閣寺\n- 1397年創建 [出典: 金閣寺公式サイト]\n\n## 追加のおすすめスポット\n\n### 二条城\n- 1603年築城 [出典: 二条城公式サイト]",
        structured_data=_structured_guide_payload_with_recommendations(),
    )

    # 実行: 旅行ガイドを生成する。
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=fake_job_repository,
    )
    dto = await use_case.execute(plan_id=sample_travel_plan.id)

    # 検証: 追加スポットと目的地全体の年表イベントが保持される。
    spot_names = {detail["spotName"] for detail in dto.spot_details}
    assert "二条城" in spot_names
    assert "清水寺" in spot_names
    assert "金閣寺" in spot_names
    assert any("京都" in event["relatedSpots"] for event in dto.timeline)


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_rejects_short_overview(
    db_session: Session, sample_travel_plan, fake_job_repository
) -> None:
    """前提条件: overviewが最小文字数を満たさない構造化データ。
    実行: 旅行ガイドを生成する。
    検証: ValueErrorが発生し、生成ステータスがFAILEDになる。
    """
    # 前提条件: overviewが最小文字数を満たさない構造化データ。
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    short_overview_payload = {
        **_structured_guide_payload(),
        "overview": "短い概要。",
    }
    ai_service = FakeAIService(
        extracted_facts="## スポット別の事実\n\n### 清水寺\n- 778年創建 [出典: 清水寺公式サイト]",
        structured_data=short_overview_payload,
    )

    # 実行 & 検証: ValueErrorが発生する。
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=fake_job_repository,
    )
    with pytest.raises(ValueError, match="Invalid AI response structure"):
        await use_case.execute(plan_id=sample_travel_plan.id)

    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    assert plan.guide_generation_status == GenerationStatus.FAILED


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_rolls_back_new_spots_on_failure(
    db_session: Session, sample_travel_plan, fake_job_repository
) -> None:
    """前提条件: 旅行計画が存在し、AIが新規スポットを追加する。
    実行: 年表に不正な関連スポットを含めてガイド生成を失敗させる。
    検証: 旅行計画に新規スポットが保存されず、生成ステータスがFAILEDになる。
    """
    # 前提条件: 旅行計画が存在する。
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    broken_timeline_payload = {
        **_structured_guide_payload_with_recommendations(),
        "timeline": [
            {
                "year": 1603,
                "event": "不正な関連スポット",
                "significance": "存在しないスポットを参照。",
                "relatedSpots": ["存在しないスポット"],
            }
        ],
    }
    ai_service = FakeAIService(
        extracted_facts="## スポット別の事実\n\n### 清水寺\n- 778年創建 [出典: 清水寺公式サイト]\n\n### 金閣寺\n- 1397年創建 [出典: 金閣寺公式サイト]\n\n## 追加のおすすめスポット\n\n### 二条城\n- 1603年築城 [出典: 二条城公式サイト]",
        structured_data=broken_timeline_payload,
    )

    # 実行 & 検証: ValueErrorが発生する。
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=fake_job_repository,
    )
    with pytest.raises(ValueError, match="relatedSpots contains unknown spot names"):
        await use_case.execute(plan_id=sample_travel_plan.id)

    # 検証: 新規スポットが保存されていない。
    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    spot_names = [spot.name for spot in plan.spots]
    assert spot_names == ["清水寺", "金閣寺"]
    assert plan.guide_generation_status == GenerationStatus.FAILED


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_updates_existing_guide(
    db_session: Session, sample_travel_plan, sample_travel_guide, fake_job_repository
) -> None:
    """前提条件: 既存の旅行ガイドが存在する。
    実行: 旅行ガイドを再生成する。
    検証: 既存ガイドが更新される。
    """
    # 前提条件: 既存の旅行ガイドが存在する。
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        extracted_facts="## スポット別の事実\n\n### 清水寺\n- 778年創建（再生成） [出典: 清水寺公式サイト]",
        structured_data=_structured_guide_payload(),
    )

    # 実行: 旅行ガイドを再生成する。
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=fake_job_repository,
    )
    dto = await use_case.execute(plan_id=sample_travel_plan.id)

    # 検証: 既存ガイドが更新される。
    assert dto.id == sample_travel_guide.id
    assert dto.overview == _structured_guide_payload()["overview"]


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_plan_not_found(db_session: Session, fake_job_repository) -> None:
    """前提条件: 存在しない旅行計画ID。
    実行: 旅行ガイドを生成する。
    検証: TravelPlanNotFoundErrorが発生する。
    """
    # 前提条件: 存在しない旅行計画ID。
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        extracted_facts="## スポット別の事実\n\n### 清水寺\n- 778年創建 [出典: 清水寺公式サイト]",
        structured_data=_structured_guide_payload(),
    )

    # 実行 & 検証: TravelPlanNotFoundErrorが発生する。
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=fake_job_repository,
    )
    with pytest.raises(TravelPlanNotFoundError):
        await use_case.execute(plan_id="non-existent-id")


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_fails_when_job_registration_fails(
    db_session: Session, sample_travel_plan, failing_job_repository
) -> None:
    """前提条件: ジョブ登録が失敗する。
    実行: 旅行ガイドを生成する。
    検証: 例外が送出され、生成ステータスがFAILEDになる。
    """
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        extracted_facts="## スポット別の事実\n\n### 清水寺\n- 778年創建 [出典: 清水寺公式サイト]",
        structured_data=_structured_guide_payload(),
    )

    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=failing_job_repository,
    )

    with pytest.raises(ValueError, match="job registration failed"):
        await use_case.execute(plan_id=sample_travel_plan.id)

    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    assert plan.guide_generation_status == GenerationStatus.FAILED
    assert guide_repository.find_by_plan_id(sample_travel_plan.id) is None


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_rolls_back_existing_guide_update_when_job_registration_fails(
    db_session: Session, sample_travel_plan, sample_travel_guide, failing_job_repository
) -> None:
    """前提条件: 既存ガイドがあり、ジョブ登録が失敗する。
    実行: 旅行ガイドを再生成する。
    検証: 既存ガイド更新とスポット追加がロールバックされ、生成ステータスのみFAILEDになる。
    """
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        extracted_facts="## スポット別の事実\n\n### 清水寺\n- 778年創建 [出典: 清水寺公式サイト]",
        structured_data=_structured_guide_payload_with_recommendations(),
    )

    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=failing_job_repository,
    )

    with pytest.raises(ValueError, match="job registration failed"):
        await use_case.execute(plan_id=sample_travel_plan.id)

    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    assert plan.guide_generation_status == GenerationStatus.FAILED
    assert [spot.name for spot in plan.spots] == ["清水寺", "金閣寺"]

    rolled_back_guide = guide_repository.find_by_plan_id(sample_travel_plan.id)
    assert rolled_back_guide is not None
    assert rolled_back_guide.id == sample_travel_guide.id
    assert rolled_back_guide.overview == "京都の歴史的寺院を巡る旅"
    assert len(rolled_back_guide.spot_details) == 1
    assert rolled_back_guide.spot_details[0].spot_name == "清水寺"


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_rolls_back_new_spots_when_job_registration_fails(
    db_session: Session, sample_travel_plan, failing_job_repository
) -> None:
    """前提条件: ジョブ登録が失敗し、AI応答に新規スポットが含まれる。
    実行: 旅行ガイドを生成する。
    検証: 新規スポットと旅行ガイドがロールバックされ、生成ステータスのみFAILEDになる。
    """
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        extracted_facts="## スポット別の事実\n\n### 清水寺\n- 778年創建 [出典: 清水寺公式サイト]",
        structured_data={
            "overview": "京都の代表的な寺院と城郭を巡り、宗教と政治の歴史を比較しながら学ぶ旅行ガイドです。清水寺と金閣寺に加えて二条城を取り上げ、時代ごとの建築様式や権力構造の変遷を現地で確認できるように構成しています。各スポットの背景、見どころ、学習観点を明確に示し、体験を通じて歴史理解を深める内容です。",
            "timeline": [
                {
                    "year": 778,
                    "event": "清水寺創建",
                    "significance": "平安初期の信仰文化の形成",
                    "relatedSpots": ["清水寺"],
                },
                {
                    "year": 1397,
                    "event": "金閣寺建立",
                    "significance": "室町文化の象徴",
                    "relatedSpots": ["金閣寺"],
                },
                {
                    "year": 1603,
                    "event": "二条城が徳川政権の拠点として整備",
                    "significance": "江戸幕府の統治体制を示す重要拠点",
                    "relatedSpots": ["二条城"],
                },
            ],
            "spotDetails": [
                {
                    "spotName": "清水寺",
                    "historicalBackground": "奈良時代末期に創建された寺院で、京都東山の信仰拠点として発展した。",
                    "highlights": ["清水の舞台", "音羽の滝"],
                    "recommendedVisitTime": "午前",
                    "historicalSignificance": "庶民信仰と観音信仰の広がりを示す。",
                },
                {
                    "spotName": "金閣寺",
                    "historicalBackground": "足利義満の別荘を前身とし、北山文化を代表する寺院として知られる。",
                    "highlights": ["舎利殿", "鏡湖池"],
                    "recommendedVisitTime": "午後",
                    "historicalSignificance": "室町期の権威と美意識を体現する。",
                },
                {
                    "spotName": "二条城",
                    "historicalBackground": "徳川家康が築城し、将軍権威の象徴として機能した城郭。",
                    "highlights": ["二の丸御殿", "唐門"],
                    "recommendedVisitTime": "午後",
                    "historicalSignificance": "武家政権の政治運営を理解する重要資料。",
                },
            ],
            "checkpoints": [
                {
                    "spotName": "清水寺",
                    "checkpoints": ["舞台構造を観察する"],
                    "historicalContext": "信仰と景観が結びついた寺院建築。",
                },
                {
                    "spotName": "金閣寺",
                    "checkpoints": ["庭園と舎利殿の関係を確認する"],
                    "historicalContext": "室町文化の美的価値観を反映した空間。",
                },
                {
                    "spotName": "二条城",
                    "checkpoints": ["二の丸御殿の意匠を確認する"],
                    "historicalContext": "江戸幕府の権威表象としての建築。",
                },
            ],
        },
    )

    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=failing_job_repository,
    )

    with pytest.raises(ValueError, match="job registration failed"):
        await use_case.execute(plan_id=sample_travel_plan.id)

    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    assert plan.guide_generation_status == GenerationStatus.FAILED
    assert [spot.name for spot in plan.spots] == ["清水寺", "金閣寺"]
    assert guide_repository.find_by_plan_id(sample_travel_plan.id) is None


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_rejects_duplicate_spot_names(
    db_session: Session, fake_job_repository
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
        status="planning",
    )
    duplicate_plan.spots = [
        TravelPlanSpotModel(
            id="spot-dup-001",
            name="清水寺",
            description="重複テスト用",
            user_notes="1回目",
            sort_order=0,
        ),
        TravelPlanSpotModel(
            id="spot-dup-002",
            name="清水寺",
            description="重複テスト用",
            user_notes="2回目",
            sort_order=1,
        ),
    ]
    db_session.add(duplicate_plan)
    db_session.commit()
    db_session.refresh(duplicate_plan)

    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        extracted_facts="## スポット別の事実\n\n### 清水寺\n- 重複スポットの事実 [出典: テスト]",
        structured_data=_structured_guide_payload(),
    )

    # 実行 & 検証: ValueErrorが発生する。
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=fake_job_repository,
    )
    with pytest.raises(ValueError):
        await use_case.execute(plan_id=duplicate_plan.id)


@pytest.mark.asyncio
async def test_generate_travel_guide_use_case_rejects_non_dict_structured_response(
    db_session: Session, sample_travel_plan, fake_job_repository
) -> None:
    """前提条件: AIサービスが辞書以外の構造化データを返す。
    実行: 旅行ガイドを生成する。
    検証: ValueErrorが発生する。
    """
    # 前提条件: AIサービスが辞書以外の構造化データを返す。
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        extracted_facts="## スポット別の事実\n\n### 清水寺\n- 778年創建 [出典: 清水寺公式サイト]",
        structured_data=[],
    )

    # 実行 & 検証: ValueErrorが発生する。
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=fake_job_repository,
    )
    with pytest.raises(ValueError):
        await use_case.execute(plan_id=sample_travel_plan.id)

    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    assert plan.guide_generation_status == GenerationStatus.FAILED


@pytest.mark.asyncio
async def test_generate_travel_guide_retries_on_evaluation_failure(
    db_session: Session, sample_travel_plan, fake_job_repository
) -> None:
    """前提条件: 初回生成が評価に失敗し、再生成で成功する。
    実行: 旅行ガイドを生成する。
    検証: 再生成が実行され、最終的に成功する。
    """
    # 前提条件: 初回は評価失敗、2回目は成功するデータ
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)

    # 初回: 出典なし、歴史的対比なし
    first_payload = {
        "overview": "京都の代表的な寺院を巡る旅行ガイドです。",
        "timeline": [
            {
                "year": 778,
                "event": "清水寺創建",
                "significance": "奈良時代から続く歴史的寺院の始まり。",
                "relatedSpots": ["清水寺"],
            },
        ],
        "spotDetails": [
            {
                "spotName": "清水寺",
                "historicalBackground": "奈良時代末期に創建された古刹。",
                "highlights": ["清水の舞台"],
                "recommendedVisitTime": "早朝",
                "historicalSignificance": "平安京遷都以前の歴史を持つ。",
            },
            {
                "spotName": "金閣寺",
                "historicalBackground": "足利義満の別荘として建立された寺院。",
                "highlights": ["金箔の舎利殿"],
                "recommendedVisitTime": "午後",
                "historicalSignificance": "室町文化の象徴として知られる重要な建築物。",
            },
        ],
        "checkpoints": [
            {
                "spotName": "清水寺",
                "checkpoints": ["清水の舞台の高さを確認"],
                "historicalContext": "断崖に建つ舞台は江戸時代の信仰文化を示す。",
            },
            {
                "spotName": "金閣寺",
                "checkpoints": ["金箔装飾の意味を学ぶ"],
                "historicalContext": "将軍文化が色濃く反映された空間構成。",
            },
        ],
    }

    # 2回目: 出典あり、歴史的対比あり
    second_payload = {
        "overview": "京都の代表的な寺院を巡る旅行ガイドです。同時期のヨーロッパではルネサンスが始まっており、世界的な文化の転換期でした。清水寺と金閣寺を訪問し、それぞれの時代背景と文化的意義を学びます。奈良時代から室町時代にかけての日本の歴史を体感できる貴重な機会となります。",
        "timeline": [
            {
                "year": 778,
                "event": "清水寺創建",
                "significance": "奈良時代から続く歴史的寺院の始まり。",
                "relatedSpots": ["清水寺"],
            },
        ],
        "spotDetails": [
            {
                "spotName": "清水寺",
                "historicalBackground": "『京都の歴史』によると、奈良時代末期に創建された古刹。",
                "highlights": ["清水の舞台"],
                "recommendedVisitTime": "早朝",
                "historicalSignificance": "平安京遷都以前の歴史を持つ。",
            },
            {
                "spotName": "金閣寺",
                "historicalBackground": "公式サイトによると、足利義満の別荘として建立された寺院。",
                "highlights": ["金箔の舎利殿"],
                "recommendedVisitTime": "午後",
                "historicalSignificance": "室町文化の象徴として知られる重要な建築物。",
            },
        ],
        "checkpoints": [
            {
                "spotName": "清水寺",
                "checkpoints": ["清水の舞台の高さを確認"],
                "historicalContext": "断崖に建つ舞台は江戸時代の信仰文化を示す。",
            },
            {
                "spotName": "金閣寺",
                "checkpoints": ["金箔装飾の意味を学ぶ"],
                "historicalContext": "将軍文化が色濃く反映された空間構成。",
            },
        ],
    }

    ai_service = FakeAIService(
        extracted_facts="京都の歴史情報を検索結果から取得。",
        structured_data=[first_payload, second_payload],
        evaluation_data=[
            # 初回評価: 不合格
            {
                "spotEvaluations": [
                    {"spotName": "清水寺", "hasCitation": False, "citationExample": ""},
                    {"spotName": "金閣寺", "hasCitation": False, "citationExample": ""},
                ],
                "hasHistoricalComparison": False,
                "historicalComparisonExample": "",
                "allSpotsIncluded": True,
                "missingSpots": [],
            },
            # 2回目評価: 合格
            {
                "spotEvaluations": [
                    {
                        "spotName": "清水寺",
                        "hasCitation": True,
                        "citationExample": "『京都の歴史』",
                    },
                    {
                        "spotName": "金閣寺",
                        "hasCitation": True,
                        "citationExample": "公式サイト",
                    },
                ],
                "hasHistoricalComparison": True,
                "historicalComparisonExample": "同時期のヨーロッパではルネサンス",
                "allSpotsIncluded": True,
                "missingSpots": [],
            },
        ],
    )

    # 実行: 旅行ガイドを生成する
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=fake_job_repository,
    )
    dto = await use_case.execute(plan_id=sample_travel_plan.id)

    # 検証: 2回目のデータが使用されている
    assert "ヨーロッパ" in dto.overview
    assert "『京都の歴史』" in dto.spot_details[0]["historicalBackground"]
    assert ai_service.call_count == 2

    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    assert plan.guide_generation_status == GenerationStatus.SUCCEEDED


@pytest.mark.asyncio
async def test_generate_travel_guide_proceeds_after_retry_failure(
    db_session: Session, sample_travel_plan, fake_job_repository
) -> None:
    """前提条件: 初回も再生成も評価に失敗する。
    実行: 旅行ガイドを生成する。
    検証: 警告ログを出力しつつ処理を続行する。
    """
    # 前提条件: 両方とも評価失敗するデータ
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)

    # 出典なし、歴史的対比なし（両方とも同じ）
    payload = {
        "overview": "京都の代表的な寺院を巡る旅行ガイドです。清水寺と金閣寺を訪問し、それぞれの歴史的背景を学びます。奈良時代から室町時代にかけての日本の文化と建築の変遷を体感できる貴重な機会となります。各寺院の特徴や見どころを詳しく解説します。",
        "timeline": [
            {
                "year": 778,
                "event": "清水寺創建",
                "significance": "奈良時代から続く歴史的寺院の始まり。",
                "relatedSpots": ["清水寺"],
            },
        ],
        "spotDetails": [
            {
                "spotName": "清水寺",
                "historicalBackground": "奈良時代末期に創建された古刹。",
                "highlights": ["清水の舞台"],
                "recommendedVisitTime": "早朝",
                "historicalSignificance": "平安京遷都以前の歴史を持つ。",
            },
            {
                "spotName": "金閣寺",
                "historicalBackground": "足利義満の別荘として建立された寺院。",
                "highlights": ["金箔の舎利殿"],
                "recommendedVisitTime": "午後",
                "historicalSignificance": "室町文化の象徴として知られる重要な建築物。",
            },
        ],
        "checkpoints": [
            {
                "spotName": "清水寺",
                "checkpoints": ["清水の舞台の高さを確認"],
                "historicalContext": "断崖に建つ舞台は江戸時代の信仰文化を示す。",
            },
            {
                "spotName": "金閣寺",
                "checkpoints": ["金箔装飾の意味を学ぶ"],
                "historicalContext": "将軍文化が色濃く反映された空間構成。",
            },
        ],
    }

    ai_service = FakeAIService(
        extracted_facts="京都の歴史情報を検索結果から取得。",
        structured_data=payload,
        evaluation_data={
            # 両方とも不合格
            "spotEvaluations": [
                {"spotName": "清水寺", "hasCitation": False, "citationExample": ""},
                {"spotName": "金閣寺", "hasCitation": False, "citationExample": ""},
            ],
            "hasHistoricalComparison": False,
            "historicalComparisonExample": "",
            "allSpotsIncluded": True,
            "missingSpots": [],
        },
    )

    # 実行: 旅行ガイドを生成する（エラーにならず処理が続行される）
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=fake_job_repository,
    )
    dto = await use_case.execute(plan_id=sample_travel_plan.id)

    # 検証: 処理は成功するが、評価は失敗している
    assert dto.plan_id == sample_travel_plan.id
    assert ai_service.call_count == 2  # 初回 + 再生成

    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    assert plan.guide_generation_status == GenerationStatus.SUCCEEDED


@pytest.mark.asyncio
async def test_generate_travel_guide_enqueues_tasks_in_cloud_tasks_mode(
    db_session: Session, sample_travel_plan, fake_job_repository, fake_task_dispatcher, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("IMAGE_EXECUTION_MODE", "cloud_tasks")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setenv("CLOUD_TASKS_LOCATION", "asia-northeast1")
    monkeypatch.setenv("CLOUD_TASKS_QUEUE_NAME", "spot-image-generation")
    monkeypatch.setenv("CLOUD_TASKS_TARGET_URL", "https://example.com/api/v1/internal/tasks/spot-image")
    monkeypatch.setenv("CLOUD_TASKS_SERVICE_ACCOUNT_EMAIL", "worker@example.com")
    from app.config.settings import get_settings

    get_settings.cache_clear()

    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        extracted_facts="京都の歴史情報。",
        structured_data=_structured_guide_payload(),
    )
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=fake_job_repository,
        task_dispatcher=fake_task_dispatcher,
    )
    await use_case.execute(plan_id=sample_travel_plan.id)

    assert len(fake_task_dispatcher.enqueued) == 2
    assert fake_task_dispatcher.enqueued[0][0] == sample_travel_plan.id


@pytest.mark.asyncio
async def test_generate_travel_guide_skips_enqueue_in_local_worker_mode(
    db_session: Session, sample_travel_plan, fake_job_repository, fake_task_dispatcher, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("IMAGE_EXECUTION_MODE", "local_worker")
    from app.config.settings import get_settings

    get_settings.cache_clear()

    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)
    ai_service = FakeAIService(
        extracted_facts="京都の歴史情報。",
        structured_data=_structured_guide_payload(),
    )
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=fake_job_repository,
        task_dispatcher=fake_task_dispatcher,
    )
    await use_case.execute(plan_id=sample_travel_plan.id)

    assert fake_task_dispatcher.enqueued == []
