"""TravelGuideRepositoryのテスト"""

import pytest
from sqlalchemy.orm import Session

from app.domain.travel_guide.entity import TravelGuide
from app.domain.travel_guide.value_objects import Checkpoint, HistoricalEvent, MapData, SpotDetail
from app.infrastructure.persistence.models import TravelGuideModel, TravelPlanModel
from app.infrastructure.repositories.travel_guide_repository import TravelGuideRepository


def test_save_new_travel_guide(db_session: Session, sample_travel_plan: TravelPlanModel):
    """前提: 新規TravelGuideエンティティを作成（idはNone）
    検証: IDが自動生成される、DBに保存される
    """
    # Arrange
    repository = TravelGuideRepository(db_session)
    travel_guide = TravelGuide(
        id=None,
        plan_id=sample_travel_plan.id,
        overview="奈良の歴史的寺院を巡る旅",
        timeline=[
            HistoricalEvent(
                year=710,
                event="平城京遷都",
                significance="奈良時代の始まり",
                related_spots=["東大寺", "春日大社"],
            ),
        ],
        spot_details=[
            SpotDetail(
                spot_name="東大寺",
                historical_background="奈良時代に創建された寺院",
                highlights=["大仏殿", "南大門", "二月堂"],
                recommended_visit_time="午前中",
                historical_significance="奈良時代の仏教文化の象徴",
            ),
        ],
        checkpoints=[
            Checkpoint(
                spot_name="東大寺",
                checkpoints=["大仏の高さを確認", "南大門の金剛力士像を観察"],
                historical_context="聖武天皇の発願により創建",
            ),
        ],
        map_data={
            "center": {"lat": 34.6851, "lng": 135.8048},
            "zoom": 14,
            "markers": [{"lat": 34.6889, "lng": 135.8398, "label": "東大寺"}],
        },
    )

    # Act
    saved = repository.save(travel_guide)

    # Assert
    assert saved.id is not None
    assert saved.plan_id == sample_travel_plan.id
    assert saved.overview == "奈良の歴史的寺院を巡る旅"
    assert saved.created_at is not None
    assert saved.updated_at is not None


def test_save_update_travel_guide(db_session: Session, sample_travel_guide: TravelGuideModel):
    """前提: 既存TravelGuideを取得し、update_guide()で変更
    検証: IDが変わらない、更新内容がDBに反映される
    """
    # Arrange
    repository = TravelGuideRepository(db_session)
    existing = repository.find_by_id(sample_travel_guide.id)
    assert existing is not None
    original_id = existing.id

    # Act
    existing.update_guide(overview="京都の歴史的寺院を巡る素晴らしい旅")
    saved = repository.save(existing)

    # Assert
    assert saved.id == original_id
    assert saved.overview == "京都の歴史的寺院を巡る素晴らしい旅"


def test_find_by_id_existing(db_session: Session, sample_travel_guide: TravelGuideModel):
    """検証: TravelGuideエンティティが返却される、値オブジェクトが正しく変換される"""
    # Arrange
    repository = TravelGuideRepository(db_session)

    # Act
    result = repository.find_by_id(sample_travel_guide.id)

    # Assert
    assert result is not None
    assert result.id == sample_travel_guide.id
    assert result.plan_id == sample_travel_guide.plan_id
    assert result.overview == sample_travel_guide.overview
    assert isinstance(result.timeline, list)
    assert all(isinstance(event, HistoricalEvent) for event in result.timeline)
    assert isinstance(result.spot_details, list)
    assert all(isinstance(detail, SpotDetail) for detail in result.spot_details)
    assert isinstance(result.checkpoints, list)
    assert all(isinstance(checkpoint, Checkpoint) for checkpoint in result.checkpoints)
    assert isinstance(result.map_data, dict)


def test_find_by_id_not_found(db_session: Session):
    """検証: Noneが返却される"""
    # Arrange
    repository = TravelGuideRepository(db_session)

    # Act
    result = repository.find_by_id("non-existent-id")

    # Assert
    assert result is None


def test_find_by_plan_id_existing(db_session: Session, sample_travel_guide: TravelGuideModel):
    """検証: TravelGuideエンティティが返却される"""
    # Arrange
    repository = TravelGuideRepository(db_session)

    # Act
    result = repository.find_by_plan_id(sample_travel_guide.plan_id)

    # Assert
    assert result is not None
    assert result.id == sample_travel_guide.id
    assert result.plan_id == sample_travel_guide.plan_id


def test_find_by_plan_id_not_found(db_session: Session):
    """検証: Noneが返却される"""
    # Arrange
    repository = TravelGuideRepository(db_session)

    # Act
    result = repository.find_by_plan_id("non-existent-plan-id")

    # Assert
    assert result is None


