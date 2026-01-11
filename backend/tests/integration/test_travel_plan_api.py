"""TravelPlan API統合テスト."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.models import TravelPlanModel
from main import app


def test_create_travel_plan(db_session: Session):
    """前提条件: テスト用DBセッション
    実行: POST /api/v1/travel-plans
    検証: ステータスコード201、レスポンスデータ
    """
    # 前提条件: テスト用DBセッションを使用

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # リクエストデータ
    request_data = {
        "userId": "test_user_001",
        "title": "京都歴史ツアー",
        "destination": "京都",
        "spots": [
            {
                "name": "清水寺",
                "location": {"lat": 34.9949, "lng": 135.785},
                "description": "京都を代表する寺院",
                "userNotes": "早朝訪問予定",
            }
        ],
    }

    # 実行: POST /api/v1/travel-plans
    response = client.post("/api/v1/travel-plans", json=request_data)

    # 検証: ステータスコード201、レスポンスデータ
    assert response.status_code == 201
    data = response.json()
    assert data["userId"] == "test_user_001"
    assert data["title"] == "京都歴史ツアー"
    assert data["destination"] == "京都"
    assert len(data["spots"]) == 1
    assert data["spots"][0]["name"] == "清水寺"
    assert data["status"] == "planning"
    assert "id" in data
    assert "createdAt" in data
    assert "updatedAt" in data

    # クリーンアップ
    app.dependency_overrides.clear()


def test_get_travel_plan(db_session: Session, sample_travel_plan: TravelPlanModel):
    """前提条件: テスト用DBセッションとサンプルデータ
    実行: GET /api/v1/travel-plans/{id}
    検証: ステータスコード200、レスポンスデータ
    """
    # 前提条件: テスト用DBセッションとサンプルデータ

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # 実行: GET /api/v1/travel-plans/{id}
    response = client.get(f"/api/v1/travel-plans/{sample_travel_plan.id}")

    # 検証: ステータスコード200、レスポンスデータ
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_travel_plan.id
    assert data["title"] == sample_travel_plan.title
    assert data["destination"] == sample_travel_plan.destination
    assert len(data["spots"]) == len(sample_travel_plan.spots)

    # クリーンアップ
    app.dependency_overrides.clear()


def test_get_travel_plan_not_found(db_session: Session):
    """前提条件: 存在しないID
    実行: GET /api/v1/travel-plans/{non_existent_id}
    検証: ステータスコード404
    """
    # 前提条件: 存在しないID

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # 実行: GET /api/v1/travel-plans/{non_existent_id}
    response = client.get("/api/v1/travel-plans/non-existent-id")

    # 検証: ステータスコード404
    assert response.status_code == 404

    # クリーンアップ
    app.dependency_overrides.clear()


def test_list_travel_plans(db_session: Session, sample_travel_plan: TravelPlanModel):
    """前提条件: テスト用DBセッションとサンプルデータ
    実行: GET /api/v1/travel-plans?user_id={id}
    検証: ステータスコード200、レスポンスリスト
    """
    # 前提条件: テスト用DBセッションとサンプルデータ

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # 実行: GET /api/v1/travel-plans?user_id={id}
    response = client.get(f"/api/v1/travel-plans?user_id={sample_travel_plan.user_id}")

    # 検証: ステータスコード200、レスポンスリスト
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == sample_travel_plan.id

    # クリーンアップ
    app.dependency_overrides.clear()


def test_update_travel_plan(db_session: Session, sample_travel_plan: TravelPlanModel):
    """前提条件: テスト用DBセッションとサンプルデータ
    実行: PUT /api/v1/travel-plans/{id}
    検証: ステータスコード200、更新されたデータ
    """
    # 前提条件: テスト用DBセッションとサンプルデータ

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # リクエストデータ
    update_data = {
        "title": "京都歴史探訪の旅（更新版）",
        "destination": "京都・大阪",
    }

    # 実行: PUT /api/v1/travel-plans/{id}
    response = client.put(
        f"/api/v1/travel-plans/{sample_travel_plan.id}", json=update_data
    )

    # 検証: ステータスコード200、更新されたデータ
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_travel_plan.id
    assert data["title"] == "京都歴史探訪の旅（更新版）"
    assert data["destination"] == "京都・大阪"

    # クリーンアップ
    app.dependency_overrides.clear()


def test_update_travel_plan_not_found(db_session: Session):
    """前提条件: 存在しないID
    実行: PUT /api/v1/travel-plans/{non_existent_id}
    検証: ステータスコード404
    """
    # 前提条件: 存在しないID

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # リクエストデータ
    update_data = {
        "title": "更新タイトル",
    }

    # 実行: PUT /api/v1/travel-plans/{non_existent_id}
    response = client.put("/api/v1/travel-plans/non-existent-id", json=update_data)

    # 検証: ステータスコード404
    assert response.status_code == 404

    # クリーンアップ
    app.dependency_overrides.clear()
