"""SQLAlchemyモデルのテスト."""

import uuid

from sqlalchemy.orm import Session

from app.infrastructure.persistence.models import (
    ReflectionModel,
    TravelGuideModel,
    TravelPlanModel,
)


def test_create_travel_plan(db_session: Session):
    """TravelPlanの作成をテストする."""
    # TravelPlanを作成
    travel_plan = TravelPlanModel(
        user_id="user123",
        title="奈良歴史ツアー",
        destination="奈良",
        spots=[
            {
                "name": "東大寺",
                "location": {"lat": 34.689, "lng": 135.84},
                "description": "大仏殿",
                "userNotes": "午前中に訪問",
            }
        ],
        status="planning",
    )
    db_session.add(travel_plan)
    db_session.commit()
    db_session.refresh(travel_plan)

    # 検証
    assert travel_plan.id is not None
    # IDがUUID形式であることを確認
    assert uuid.UUID(travel_plan.id)
    assert travel_plan.user_id == "user123"
    assert travel_plan.title == "奈良歴史ツアー"
    assert travel_plan.destination == "奈良"
    assert len(travel_plan.spots) == 1
    assert travel_plan.spots[0]["name"] == "東大寺"
    assert travel_plan.status == "planning"
    assert travel_plan.created_at is not None
    assert travel_plan.updated_at is not None


def test_create_travel_guide(db_session: Session, sample_travel_plan: TravelPlanModel):
    """TravelGuideの作成とリレーションをテストする."""
    # TravelGuideを作成
    travel_guide = TravelGuideModel(
        plan_id=sample_travel_plan.id,
        overview="京都の歴史を学ぶ旅",
        timeline=[
            {
                "year": 794,
                "event": "平安京遷都",
                "significance": "京都の歴史の始まり",
                "relatedSpots": ["京都御所"],
            }
        ],
        spot_details=[
            {
                "spotName": "京都御所",
                "historicalBackground": "歴代天皇の住まい",
                "highlights": ["紫宸殿", "清涼殿"],
                "recommendedVisitTime": "午前中",
                "historicalSignificance": "日本の政治の中心",
            }
        ],
        checkpoints=[
            {
                "spotName": "京都御所",
                "checkpoints": ["紫宸殿を見学", "庭園を散策"],
                "historicalContext": "平安時代から江戸時代までの歴史",
            }
        ],
        map_data={
            "center": {"lat": 35.025, "lng": 135.762},
            "zoom": 14,
        },
    )
    db_session.add(travel_guide)
    db_session.commit()
    db_session.refresh(travel_guide)

    # 検証
    assert travel_guide.id is not None
    assert uuid.UUID(travel_guide.id)
    assert travel_guide.plan_id == sample_travel_plan.id
    assert travel_guide.overview == "京都の歴史を学ぶ旅"
    assert len(travel_guide.timeline) == 1
    assert travel_guide.timeline[0]["year"] == 794
    assert len(travel_guide.spot_details) == 1
    assert len(travel_guide.checkpoints) == 1
    assert isinstance(travel_guide.map_data, dict)
    assert travel_guide.map_data["zoom"] == 14

    # リレーションシップを確認
    assert travel_guide.plan == sample_travel_plan
    assert sample_travel_plan.guide == travel_guide


def test_create_reflection(db_session: Session, sample_travel_plan: TravelPlanModel):
    """Reflectionの作成とリレーションをテストする."""
    # Reflectionを作成
    reflection = ReflectionModel(
        plan_id=sample_travel_plan.id,
        user_id="user123",
        photos=[
            {
                "id": "photo123",
                "url": "https://example.com/photo.jpg",
                "analysis": {
                    "detectedSpots": ["京都タワー"],
                    "historicalElements": ["タワー"],
                    "landmarks": ["京都タワー"],
                    "confidence": 0.9,
                },
                "userDescription": "京都駅から見たタワー",
            }
        ],
        user_notes="素晴らしい旅でした",
    )
    db_session.add(reflection)
    db_session.commit()
    db_session.refresh(reflection)

    # 検証
    assert reflection.id is not None
    assert uuid.UUID(reflection.id)
    assert reflection.plan_id == sample_travel_plan.id
    assert reflection.user_id == "user123"
    assert len(reflection.photos) == 1
    assert reflection.photos[0]["id"] == "photo123"
    assert reflection.photos[0]["analysis"]["confidence"] == 0.9
    assert reflection.user_notes == "素晴らしい旅でした"

    # リレーションシップを確認
    assert reflection.plan == sample_travel_plan
    assert sample_travel_plan.reflection == reflection