def test_delete_existing(db_session: Session, sample_travel_guide: TravelGuideModel):
    """検証: DBから削除される"""
    # Arrange
    repository = TravelGuideRepository(db_session)
    guide_id = sample_travel_guide.id

    # Act
    repository.delete(guide_id)

    # Assert
    result = repository.find_by_id(guide_id)
    assert result is None


def test_delete_not_found(db_session: Session):
    """検証: エラーが発生しない"""
    # Arrange
    repository = TravelGuideRepository(db_session)

    # Act & Assert（例外が発生しないことを確認）
    repository.delete("non-existent-id")


def test_value_object_conversion(db_session: Session, sample_travel_plan: TravelPlanModel):
    """検証: HistoricalEvent、SpotDetail、Checkpointの各フィールドが正しく変換される"""
    # Arrange
    repository = TravelGuideRepository(db_session)
    travel_guide = TravelGuide(
        id=None,
        plan_id=sample_travel_plan.id,
        overview="大阪の歴史的建造物を巡る旅",
        timeline=[
            HistoricalEvent(
                year=1583,
                event="大阪城築城開始",
                significance="豊臣秀吉による天下統一の象徴",
                related_spots=["大阪城", "真田丸跡"],
            ),
        ],
        spot_details=[
            SpotDetail(
                spot_name="大阪城",
                historical_background="豊臣秀吉により築かれた日本三名城の一つ",
                highlights=["天守閣", "石垣", "堀"],
                recommended_visit_time="午前中から昼過ぎ",
                historical_significance="豊臣政権の権威の象徴",
            ),
        ],
        checkpoints=[
            Checkpoint(
                spot_name="大阪城",
                checkpoints=["石垣の巨石を確認", "天守閣の展望台から市街を眺める"],
                historical_context="徳川時代に再建された現在の石垣",
            ),
        ],
        map_data={
            "center": {"lat": 34.6873, "lng": 135.526},
            "zoom": 15,
            "markers": [{"lat": 34.6873, "lng": 135.526, "label": "大阪城"}],
        },
    )

    # Act
    saved = repository.save(travel_guide)
    retrieved = repository.find_by_id(saved.id)

    # Assert
    assert retrieved is not None

    # HistoricalEventの検証
    assert len(retrieved.timeline) == 1
    event = retrieved.timeline[0]
    assert event.year == 1583
    assert event.event == "大阪城築城開始"
    assert event.significance == "豊臣秀吉による天下統一の象徴"
    assert event.related_spots == ("大阪城", "真田丸跡")

    # SpotDetailの検証
    assert len(retrieved.spot_details) == 1
    detail = retrieved.spot_details[0]
    assert detail.spot_name == "大阪城"
    assert detail.historical_background == "豊臣秀吉により築かれた日本三名城の一つ"
    assert detail.highlights == ("天守閣", "石垣", "堀")
    assert detail.recommended_visit_time == "午前中から昼過ぎ"
    assert detail.historical_significance == "豊臣政権の権威の象徴"

    # Checkpointの検証
    assert len(retrieved.checkpoints) == 1
    checkpoint = retrieved.checkpoints[0]
    assert checkpoint.spot_name == "大阪城"
    assert checkpoint.checkpoints == ("石垣の巨石を確認", "天守閣の展望台から市街を眺める")
    assert checkpoint.historical_context == "徳川時代に再建された現在の石垣"


def test_save_update_not_found(db_session: Session):
    """検証: ValueErrorがraiseされる"""
    # Arrange
    repository = TravelGuideRepository(db_session)
    travel_guide = TravelGuide(
        id="non-existent-id",
        plan_id="dummy-plan-id",
        overview="存在しないガイド",
        timeline=[
            HistoricalEvent(
                year=2000,
                event="テスト",
                significance="テスト",
                related_spots=["テスト"],
            ),
        ],
        spot_details=[
            SpotDetail(
                spot_name="テスト",
                historical_background="テスト",
                highlights=["テスト"],
                recommended_visit_time="テスト",
                historical_significance="テスト",
            ),
        ],
        checkpoints=[
            Checkpoint(
                spot_name="テスト",
                checkpoints=["テスト"],
                historical_context="テスト",
            ),
        ],
        map_data={
            "center": {"lat": 0.0, "lng": 0.0},
            "zoom": 10,
            "markers": [{"lat": 0.0, "lng": 0.0, "label": "テスト"}],
        },
    )

    # Act & Assert
    with pytest.raises(ValueError, match="TravelGuide not found"):
        repository.save(travel_guide)
