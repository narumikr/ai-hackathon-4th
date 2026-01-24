"""TravelGuide API統合テスト"""

import time

from sqlalchemy.orm import sessionmaker
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.application.ports.ai_service import IAIService
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.models import TravelGuideModel, TravelPlanModel
from app.interfaces.api.dependencies import get_ai_service_dependency
from main import app


class StubAIService(IAIService):
    """AIサービスのスタブ"""

    async def generate_text(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        return "京都の歴史情報の要約"

    async def generate_with_search(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        return "京都の歴史情報（スタブ）"

    async def analyze_image(
        self,
        prompt: str,
        image_uri: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        return "画像分析結果（スタブ）"

    async def generate_structured_data(
        self,
        prompt: str,
        response_schema: dict,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict:
        return {
            "overview": "京都の歴史を学ぶ旅行ガイド",
            "timeline": [
                {
                    "year": 778,
                    "event": "清水寺創建",
                    "significance": "奈良時代末期の創建",
                    "relatedSpots": ["清水寺"],
                },
                {
                    "year": 1397,
                    "event": "金閣寺創建",
                    "significance": "室町幕府の象徴的建築",
                    "relatedSpots": ["金閣寺"],
                },
            ],
            "spotDetails": [
                {
                    "spotName": "清水寺",
                    "historicalBackground": "平安京遷都以前からの歴史を持つ",
                    "highlights": ["清水の舞台", "音羽の滝"],
                    "recommendedVisitTime": "早朝",
                    "historicalSignificance": "信仰と文化の中心地",
                },
                {
                    "spotName": "金閣寺",
                    "historicalBackground": "足利義満の別荘として建立",
                    "highlights": ["金色の舎利殿", "鏡湖池"],
                    "recommendedVisitTime": "午後",
                    "historicalSignificance": "室町文化の象徴",
                },
            ],
            "checkpoints": [
                {
                    "spotName": "清水寺",
                    "checkpoints": ["清水の舞台の構造を確認", "音羽の滝の由来を学ぶ"],
                    "historicalContext": "断崖の上に建つ懸造り",
                },
                {
                    "spotName": "金閣寺",
                    "checkpoints": ["舎利殿の建築様式を観察"],
                    "historicalContext": "北山文化の代表的建築",
                },
            ],
        }


@pytest.fixture
def api_client(db_session: Session):
    """テスト用DBセッションとAIサービスを注入したTestClientを返す"""

    def override_get_db():
        session_factory = sessionmaker(bind=db_session.get_bind())
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    async def override_get_ai_service():
        return StubAIService()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_ai_service_dependency] = override_get_ai_service
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def test_generate_travel_guide(
    api_client: TestClient, db_session: Session, sample_travel_plan: TravelPlanModel
):
    """前提条件: テスト用DBセッションとサンプル計画
    実行: POST /api/v1/travel-guides
    検証: ステータスコード201、ガイド生成とステータス更新
    """
    # 前提条件: テスト用DBセッションとサンプル計画

    # リクエストデータ
    request_data = {"planId": sample_travel_plan.id}

    # 実行: POST /api/v1/travel-guides
    response = api_client.post("/api/v1/travel-guides", json=request_data)

    # 検証: ステータスコード202、生成中ステータスが返る
    assert response.status_code == 202
    data = response.json()
    assert data["id"] == sample_travel_plan.id
    assert data["guideGenerationStatus"] == "processing"

    # 実行: GET /api/v1/travel-plans/{id}
    status_response = api_client.get(
        f"/api/v1/travel-plans/{sample_travel_plan.id}"
    )

    # 検証: ジョブ完了後にガイドが作成される
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["id"] == sample_travel_plan.id

    # 検証: ポーリングで生成完了を確認する
    for _ in range(20):
        if status_data["guideGenerationStatus"] == "succeeded":
            break
        time.sleep(0.01)
        status_data = api_client.get(
            f"/api/v1/travel-plans/{sample_travel_plan.id}"
        ).json()

    assert status_data["guideGenerationStatus"] == "succeeded"

    db_session.expire_all()
    saved_plan = db_session.get(TravelPlanModel, sample_travel_plan.id)
    assert saved_plan is not None
    assert saved_plan.guide_generation_status == "succeeded"

    saved_guide = (
        db_session.query(TravelGuideModel)
        .filter(TravelGuideModel.plan_id == sample_travel_plan.id)
        .first()
    )
    assert saved_guide is not None


def test_generate_travel_guide_plan_not_found(api_client: TestClient):
    """前提条件: 存在しない旅行計画ID
    実行: POST /api/v1/travel-guides
    検証: ステータスコード404
    """
    # 前提条件: 存在しない旅行計画ID

    # リクエストデータ
    request_data = {"planId": "non-existent-plan-id"}

    # 実行: POST /api/v1/travel-guides
    response = api_client.post("/api/v1/travel-guides", json=request_data)

    # 検証: ステータスコード404
    assert response.status_code == 404
