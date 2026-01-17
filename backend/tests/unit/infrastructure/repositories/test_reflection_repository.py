"""ReflectionRepositoryのテスト"""

import pytest
from sqlalchemy.orm import Session

from app.domain.reflection.entity import Photo, Reflection
from app.domain.reflection.value_objects import ImageAnalysis
from app.infrastructure.persistence.models import ReflectionModel, TravelPlanModel
from app.infrastructure.repositories.reflection_repository import ReflectionRepository


def test_save_new_reflection(db_session: Session, sample_travel_plan: TravelPlanModel):
    """前提: 新規Reflectionエンティティを作成（idはNone）
    検証: IDが自動生成される、photosがJSON型で保存される
    """
    # Arrange
    repository = ReflectionRepository(db_session)
    photo = Photo(
        id="photo_nara_001",
        url="https://example.com/photos/todaiji.jpg",
        analysis=ImageAnalysis(
            detected_spots=["東大寺"],
            historical_elements=["大仏殿", "南大門"],
            landmarks=["奈良の大仏"],
            confidence=0.98,
        ),
        user_description="奈良の大仏の迫力に圧倒されました",
    )
    reflection = Reflection(
        id=None,
        plan_id=sample_travel_plan.id,
        user_id="test_user_002",
        photos=[photo],
        user_notes="奈良の歴史を深く感じた旅でした",
    )

    # Act
    saved = repository.save(reflection)

    # Assert
    assert saved.id is not None
    assert saved.plan_id == sample_travel_plan.id
    assert saved.user_id == "test_user_002"
    assert len(saved.photos) == 1
    assert saved.photos[0].id == "photo_nara_001"
    assert saved.created_at is not None


def test_save_update_reflection(db_session: Session, sample_reflection: ReflectionModel):
    """前提: 既存Reflectionを取得し、update_notes()で変更
    検証: IDが変わらない、user_notesが更新される
    """
    # Arrange
    repository = ReflectionRepository(db_session)
    existing = repository.find_by_id(sample_reflection.id)
    assert existing is not None
    original_id = existing.id

    # Act
    existing.update_notes("歴史の重みと美しさを再認識した素晴らしい旅でした")
    saved = repository.save(existing)

    # Assert
    assert saved.id == original_id
    assert saved.user_notes == "歴史の重みと美しさを再認識した素晴らしい旅でした"


def test_find_by_id_existing(db_session: Session, sample_reflection: ReflectionModel):
    """検証: Reflectionエンティティが返却される、PhotoとImageAnalysisが正しく復元される"""
    # Arrange
    repository = ReflectionRepository(db_session)

    # Act
    result = repository.find_by_id(sample_reflection.id)

    # Assert
    assert result is not None
    assert result.id == sample_reflection.id
    assert result.plan_id == sample_reflection.plan_id
    assert result.user_id == sample_reflection.user_id
    assert isinstance(result.photos, list)
    assert all(isinstance(photo, Photo) for photo in result.photos)
    assert all(isinstance(photo.analysis, ImageAnalysis) for photo in result.photos)


def test_find_by_id_not_found(db_session: Session):
    """検証: Noneが返却される"""
    # Arrange
    repository = ReflectionRepository(db_session)

    # Act
    result = repository.find_by_id("non-existent-id")

    # Assert
    assert result is None


def test_find_by_plan_id_existing(db_session: Session, sample_reflection: ReflectionModel):
    """検証: Reflectionエンティティが返却される"""
    # Arrange
    repository = ReflectionRepository(db_session)

    # Act
    result = repository.find_by_plan_id(sample_reflection.plan_id)

    # Assert
    assert result is not None
    assert result.id == sample_reflection.id
    assert result.plan_id == sample_reflection.plan_id


def test_find_by_plan_id_not_found(db_session: Session):
    """検証: Noneが返却される"""
    # Arrange
    repository = ReflectionRepository(db_session)

    # Act
    result = repository.find_by_plan_id("non-existent-plan-id")

    # Assert
    assert result is None


