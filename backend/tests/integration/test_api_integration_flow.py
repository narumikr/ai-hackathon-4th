"""API統合テスト"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, TypeVar

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.application.ports.ai_service import IAIService
from app.application.ports.storage_service import IStorageService
from app.infrastructure.persistence.database import get_db
from app.interfaces.api.dependencies import (
    get_ai_service_dependency,
    get_storage_service_dependency,
)
from main import app

if TYPE_CHECKING:
    from app.infrastructure.ai.schemas.base import GeminiResponseSchema

T = TypeVar("T", bound="GeminiResponseSchema")


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
        tools: list[str] | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        return (
            "清水寺は平安時代から続く寺院で、清水の舞台が象徴的な建築として知られる。"
            "出典: 清水寺公式サイト https://www.kiyomizudera.or.jp/history/ 。"
        )

    async def analyze_image_structured(
        self,
        prompt: str,
        image_uri: str,
        response_schema: type[T],
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict:
        return {
            "detectedSpots": ["清水寺"],
            "historicalElements": ["清水の舞台"],
            "landmarks": ["清水寺本堂"],
            "confidence": 0.9,
        }

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
        """旅行ガイドの評価（スタブ：常に合格を返す）"""
        return {
            "spotEvaluations": [
                {
                    "spotName": "清水寺",
                    "hasCitation": True,
                    "citationExample": "清水寺公式サイト",
                },
                {
                    "spotName": "金閣寺",
                    "hasCitation": True,
                    "citationExample": "金閣寺公式サイト",
                },
            ],
            "hasHistoricalComparison": True,
            "historicalComparisonExample": "同時期のヨーロッパでは...",
        }

    async def generate_structured_data(
        self,
        prompt: str,
        response_schema: type[T],
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict:
        # Pydanticモデルからスキーマ名を取得して判定
        schema_name = response_schema.__name__ if hasattr(response_schema, "__name__") else ""
        if "Reflection" in schema_name or "travelSummary" in str(response_schema):
            return {
                "travelSummary": "京都の歴史を再発見できた旅だった。",
                "spotReflections": [
                    {"spotName": "清水寺", "reflection": "舞台の眺めが印象的だった。"}
                ],
                "nextTripSuggestions": ["奈良の寺社巡り"],
            }
        return {
            "overview": "京都の歴史を学ぶ旅行ガイドです。清水寺を中心に、地域の成り立ちや信仰文化の背景を丁寧にたどり、観光体験の学びが深まるよう構成しています。時代ごとの変化と見どころを整理し、旅のテーマとハイライトが伝わる内容にしています。",
            "timeline": [
                {
                    "year": 778,
                    "event": "清水寺創建",
                    "significance": "奈良時代末期の創建から続く歴史的寺院の始まり。",
                    "relatedSpots": ["清水寺"],
                }
            ],
            "spotDetails": [
                {
                    "spotName": "清水寺",
                    "historicalBackground": "平安京遷都以前からの歴史を持つ古刹で、長い歴史を今に伝える。",
                    "highlights": ["清水の舞台", "音羽の滝"],
                    "recommendedVisitTime": "早朝",
                    "historicalSignificance": "信仰と文化の中心地として、京都の歴史において重要な役割を果たした。",
                }
            ],
            "checkpoints": [
                {
                    "spotName": "清水寺",
                    "checkpoints": ["清水の舞台の構造を確認"],
                    "historicalContext": "断崖の上に建つ懸造り",
                }
            ],
        }


class StubStorageService(IStorageService):
    """ストレージサービスのスタブ"""

    async def upload_file(
        self,
        file_data: bytes,
        destination: str,
        content_type: str,
    ) -> str:
        return f"http://example.com/{destination}"

    async def get_file_url(self, file_path: str) -> str:
        return f"http://example.com/{file_path}"

    async def delete_file(self, file_path: str) -> bool:
        return True

    async def file_exists(self, file_path: str) -> bool:
        return True


@pytest.fixture
def api_client(db_session: Session):
    """テスト用DBセッションと依存性を注入したTestClientを返す"""

    def override_get_db():
        session_factory = sessionmaker(bind=db_session.get_bind())
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    async def override_get_ai_service():
        return StubAIService()

    async def override_get_storage_service():
        return StubStorageService()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_ai_service_dependency] = override_get_ai_service
    app.dependency_overrides[get_storage_service_dependency] = override_get_storage_service
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def _wait_for_generation(
    api_client: TestClient,
    plan_id: str,
    field: str,
    *,
    timeout_seconds: float = 5.0,
    interval_seconds: float = 0.05,
) -> dict:
    """指定した生成ステータスが完了状態になるまでポーリングする。

    Args:
        api_client: テスト対象APIへのリクエストに使うTestClient。
        plan_id: 対象となる旅行プランID。
        field: レスポンスJSON内の生成ステータスフィールド名。
        timeout_seconds: 最大待機時間（秒）。
        interval_seconds: ポーリング間隔（秒）。

    Returns:
        dict: 最後に取得したレスポンスJSON。
    """
    deadline = time.monotonic() + timeout_seconds
    status_data = api_client.get(f"/api/v1/travel-plans/{plan_id}").json()
    while time.monotonic() < deadline:
        if status_data[field] == "succeeded":
            break
        if status_data[field] == "failed":
            break
        time.sleep(interval_seconds)
        status_data = api_client.get(f"/api/v1/travel-plans/{plan_id}").json()
    if status_data[field] not in ("succeeded", "failed"):
        pytest.fail(
            "タイムアウトしました: "
            f"plan_id={plan_id}, field={field}, "
            f"last_status={status_data.get(field)!r}"
        )
    return status_data


def test_api_end_to_end_flow(api_client: TestClient):
    """前提条件: テスト用DBセッションとスタブ依存
    実行: 旅行計画作成 -> 旅行ガイド生成 -> 画像アップロード -> 振り返り生成
    検証: ステータスコードと生成結果が正しい
    """
    # 前提条件: テスト用DBセッションとスタブ依存

    # 実行: 旅行計画作成
    create_response = api_client.post(
        "/api/v1/travel-plans",
        json={
            "userId": "test_user_010",
            "title": "京都歴史探訪",
            "destination": "京都",
            "spots": [
                {
                    "id": "spot-010",
                    "name": "清水寺",
                    "description": "京都を代表する寺院",
                    "userNotes": "早朝訪問予定",
                }
            ],
        },
    )

    # 検証: ステータスコード201、作成結果
    assert create_response.status_code == 201
    plan_data = create_response.json()
    plan_id = plan_data["id"]

    # 実行: 旅行ガイド生成
    guide_response = api_client.post("/api/v1/travel-guides", json={"planId": plan_id})

    # 検証: ステータスコード202、生成中ステータス
    assert guide_response.status_code == 202
    assert guide_response.json()["guideGenerationStatus"] == "processing"

    # 検証: ガイド生成完了
    guide_status = _wait_for_generation(api_client, plan_id, "guideGenerationStatus")
    assert guide_status["guideGenerationStatus"] == "succeeded"
    assert guide_status["guide"] is not None
    assert guide_status["guide"]["overview"]
    assert guide_status["guide"]["timeline"]
    assert guide_status["guide"]["spotDetails"]

    # 実行: 画像アップロード
    upload_response = api_client.post(
        "/api/v1/spot-reflections",
        data={
            "planId": plan_id,
            "userId": "test_user_010",
            "spotId": "spot-010",
            "spotNote": "清水寺の舞台が印象的だった",
        },
        files=[("files", ("kyoto.jpg", b"dummy-bytes", "image/jpeg"))],
    )

    # 検証: ステータスコード204
    assert upload_response.status_code == 204

    # 実行: 振り返り生成
    reflection_response = api_client.post(
        "/api/v1/reflections",
        json={"planId": plan_id, "userId": "test_user_010"},
    )

    # 検証: ステータスコード204
    assert reflection_response.status_code == 204

    # 検証: 振り返り生成完了
    reflection_status = _wait_for_generation(api_client, plan_id, "reflectionGenerationStatus")
    assert reflection_status["reflectionGenerationStatus"] == "succeeded"
    assert reflection_status["reflection"] is not None
    assert reflection_status["reflection"]["photos"]
    assert reflection_status["reflection"]["spotNotes"]["spot-010"]
    first_photo = reflection_status["reflection"]["photos"][0]
    assert isinstance(first_photo["analysis"], str)
    assert first_photo["analysis"].strip()


def test_api_error_handling_flow(api_client: TestClient):
    """前提条件: テスト用DBセッションとスタブ依存
    実行: 不正リクエストの送信
    検証: ステータスコードが正しい
    """
    # 前提条件: テスト用DBセッションとスタブ依存

    # 実行: 旅行計画作成
    create_response = api_client.post(
        "/api/v1/travel-plans",
        json={
            "userId": "test_user_011",
            "title": "奈良歴史巡り",
            "destination": "奈良",
            "spots": [
                {
                    "id": "spot-011",
                    "name": "清水寺",
                    "description": "京都を代表する寺院",
                    "userNotes": "午後に訪問",
                }
            ],
        },
    )

    assert create_response.status_code == 201
    plan_id = create_response.json()["id"]

    # 実行: 誤ったユーザーIDで画像アップロード
    wrong_user_response = api_client.post(
        "/api/v1/spot-reflections",
        data={
            "planId": plan_id,
            "userId": "different_user",
            "spotId": "spot-011",
            "spotNote": "ユーザー違いのテスト",
        },
        files=[("files", ("nara.jpg", b"dummy-bytes", "image/jpeg"))],
    )

    # 検証: ステータスコード400
    assert wrong_user_response.status_code == 400

    # 実行: 存在しないスポットIDで画像アップロード
    wrong_spot_response = api_client.post(
        "/api/v1/spot-reflections",
        data={
            "planId": plan_id,
            "userId": "test_user_011",
            "spotId": "spot-unknown",
            "spotNote": "スポット違いのテスト",
        },
        files=[("files", ("nara.jpg", b"dummy-bytes", "image/jpeg"))],
    )

    # 検証: ステータスコード400
    assert wrong_spot_response.status_code == 400

    # 実行: 旅行ガイド生成
    guide_response = api_client.post("/api/v1/travel-guides", json={"planId": plan_id})
    assert guide_response.status_code == 202

    guide_status = _wait_for_generation(api_client, plan_id, "guideGenerationStatus")
    assert guide_status["guideGenerationStatus"] == "succeeded"

    # 実行: 画像未登録で振り返り生成
    reflection_response = api_client.post(
        "/api/v1/reflections",
        json={"planId": plan_id, "userId": "test_user_011"},
    )

    # 検証: ステータスコード409
    assert reflection_response.status_code == 409
