"""TravelPlan API統合テスト"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.models import ReflectionModel, TravelPlanModel
from app.interfaces.middleware.auth import UserContext, require_auth
from main import app

TEST_USER_ID = "test_user_001"


def _make_auth_override(uid: str = TEST_USER_ID):
    """テスト用の認証オーバーライドを返す"""

    def override_require_auth() -> UserContext:
        return UserContext(uid=uid)

    return override_require_auth


@pytest.fixture
def api_client(db_session: Session):
    """テスト用DBセッションと認証を注入したTestClientを返す"""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_auth] = _make_auth_override()
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def test_create_travel_plan(api_client: TestClient):
    """前提条件: テスト用DBセッション
    実行: POST /api/v1/travel-plans
    検証: ステータスコード201、レスポンスデータ
    """
    request_data = {
        "title": "京都歴史ツアー",
        "destination": "京都",
        "spots": [
            {
                "name": "清水寺",
                "description": "京都を代表する寺院",
                "userNotes": "早朝訪問予定",
            }
        ],
    }

    response = api_client.post("/api/v1/travel-plans", json=request_data)

    assert response.status_code == 201
    data = response.json()
    assert data["userId"] == TEST_USER_ID
    assert data["title"] == "京都歴史ツアー"
    assert data["destination"] == "京都"
    assert len(data["spots"]) == 1
    assert data["spots"][0]["name"] == "清水寺"
    assert data["status"] == "planning"
    assert data["guideGenerationStatus"] == "not_started"
    assert data["reflectionGenerationStatus"] == "not_started"
    assert "id" in data
    assert "createdAt" in data
    assert "updatedAt" in data


def test_create_travel_plan_with_empty_spots(api_client: TestClient):
    """前提条件: 空のspotsを含むリクエスト
    実行: POST /api/v1/travel-plans
    検証: ステータスコード201、spotsが空配列で返る
    """
    request_data = {
        "title": "奈良日帰りプラン",
        "destination": "奈良",
        "spots": [],
    }

    response = api_client.post("/api/v1/travel-plans", json=request_data)

    assert response.status_code == 201
    data = response.json()
    assert data["userId"] == TEST_USER_ID
    assert data["title"] == "奈良日帰りプラン"
    assert data["destination"] == "奈良"
    assert data["spots"] == []
    assert data["guideGenerationStatus"] == "not_started"
    assert data["reflectionGenerationStatus"] == "not_started"


def test_create_travel_plan_without_spots(api_client: TestClient):
    """前提条件: spotsを未送信のリクエスト
    実行: POST /api/v1/travel-plans
    検証: ステータスコード201、spotsが空配列で返る
    """
    request_data = {
        "title": "広島歴史巡り",
        "destination": "広島",
    }

    response = api_client.post("/api/v1/travel-plans", json=request_data)

    assert response.status_code == 201
    data = response.json()
    assert data["userId"] == TEST_USER_ID
    assert data["title"] == "広島歴史巡り"
    assert data["destination"] == "広島"
    assert data["spots"] == []
    assert data["guideGenerationStatus"] == "not_started"
    assert data["reflectionGenerationStatus"] == "not_started"


def test_create_travel_plan_with_null_spots(api_client: TestClient):
    """前提条件: spotsがnullのリクエスト
    実行: POST /api/v1/travel-plans
    検証: ステータスコード422
    """
    request_data = {
        "title": "鎌倉散策",
        "destination": "鎌倉",
        "spots": None,
    }

    response = api_client.post("/api/v1/travel-plans", json=request_data)

    assert response.status_code == 422


def test_get_travel_plan(api_client: TestClient, sample_travel_plan: TravelPlanModel):
    """前提条件: テスト用DBセッションとサンプルデータ
    実行: GET /api/v1/travel-plans/{id}
    検証: ステータスコード200、レスポンスデータ
    """
    response = api_client.get(f"/api/v1/travel-plans/{sample_travel_plan.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_travel_plan.id
    assert data["title"] == sample_travel_plan.title
    assert data["destination"] == sample_travel_plan.destination
    assert len(data["spots"]) == len(sample_travel_plan.spots)
    assert data["guideGenerationStatus"] == sample_travel_plan.guide_generation_status
    assert data["reflectionGenerationStatus"] == sample_travel_plan.reflection_generation_status
    assert data["guide"] is None
    assert data["reflection"] is None
    assert data["pamphlet"] is None


def test_get_travel_plan_forbidden(db_session: Session, sample_travel_plan: TravelPlanModel):
    """前提条件: 他のユーザーの旅行計画
    実行: GET /api/v1/travel-plans/{id}
    検証: ステータスコード403
    """

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_auth] = _make_auth_override(uid="other_user")
    client = TestClient(app)

    response = client.get(f"/api/v1/travel-plans/{sample_travel_plan.id}")

    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_get_travel_plan_returns_pamphlet(
    api_client: TestClient,
    db_session: Session,
    sample_travel_plan: TravelPlanModel,
):
    """前提条件: パンフレット付きの振り返りが存在する
    実行: GET /api/v1/travel-plans/{id}
    検証: pamphletがレスポンスに含まれる
    """
    reflection = ReflectionModel(
        plan_id=sample_travel_plan.id,
        user_id=sample_travel_plan.user_id,
        photos=[
            {
                "id": "photo_010",
                "spotId": "spot-001",
                "url": "https://example.com/photos/kiyomizu.jpg",
                "analysis": "清水寺の写真。清水の舞台（本堂の張り出し舞台）が写っており、清水寺本堂の特徴的な懸造（かけづくり）建築が確認できる。",
                "userDescription": "清水寺の舞台が印象的だった",
            },
        ],
        spot_notes={"spot-001": "清水寺の舞台が印象的だった"},
        user_notes="京都の寺院巡りは刺激的だった",
        pamphlet={
            "travel_summary": "京都の寺院巡りを満喫した。",
            "spot_reflections": [
                {"spotName": "清水寺", "reflection": "舞台の眺めが印象的だった。"},
                {"spotName": "金閣寺", "reflection": "金色の輝きが美しかった。"},
            ],
            "next_trip_suggestions": ["奈良の寺院巡り"],
        },
    )
    db_session.add(reflection)
    db_session.commit()

    response = api_client.get(f"/api/v1/travel-plans/{sample_travel_plan.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["pamphlet"] is not None
    assert data["pamphlet"]["travelSummary"] == "京都の寺院巡りを満喫した。"
    assert data["pamphlet"]["spotReflections"][0]["spotName"] == "清水寺"
    assert data["pamphlet"]["spotReflections"][0]["reflection"] == "舞台の眺めが印象的だった。"
    assert data["pamphlet"]["nextTripSuggestions"] == ["奈良の寺院巡り"]


def test_get_travel_plan_not_found(api_client: TestClient):
    """前提条件: 存在しないID
    実行: GET /api/v1/travel-plans/{non_existent_id}
    検証: ステータスコード404
    """
    response = api_client.get("/api/v1/travel-plans/non-existent-id")

    assert response.status_code == 404


def test_list_travel_plans(api_client: TestClient, sample_travel_plan: TravelPlanModel):
    """前提条件: テスト用DBセッションとサンプルデータ
    実行: GET /api/v1/travel-plans
    検証: ステータスコード200、レスポンスリスト（auth.uidでフィルタ）
    """
    response = api_client.get("/api/v1/travel-plans")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    expected_keys = {
        "id",
        "title",
        "destination",
        "status",
        "guideGenerationStatus",
        "reflectionGenerationStatus",
    }
    assert set(data[0].keys()) == expected_keys
    assert data[0]["id"] == sample_travel_plan.id
    assert data[0]["title"] == sample_travel_plan.title
    assert data[0]["destination"] == sample_travel_plan.destination
    assert data[0]["status"] == sample_travel_plan.status
    assert data[0]["guideGenerationStatus"] == sample_travel_plan.guide_generation_status
    assert data[0]["reflectionGenerationStatus"] == sample_travel_plan.reflection_generation_status


def test_update_travel_plan(api_client: TestClient, sample_travel_plan: TravelPlanModel):
    """前提条件: テスト用DBセッションとサンプルデータ
    実行: PUT /api/v1/travel-plans/{id}
    検証: ステータスコード200、更新されたデータ
    """
    update_data = {
        "title": "京都歴史探訪の旅（更新版）",
        "destination": "京都・大阪",
    }

    response = api_client.put(f"/api/v1/travel-plans/{sample_travel_plan.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_travel_plan.id
    assert data["title"] == "京都歴史探訪の旅（更新版）"
    assert data["destination"] == "京都・大阪"
    assert data["guideGenerationStatus"] == "not_started"
    assert data["reflectionGenerationStatus"] == "not_started"


def test_update_travel_plan_status(api_client: TestClient, sample_travel_plan: TravelPlanModel):
    """前提条件: テスト用DBセッションとサンプルデータ
    実行: PUT /api/v1/travel-plans/{id} でstatus更新
    検証: ステータスコード200、statusが更新される
    """
    update_data = {
        "status": "completed",
    }

    response = api_client.put(f"/api/v1/travel-plans/{sample_travel_plan.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_travel_plan.id
    assert data["status"] == "completed"


def test_update_travel_plan_not_found(api_client: TestClient):
    """前提条件: 存在しないID
    実行: PUT /api/v1/travel-plans/{non_existent_id}
    検証: ステータスコード404
    """
    update_data = {
        "title": "更新タイトル",
    }

    response = api_client.put("/api/v1/travel-plans/non-existent-id", json=update_data)

    assert response.status_code == 404


def test_update_travel_plan_forbidden(db_session: Session, sample_travel_plan: TravelPlanModel):
    """前提条件: 他のユーザーの旅行計画
    実行: PUT /api/v1/travel-plans/{id}
    検証: ステータスコード403
    """

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_auth] = _make_auth_override(uid="other_user")
    client = TestClient(app)

    update_data = {"title": "不正な更新"}
    response = client.put(f"/api/v1/travel-plans/{sample_travel_plan.id}", json=update_data)

    assert response.status_code == 403
    app.dependency_overrides.clear()


def test_delete_travel_plan(
    api_client: TestClient, db_session: Session, sample_travel_plan: TravelPlanModel
):
    """前提条件: テスト用DBセッションとサンプルデータ
    実行: DELETE /api/v1/travel-plans/{id}
    検証: ステータスコード204、データが削除されている
    """
    response = api_client.delete(f"/api/v1/travel-plans/{sample_travel_plan.id}")

    assert response.status_code == 204
    assert db_session.get(TravelPlanModel, sample_travel_plan.id) is None


def test_delete_travel_plan_not_found(api_client: TestClient):
    """前提条件: 存在しないID
    実行: DELETE /api/v1/travel-plans/{non_existent_id}
    検証: ステータスコード404
    """
    response = api_client.delete("/api/v1/travel-plans/non-existent-id")

    assert response.status_code == 404


def test_delete_travel_plan_forbidden(db_session: Session, sample_travel_plan: TravelPlanModel):
    """前提条件: 他のユーザーの旅行計画
    実行: DELETE /api/v1/travel-plans/{id}
    検証: ステータスコード403
    """

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_auth] = _make_auth_override(uid="other_user")
    client = TestClient(app)

    response = client.delete(f"/api/v1/travel-plans/{sample_travel_plan.id}")

    assert response.status_code == 403
    app.dependency_overrides.clear()