def test_delete_existing(db_session: Session, sample_reflection: ReflectionModel):
    """検証: DBから削除される"""
    # Arrange
    repository = ReflectionRepository(db_session)
    reflection_id = sample_reflection.id

    # Act
    repository.delete(reflection_id)

    # Assert
    result = repository.find_by_id(reflection_id)
    assert result is None


def test_delete_not_found(db_session: Session):
    """検証: エラーが発生しない"""
    # Arrange
    repository = ReflectionRepository(db_session)

    # Act & Assert（例外が発生しないことを確認）
    repository.delete("non-existent-id")


def test_photo_conversion_with_image_analysis(db_session: Session, sample_travel_plan: TravelPlanModel):
    """検証: ImageAnalysisの全フィールドが正しく保存・復元される"""
    # Arrange
    repository = ReflectionRepository(db_session)
    photo1 = Photo(
        id="photo_osaka_001",
        url="https://example.com/photos/osaka_castle.jpg",
        analysis=ImageAnalysis(
            detected_spots=["大阪城"],
            historical_elements=["天守閣", "石垣", "堀"],
            landmarks=["大阪城天守閣"],
            confidence=0.92,
        ),
        user_description="大阪城の壮大さに感動",
    )
    photo2 = Photo(
        id="photo_osaka_002",
        url="https://example.com/photos/osaka_moat.jpg",
        analysis=ImageAnalysis(
            detected_spots=["大阪城"],
            historical_elements=["堀", "石垣"],
            landmarks=[],
            confidence=0.85,
        ),
        user_description="堀と石垣の美しさ",
    )
    reflection = Reflection(
        id=None,
        plan_id=sample_travel_plan.id,
        user_id="test_user_003",
        photos=[photo1, photo2],
        user_notes="大阪城の歴史的価値を学びました",
    )

    # Act
    saved = repository.save(reflection)
    retrieved = repository.find_by_id(saved.id)

    # Assert
    assert retrieved is not None
    assert len(retrieved.photos) == 2

    # photo1の検証
    retrieved_photo1 = retrieved.photos[0]
    assert retrieved_photo1.id == "photo_osaka_001"
    assert retrieved_photo1.url == "https://example.com/photos/osaka_castle.jpg"
    assert retrieved_photo1.user_description == "大阪城の壮大さに感動"
    assert retrieved_photo1.analysis.detected_spots == ("大阪城",)
    assert retrieved_photo1.analysis.historical_elements == ("天守閣", "石垣", "堀")
    assert retrieved_photo1.analysis.landmarks == ("大阪城天守閣",)
    assert retrieved_photo1.analysis.confidence == 0.92

    # photo2の検証
    retrieved_photo2 = retrieved.photos[1]
    assert retrieved_photo2.id == "photo_osaka_002"
    assert retrieved_photo2.url == "https://example.com/photos/osaka_moat.jpg"
    assert retrieved_photo2.user_description == "堀と石垣の美しさ"
    assert retrieved_photo2.analysis.detected_spots == ("大阪城",)
    assert retrieved_photo2.analysis.historical_elements == ("堀", "石垣")
    assert retrieved_photo2.analysis.landmarks == ()
    assert retrieved_photo2.analysis.confidence == 0.85


def test_save_update_not_found(db_session: Session):
    """検証: ValueErrorがraiseされる"""
    # Arrange
    repository = ReflectionRepository(db_session)
    photo = Photo(
        id="test_photo",
        url="https://example.com/test.jpg",
        analysis=ImageAnalysis(
            detected_spots=["テスト"],
            historical_elements=[],
            landmarks=[],
            confidence=0.5,
        ),
    )
    reflection = Reflection(
        id="non-existent-id",
        plan_id="dummy-plan-id",
        user_id="test_user_999",
        photos=[photo],
        user_notes="存在しない振り返り",
    )

    # Act & Assert
    with pytest.raises(ValueError, match="Reflection not found"):
        repository.save(reflection)
