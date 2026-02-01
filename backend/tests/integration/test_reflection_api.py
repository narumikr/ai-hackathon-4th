"""Reflection API統合テスト"""

import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.application.ports.ai_service import IAIService
from app.application.ports.storage_service import IStorageService
from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.models import ReflectionModel, TravelPlanModel
from app.interfaces.api.dependencies import (
    get_ai_service_dependency,
    get_storage_service_dependency,
)
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
        return "振り返りのサマリー（スタブ）"

    async def generate_with_search(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        return "検索結果（スタブ）"

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
            "清水寺の舞台は断崖に張り出した懸造りで知られ、"
            "境内の歴史的景観の中心となっている。"
            "出典: 清水寺公式サイト https://www.kiyomizudera.or.jp/history/ 。"
        )

    async def analyze_image_structured(
        self,
        prompt: str,
        image_uri: str,
        response_schema: dict,
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
            "travelSummary": "京都の歴史を再発見できた旅だった。",
            "spotReflections": [
                {"spotName": "清水寺", "reflection": "舞台の眺めが印象的だった。"},
                {"spotName": "金閣寺", "reflection": "金色の輝きが美しかった。"},
            ],
            "nextTripSuggestions": ["奈良の寺社巡り", "鎌倉の歴史散策"],
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


def test_upload_images(
    api_client: TestClient,
    sample_travel_plan: TravelPlanModel,
):
    """前提条件: サンプル旅行計画
    実行: POST /api/v1/spot-reflections
    検証: ステータスコード204
    """
    data = {
        "planId": sample_travel_plan.id,
        "userId": sample_travel_plan.user_id,
        "spotId": "spot-001",
        "spotNote": "清水寺の舞台が印象的だった",
    }
    files = [
        ("files", ("kyoto.jpg", b"dummy-bytes", "image/jpeg")),
    ]

    response = api_client.post("/api/v1/spot-reflections", data=data, files=files)

    assert response.status_code == 204


def test_upload_images_accepts_empty_spot_note(
    api_client: TestClient,
    db_session: Session,
    sample_travel_plan: TravelPlanModel,
):
    """前提条件: サンプル旅行計画
    実行: spotNoteが空文字のPOST /api/v1/spot-reflections
    検証: ステータスコード204、spot_notesに空文字が保存されない
    """
    data = {
        "planId": sample_travel_plan.id,
        "userId": sample_travel_plan.user_id,
        "spotId": "spot-001",
        "spotNote": "",
    }
    files = [
        ("files", ("kyoto.jpg", b"dummy-bytes", "image/jpeg")),
    ]

    response = api_client.post("/api/v1/spot-reflections", data=data, files=files)

    assert response.status_code == 204

    db_session.expire_all()
    saved_reflection = (
        db_session.query(ReflectionModel)
        .filter(ReflectionModel.plan_id == sample_travel_plan.id)
        .first()
    )
    assert saved_reflection is not None
    assert saved_reflection.spot_notes == {}


def test_upload_images_clears_spot_note_when_empty(
    api_client: TestClient,
    db_session: Session,
    sample_travel_plan: TravelPlanModel,
):
    """前提条件: サンプル旅行計画
    実行: spotNoteを登録後、空文字でPOST /api/v1/spot-reflections
    検証: ステータスコード204、spot_notesから対象スポットのメモが削除される
    """
    initial_data = {
        "planId": sample_travel_plan.id,
        "userId": sample_travel_plan.user_id,
        "spotId": "spot-001",
        "spotNote": "最初のメモ",
    }
    initial_files = [
        ("files", ("kyoto.jpg", b"dummy-bytes", "image/jpeg")),
    ]
    initial_response = api_client.post(
        "/api/v1/spot-reflections", data=initial_data, files=initial_files
    )
    assert initial_response.status_code == 204

    empty_data = {
        "planId": sample_travel_plan.id,
        "userId": sample_travel_plan.user_id,
        "spotId": "spot-001",
        "spotNote": "",
    }
    empty_files = [
        ("files", ("kyoto-2.jpg", b"dummy-bytes", "image/jpeg")),
    ]
    empty_response = api_client.post("/api/v1/spot-reflections", data=empty_data, files=empty_files)
    assert empty_response.status_code == 204

    db_session.expire_all()
    saved_reflection = (
        db_session.query(ReflectionModel)
        .filter(ReflectionModel.plan_id == sample_travel_plan.id)
        .first()
    )
    assert saved_reflection is not None
    assert saved_reflection.spot_notes == {}


def test_create_reflection(
    api_client: TestClient,
    db_session: Session,
    sample_travel_plan: TravelPlanModel,
    sample_travel_guide,
):
    """前提条件: サンプル旅行計画と旅行ガイド
    実行: POST /api/v1/reflections
    検証: ステータスコード204、振り返り生成が完了する
    """
    upload_data = {
        "planId": sample_travel_plan.id,
        "userId": sample_travel_plan.user_id,
        "spotId": "spot-001",
        "spotNote": "清水寺の舞台からの眺めが最高だった",
    }

    files = [("files", ("kiyomizu.jpg", b"dummy-bytes", "image/jpeg"))]
    upload_response = api_client.post("/api/v1/spot-reflections", data=upload_data, files=files)
    assert upload_response.status_code == 204

    response = api_client.post(
        "/api/v1/reflections",
        json={
            "planId": sample_travel_plan.id,
            "userId": sample_travel_plan.user_id,
        },
    )

    assert response.status_code == 204

    status_data = api_client.get(f"/api/v1/travel-plans/{sample_travel_plan.id}").json()

    for _ in range(20):
        if status_data["reflectionGenerationStatus"] == "succeeded":
            break
        time.sleep(0.01)
        status_data = api_client.get(f"/api/v1/travel-plans/{sample_travel_plan.id}").json()

    assert status_data["reflectionGenerationStatus"] == "succeeded"

    db_session.expire_all()
    saved_plan = db_session.get(TravelPlanModel, sample_travel_plan.id)
    assert saved_plan is not None
    assert saved_plan.reflection_generation_status == "succeeded"

    saved_reflection = (
        db_session.query(ReflectionModel)
        .filter(ReflectionModel.plan_id == sample_travel_plan.id)
        .first()
    )
    assert saved_reflection is not None
    assert saved_reflection.spot_notes == {"spot-001": "清水寺の舞台からの眺めが最高だった"}


def test_create_reflection_accepts_empty_user_notes(
    api_client: TestClient,
    db_session: Session,
    sample_travel_plan: TravelPlanModel,
    sample_travel_guide,
):
    """前提条件: サンプル旅行計画と旅行ガイド
    実行: userNotesが空文字のPOST /api/v1/reflections
    検証: ステータスコード204、user_notesがNoneとして扱われる
    """
    upload_data = {
        "planId": sample_travel_plan.id,
        "userId": sample_travel_plan.user_id,
        "spotId": "spot-001",
    }

    files = [("files", ("kiyomizu.jpg", b"dummy-bytes", "image/jpeg"))]
    upload_response = api_client.post("/api/v1/spot-reflections", data=upload_data, files=files)
    assert upload_response.status_code == 204

    response = api_client.post(
        "/api/v1/reflections",
        json={
            "planId": sample_travel_plan.id,
            "userId": sample_travel_plan.user_id,
            "userNotes": "",
        },
    )

    assert response.status_code == 204

    for _ in range(20):
        status_data = api_client.get(f"/api/v1/travel-plans/{sample_travel_plan.id}").json()
        if status_data["reflectionGenerationStatus"] == "succeeded":
            break
        time.sleep(0.01)

    assert status_data["reflectionGenerationStatus"] == "succeeded"

    db_session.expire_all()
    saved_reflection = (
        db_session.query(ReflectionModel)
        .filter(ReflectionModel.plan_id == sample_travel_plan.id)
        .first()
    )
    assert saved_reflection is not None
    assert saved_reflection.user_notes is None


def test_create_reflection_without_travel_guide(
    api_client: TestClient,
    sample_travel_plan: TravelPlanModel,
):
    """前提条件: 旅行ガイドが未生成の旅行計画
    実行: POST /api/v1/reflections
    検証: ステータスコード409
    """
    request_data = {
        "planId": sample_travel_plan.id,
        "userId": sample_travel_plan.user_id,
    }

    response = api_client.post("/api/v1/reflections", json=request_data)

    assert response.status_code == 409


def test_create_reflection_plan_not_found(api_client: TestClient):
    """前提条件: 存在しない旅行計画ID
    実行: POST /api/v1/reflections
    検証: ステータスコード404
    """
    request_data = {
        "planId": "non-existent-plan-id",
        "userId": "test-user",
    }

    response = api_client.post("/api/v1/reflections", json=request_data)

    assert response.status_code == 404
