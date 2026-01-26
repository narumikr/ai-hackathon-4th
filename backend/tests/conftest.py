"""テスト用共通fixture."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.models import (
    ReflectionModel,
    TravelGuideModel,
    TravelPlanModel,
    TravelPlanSpotModel,
)

# テスト用データベースURL
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/travel_agent_test"


@pytest.fixture(scope="session")
def test_engine():
    """テスト用データベースエンジンを作成する."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)

    # テスト開始前にすべてのテーブルを作成
    Base.metadata.create_all(bind=engine)

    yield engine

    # テスト終了後にすべてのテーブルを削除
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """テスト用データベースセッションを作成する.

    各テスト関数ごとに新しいトランザクションを開始し、
    テスト終了後にロールバックすることでデータをクリーンに保つ。
    """
    connection = test_engine.connect()
    transaction = connection.begin()

    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection,
    )
    session = TestSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_travel_plan(db_session: Session) -> TravelPlanModel:
    """サンプルTravelPlanデータを作成する."""
    travel_plan = TravelPlanModel(
        user_id="test_user_001",
        title="京都歴史ツアー",
        destination="京都",
        status="planning",
    )
    travel_plan.spots = [
        TravelPlanSpotModel(
            id="spot-001",
            name="清水寺",
            description="京都を代表する寺院",
            user_notes="早朝訪問予定",
            sort_order=0,
        ),
        TravelPlanSpotModel(
            id="spot-002",
            name="金閣寺",
            description="金色に輝く舎利殿",
            user_notes="午後に訪問",
            sort_order=1,
        ),
    ]
    db_session.add(travel_plan)
    db_session.commit()
    db_session.refresh(travel_plan)
    return travel_plan


@pytest.fixture
def sample_travel_guide(
    db_session: Session, sample_travel_plan: TravelPlanModel
) -> TravelGuideModel:
    """サンプルTravelGuideデータを作成する."""
    travel_guide = TravelGuideModel(
        plan_id=sample_travel_plan.id,
        overview="京都の歴史的寺院を巡る旅",
        timeline=[
            {
                "year": 778,
                "event": "清水寺創建",
                "significance": "平安京遷都より前の歴史",
                "relatedSpots": ["清水寺"],
            },
            {
                "year": 1397,
                "event": "金閣寺創建",
                "significance": "室町幕府第3代将軍足利義満の別荘",
                "relatedSpots": ["金閣寺"],
            },
        ],
        spot_details=[
            {
                "spotName": "清水寺",
                "historicalBackground": "奈良時代末期に創建された古刹",
                "highlights": ["清水の舞台", "音羽の滝", "三重塔"],
                "recommendedVisitTime": "早朝または夕方",
                "historicalSignificance": "平安京遷都より前の歴史を持つ",
            },
        ],
        checkpoints=[
            {
                "spotName": "清水寺",
                "checkpoints": ["清水の舞台の高さを確認", "音羽の滝の三筋の意味を学ぶ"],
                "historicalContext": "断崖絶壁に建つ懸造りの舞台",
            },
        ],
    )
    db_session.add(travel_guide)
    db_session.commit()
    db_session.refresh(travel_guide)
    return travel_guide


@pytest.fixture
def sample_reflection(
    db_session: Session, sample_travel_plan: TravelPlanModel
) -> ReflectionModel:
    """サンプル振り返りデータを作成する."""
    reflection = ReflectionModel(
        plan_id=sample_travel_plan.id,
        user_id="test_user_001",
        photos=[
            {
                "id": "photo_001",
                "spotId": "spot-001",
                "url": "https://example.com/photos/kiyomizu.jpg",
                "analysis": {
                    "detectedSpots": ["清水寺"],
                    "historicalElements": ["清水の舞台", "三重塔"],
                    "landmarks": ["清水寺本堂"],
                    "confidence": 0.95,
                },
                "userDescription": "清水の舞台からの絶景",
            },
        ],
        user_notes="歴史の重みを感じる素晴らしい旅でした",
        spot_notes={"spot-001": "清水寺の舞台が印象的だった"},
    )
    db_session.add(reflection)
    db_session.commit()
    db_session.refresh(reflection)
    return reflection
