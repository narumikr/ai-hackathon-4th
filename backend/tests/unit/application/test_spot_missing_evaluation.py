"""スポット漏れ評価のテスト"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import pytest
from sqlalchemy.orm import Session

from app.application.ports.ai_service import IAIService
from app.application.use_cases.generate_travel_guide import GenerateTravelGuideUseCase
from app.domain.travel_plan.value_objects import GenerationStatus
from app.infrastructure.repositories.travel_guide_repository import TravelGuideRepository
from app.infrastructure.repositories.travel_plan_repository import TravelPlanRepository

if TYPE_CHECKING:
    from app.infrastructure.ai.schemas.base import GeminiResponseSchema

T = TypeVar("T", bound="GeminiResponseSchema")


class FakeAIServiceWithMissingSpot(IAIService):
    """スポット漏れをシミュレートするテスト用AIサービス"""

    def __init__(
        self,
        historical_info: str,
        first_generation: dict[str, Any],
        second_generation: dict[str, Any],
    ) -> None:
        self.historical_info = historical_info
        self.first_generation = first_generation
        self.second_generation = second_generation
        self.call_count = 0

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

    async def generate_image_prompt(
        self,
        spot_name: str,
        historical_background: str | None = None,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        raise NotImplementedError

    async def generate_image(
        self,
        prompt: str,
        *,
        aspect_ratio: str = "16:9",
        timeout: int = 60,
    ) -> bytes:
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
            # 現在の生成データに基づいて評価結果を返す
            # call_count == 1の時は初回生成後なのでfirst_generationを評価
            # call_count == 2の時は再生成後なのでsecond_generationを評価
            current_data = self.first_generation if self.call_count <= 1 else self.second_generation
            spot_details = current_data.get("spotDetails", [])
            spot_names = {spot["spotName"] for spot in spot_details}

            # プロンプトから必須スポットを抽出（簡易実装）
            required_spots = {"清水寺", "金閣寺"}
            missing = sorted(required_spots - spot_names)

            return {
                "spotEvaluations": [
                    {
                        "spotName": spot["spotName"],
                        "hasCitation": True,
                        "citationExample": "テスト用出典",
                    }
                    for spot in spot_details
                ],
                "hasHistoricalComparison": True,
                "historicalComparisonExample": "テスト用歴史的対比",
                "allSpotsIncluded": len(missing) == 0,
                "missingSpots": missing,
            }

        # 通常の生成
        self.call_count += 1
        if self.call_count == 1:
            return self.first_generation
        return self.second_generation

class FakeSpotImageJobRepository:
    """テスト用のスポット画像生成ジョブリポジトリ"""

    def create_jobs(
        self,
        plan_id: str,
        spot_names: list[str],
        *,
        max_attempts: int = 3,
        commit: bool = True,
    ) -> int:
        return len(spot_names)

    def fetch_and_lock_jobs(self, limit: int, *, worker_id: str):
        raise NotImplementedError

    def mark_succeeded(self, job_id: str) -> None:
        raise NotImplementedError

    def mark_failed(self, job_id: str, *, error_message: str) -> None:
        raise NotImplementedError





@pytest.mark.asyncio
async def test_retries_when_spot_is_missing(db_session: Session, sample_travel_plan) -> None:
    """前提条件: 初回生成でスポットが漏れている。
    実行: 旅行ガイドを生成する。
    検証: 再生成が実行され、全スポットが含まれる。
    """
    # 前提条件: 初回は金閣寺が漏れている、2回目は全て含まれる
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)

    # 初回: 清水寺のみ（金閣寺が漏れている）
    first_generation = {
        "overview": "京都の代表的な寺院を巡る旅行ガイドです。同時期のヨーロッパではルネサンスが始まっており、世界的な文化の転換期でした。清水寺を訪問し、奈良時代から続く歴史を体感できる貴重な機会となります。断崖に建つ清水の舞台からの眺望は圧巻で、音羽の滝の清水は古来より信仰の対象とされてきました。",
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
        ],
        "checkpoints": [
            {
                "spotName": "清水寺",
                "checkpoints": ["清水の舞台の高さを確認"],
                "historicalContext": "断崖に建つ舞台は江戸時代の信仰文化を示す。",
            },
        ],
    }

    # 2回目: 清水寺と金閣寺の両方
    second_generation = {
        "overview": "京都の代表的な寺院を巡る旅行ガイドです。同時期のヨーロッパではルネサンスが始まっており、世界的な文化の転換期でした。清水寺と金閣寺を訪問し、奈良時代から室町時代にかけての日本の歴史を体感できる貴重な機会となります。清水寺の断崖に建つ舞台と金閣寺の金箔に輝く舎利殿は、それぞれの時代の文化と技術の粋を集めた建築物です。",
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

    ai_service = FakeAIServiceWithMissingSpot(
        historical_info="京都の歴史情報を検索結果から取得。",
        first_generation=first_generation,
        second_generation=second_generation,
    )

    # 実行: 旅行ガイドを生成する
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
        job_repository=FakeSpotImageJobRepository(),
    )
    dto = await use_case.execute(plan_id=sample_travel_plan.id)

    # 検証: 2回目のデータが使用され、全スポットが含まれている
    assert len(dto.spot_details) == 2
    spot_names = {detail["spotName"] for detail in dto.spot_details}
    assert "清水寺" in spot_names
    assert "金閣寺" in spot_names
    assert ai_service.call_count == 2

    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    assert plan.guide_generation_status == GenerationStatus.SUCCEEDED