def test_json_fields(db_session: Session):
    """JSON型フィールドの格納・取得をテストする."""
    # 複雑なJSON構造を持つTravelPlanを作成
    complex_spots = [
        {
            "name": "スポット1",
            "location": {"lat": 35.0, "lng": 135.0},
            "description": "詳細な説明",
            "userNotes": "メモ",
        },
        {
            "name": "スポット2",
            "location": {"lat": 35.1, "lng": 135.1},
        },
    ]

    travel_plan = TravelPlanModel(
        user_id="user456",
        title="テストプラン",
        destination="テスト地",
        spots=complex_spots,
        status="planning",
    )
    db_session.add(travel_plan)
    db_session.commit()
    db_session.refresh(travel_plan)

    # JSONデータが正しく保存・取得できることを確認
    assert len(travel_plan.spots) == 2
    assert travel_plan.spots[0]["name"] == "スポット1"
    assert travel_plan.spots[0]["location"]["lat"] == 35.0
    assert travel_plan.spots[1]["name"] == "スポット2"
    # オプショナルフィールドが存在しない場合でもエラーにならないことを確認
    assert "description" not in travel_plan.spots[1]


def test_cascade_delete(db_session: Session, sample_travel_plan: TravelPlanModel):
    """カスケード削除の動作を確認する."""
    # TravelGuideとReflectionを作成
    travel_guide = TravelGuideModel(
        plan_id=sample_travel_plan.id,
        overview="テストガイド",
        timeline=[],
        spot_details=[],
        checkpoints=[],
        map_data={},
    )
    reflection = ReflectionModel(
        plan_id=sample_travel_plan.id,
        user_id="user123",
        photos=[],
        user_notes="テストメモ",
    )
    db_session.add(travel_guide)
    db_session.add(reflection)
    db_session.commit()

    guide_id = travel_guide.id
    reflection_id = reflection.id

    # TravelPlanを削除
    db_session.delete(sample_travel_plan)
    db_session.commit()

    # TravelGuideとReflectionも削除されていることを確認
    assert db_session.get(TravelGuideModel, guide_id) is None
    assert db_session.get(ReflectionModel, reflection_id) is None


def test_unique_constraints(
    db_session: Session, sample_travel_plan: TravelPlanModel, sample_travel_guide: TravelGuideModel
):
    """ユニーク制約の動作を確認する."""
    # 同じplan_idで別のTravelGuideを作成しようとするとエラーになる
    duplicate_guide = TravelGuideModel(
        plan_id=sample_travel_plan.id,  # 既に使用されているplan_id
        overview="重複ガイド",
        timeline=[],
        spot_details=[],
        checkpoints=[],
        map_data={},
    )
    db_session.add(duplicate_guide)

    # IntegrityError（ユニーク制約違反）が発生することを確認
    from sqlalchemy.exc import IntegrityError

    try:
        db_session.commit()
        assert False, "ユニーク制約違反が検出されませんでした"
    except IntegrityError:
        # 期待通りの動作
        db_session.rollback()
        assert True


def test_travel_plan_status_update(db_session: Session, sample_travel_plan: TravelPlanModel):
    """TravelPlanのステータス更新をテストする."""
    # ステータスを'planning'から'completed'に変更
    sample_travel_plan.status = "completed"
    db_session.commit()
    db_session.refresh(sample_travel_plan)

    # 検証
    assert sample_travel_plan.status == "completed"
    # updated_atが更新されていることを確認
    assert sample_travel_plan.updated_at >= sample_travel_plan.created_at
