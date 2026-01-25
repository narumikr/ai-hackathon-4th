"""TravelPlan API統合テスト"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.models import ReflectionModel, TravelPlanModel
from main import app


@pytest.fixture
def api_client(db_session: Session):
    """テスト用DBセッションを注入したTestClientを返す"""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def test_create_travel_plan(api_client: TestClient):
    """前提条件: テスト用DBセッション
    実行: POST /api/v1/travel-plans
    検証: ステータスコード201、レスポンスデータ
    """
    # 前提条件: テスト用DBセッションを使用

    # リクエストデータ
    request_data = {
        "userId": "test_user_001",
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

    # 実行: POST /api/v1/travel-plans
    response = api_client.post("/api/v1/travel-plans", json=request_data)

    # 検証: ステータスコード201、レスポンスデータ
    assert response.status_code == 201
    data = response.json()
    assert data["userId"] == "test_user_001"
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
    # 前提条件: テスト用DBセッションを使用

    # リクエストデータ
    request_data = {
        "userId": "test_user_002",
        "title": "奈良日帰りプラン",
        "destination": "奈良",
        "spots": [],
    }

    # 実行: POST /api/v1/travel-plans
    response = api_client.post("/api/v1/travel-plans", json=request_data)

    # 検証: ステータスコード201、spotsが空配列で返る
    assert response.status_code == 201
    data = response.json()
    assert data["userId"] == "test_user_002"
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
    # 前提条件: テスト用DBセッションを使用

    # リクエストデータ
    request_data = {
        "userId": "test_user_003",
        "title": "広島歴史巡り",
        "destination": "広島",
    }

    # 実行: POST /api/v1/travel-plans
    response = api_client.post("/api/v1/travel-plans", json=request_data)

    # 検証: ステータスコード201、spotsが空配列で返る
    assert response.status_code == 201
    data = response.json()
    assert data["userId"] == "test_user_003"
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
    # 前提条件: テスト用DBセッションを使用

    # リクエストデータ
    request_data = {
        "userId": "test_user_004",
        "title": "鎌倉散策",
        "destination": "鎌倉",
        "spots": None,
    }

    # 実行: POST /api/v1/travel-plans
    response = api_client.post("/api/v1/travel-plans", json=request_data)

    # 検証: ステータスコード422
    assert response.status_code == 422


def test_get_travel_plan(
    api_client: TestClient, sample_travel_plan: TravelPlanModel
):
    """前提条件: テスト用DBセッションとサンプルデータ
    実行: GET /api/v1/travel-plans/{id}
    検証: ステータスコード200、レスポンスデータ
    """
    # 前提条件: テスト用DBセッションとサンプルデータ

    # 実行: GET /api/v1/travel-plans/{id}
    response = api_client.get(f"/api/v1/travel-plans/{sample_travel_plan.id}")

    # 検証: ステータスコード200、レスポンスデータ
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
                "analysis": {
                    "detectedSpots": ["清水寺"],
                    "historicalElements": ["清水の舞台"],
                    "landmarks": ["清水寺本堂"],
                    "confidence": 0.9,
                },
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
    # 前提条件: 存在しないID

    # 実行: GET /api/v1/travel-plans/{non_existent_id}
    response = api_client.get("/api/v1/travel-plans/non-existent-id")

    # 検証: ステータスコード404
    assert response.status_code == 404


def test_list_travel_plans(
    api_client: TestClient, sample_travel_plan: TravelPlanModel
):
    """前提条件: テスト用DBセッションとサンプルデータ
    実行: GET /api/v1/travel-plans?user_id={id}
    検証: ステータスコード200、レスポンスリスト
    """
    # 前提条件: テスト用DBセッションとサンプルデータ

    # 実行: GET /api/v1/travel-plans?user_id={id}
    response = api_client.get(
        f"/api/v1/travel-plans?user_id={sample_travel_plan.user_id}"
    )

    # 検証: ステータスコード200、レスポンスリスト
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == sample_travel_plan.id
    assert data[0]["guideGenerationStatus"] == sample_travel_plan.guide_generation_status
    assert data[0]["reflectionGenerationStatus"] == sample_travel_plan.reflection_generation_status


def test_update_travel_plan(
    api_client: TestClient, sample_travel_plan: TravelPlanModel
):
    """前提条件: テスト用DBセッションとサンプルデータ
    実行: PUT /api/v1/travel-plans/{id}
    検証: ステータスコード200、更新されたデータ
    """
    # 前提条件: テスト用DBセッションとサンプルデータ

    # リクエストデータ
    update_data = {
        "title": "京都歴史探訪の旅（更新版）",
        "destination": "京都・大阪",
    }

    # 実行: PUT /api/v1/travel-plans/{id}
    response = api_client.put(
        f"/api/v1/travel-plans/{sample_travel_plan.id}", json=update_data
    )

    # 検証: ステータスコード200、更新されたデータ
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_travel_plan.id
    assert data["title"] == "京都歴史探訪の旅（更新版）"
    assert data["destination"] == "京都・大阪"
    assert data["guideGenerationStatus"] == "not_started"
    assert data["reflectionGenerationStatus"] == "not_started"


def test_update_travel_plan_status(
    api_client: TestClient, sample_travel_plan: TravelPlanModel
):
    """前提条件: テスト用DBセッションとサンプルデータ
    実行: PUT /api/v1/travel-plans/{id} でstatus更新
    検証: ステータスコード200、statusが更新される
    """
    # 前提条件: テスト用DBセッションとサンプルデータ

    # リクエストデータ
    update_data = {
        "status": "completed",
    }

    # 実行: PUT /api/v1/travel-plans/{id}
    response = api_client.put(
        f"/api/v1/travel-plans/{sample_travel_plan.id}", json=update_data
    )

    # 検証: ステータスコード200、statusが更新される
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_travel_plan.id
    assert data["status"] == "completed"


def test_update_travel_plan_not_found(api_client: TestClient):
    """前提条件: 存在しないID
    実行: PUT /api/v1/travel-plans/{non_existent_id}
    検証: ステータスコード404
    """
    # 前提条件: 存在しないID

    # リクエストデータ
    update_data = {
        "title": "更新タイトル",
    }

    # 実行: PUT /api/v1/travel-plans/{non_existent_id}
    response = api_client.put("/api/v1/travel-plans/non-existent-id", json=update_data)

    # 検証: ステータスコード404
    assert response.status_code == 404


def test_delete_travel_plan(
    api_client: TestClient, db_session: Session, sample_travel_plan: TravelPlanModel
):
    """前提条件: テスト用DBセッションとサンプルデータ
    実行: DELETE /api/v1/travel-plans/{id}
    検証: ステータスコード204、データが削除されている
    """
    # 前提条件: テスト用DBセッションとサンプルデータ

    # 実行: DELETE /api/v1/travel-plans/{id}
    response = api_client.delete(f"/api/v1/travel-plans/{sample_travel_plan.id}")

    # 検証: ステータスコード204、データが削除されている
    assert response.status_code == 204
    assert db_session.get(TravelPlanModel, sample_travel_plan.id) is None


def test_delete_travel_plan_not_found(api_client: TestClient):
    """前提条件: 存在しないID
    実行: DELETE /api/v1/travel-plans/{non_existent_id}
    検証: ステータスコード404
    """
    # 前提条件: 存在しないID

    # 実行: DELETE /api/v1/travel-plans/{non_existent_id}
    response = api_client.delete("/api/v1/travel-plans/non-existent-id")

    # 検証: ステータスコード404
    assert response.status_code == 404
