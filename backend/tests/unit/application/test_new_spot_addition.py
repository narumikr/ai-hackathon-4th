"""新規スポット追加機能のテスト"""

from __future__ import annotations

from typing import Any

import pytest
from sqlalchemy.orm import Session

from app.application.ports.ai_service import IAIService
from app.application.use_cases.generate_travel_guide import GenerateTravelGuideUseCase
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
        tools: list[str] | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        raise NotImplementedError

    async def analyze_image_structured(
        self,
        prompt: str,
        image_uri: str,
        response_schema: dict[str, Any],
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
        response_schema: dict[str, Any],
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        return self.structured_data


@pytest.mark.asyncio
async def test_new_spot_addition(db_session: Session, sample_travel_plan) -> None:
    """新規スポットが追加されることを確認する"""
    # 前提条件: 旅行計画には清水寺と金閣寺のみが含まれる
    plan_repository = TravelPlanRepository(db_session)
    guide_repository = TravelGuideRepository(db_session)

    # AIが二条城を追加したspotDetailsを返す
    structured_data = {
        "overview": "京都の主要寺院に加えて城郭も巡る旅行ガイドです。寺院文化と武家文化の両面から京都の歴史を俯瞰できるように構成し、各スポットの関係性と時代背景を示しながら、学びのポイントを丁寧に整理しています。宗教施設と城郭の役割の違いを比較し、旅行のハイライトと体験価値が伝わる内容にしています。",
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
            {
                "year": 1603,
                "event": "二条城の築城",
                "significance": "江戸幕府の権威を示す城郭の建立。",
                "relatedSpots": ["二条城"],
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
            {
                "spotName": "二条城",
                "historicalBackground": "徳川家康が上洛時の居城として築城。",
                "highlights": ["二の丸御殿", "唐門"],
                "recommendedVisitTime": "午前",
                "historicalSignificance": "武家政権の権威を示す城郭。",
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

    ai_service = FakeAIService(
        historical_info="京都全体とおすすめスポットの歴史情報。",
        structured_data=structured_data,
    )

    # 実行: 旅行ガイドを生成する
    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
    )
    await use_case.execute(plan_id=sample_travel_plan.id)

    # 検証: 旅行計画に二条城が追加されている
    plan = plan_repository.find_by_id(sample_travel_plan.id)
    assert plan is not None
    assert len(plan.spots) == 3
    spot_names = [spot.name for spot in plan.spots]
    assert "清水寺" in spot_names
    assert "金閣寺" in spot_names
    assert "二条城" in spot_names

    # 順序の確認: 既存スポット(清水寺、金閣寺)の後に新規スポット(二条城)が追加される
    assert spot_names[0] == "清水寺"
    assert spot_names[1] == "金閣寺"
    assert spot_names[2] == "二条城"

    # 新規スポットのプロパティ確認
    nijo_castle = plan.spots[2]
    assert nijo_castle.name == "二条城"
    assert nijo_castle.description is None
    assert nijo_castle.user_notes is None
    assert nijo_castle.id is not None
