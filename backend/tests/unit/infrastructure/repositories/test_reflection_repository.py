"""振り返りリポジトリのテスト"""

import pytest
from sqlalchemy.orm import Session

from app.domain.reflection.entity import Photo, Reflection
from app.domain.reflection.value_objects import ImageAnalysis, ReflectionPamphlet
from app.infrastructure.persistence.models import ReflectionModel, TravelPlanModel
from app.infrastructure.repositories.reflection_repository import ReflectionRepository


def test_save_new_reflection(db_session: Session, sample_travel_plan: TravelPlanModel):
    """前提: 新規振り返りエンティティを作成（idはNone）
    検証: IDが自動生成される、photosがJSON型で保存される
    """
    # Arrange
    repository = ReflectionRepository(db_session)
    photo = Photo(
        id="photo_nara_001",
        spot_id="spot-001",
        url="https://example.com/photos/todaiji.jpg",
        analysis=ImageAnalysis(
            description="東大寺の大仏殿は奈良時代の寺院建築として知られる。"
            "出典: 東大寺公式サイト https://www.todaiji.or.jp/contents/ 。",
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


def test_save_reflection_with_pamphlet(db_session: Session, sample_travel_plan: TravelPlanModel):
    """前提: パンフレット付きの振り返りを作成する
    検証: パンフレットが保存され、復元できる
    """
    repository = ReflectionRepository(db_session)
    photo = Photo(
        id="photo_tokyo_001",
        spot_id="spot-001",
        url="https://example.com/photos/tokyo_castle.jpg",
        analysis=ImageAnalysis(
            description="江戸城の写真。天守台が写っており、江戸城跡の特徴的な石垣が確認できる。"
        ),
        user_description="江戸城跡の広さに驚いた",
    )
    pamphlet = ReflectionPamphlet(
        travel_summary="江戸の歴史を感じる旅だった。",
        spot_reflections=[{"spot_name": "江戸城", "reflection": "石垣の壮大さが印象的だった。"}],
        next_trip_suggestions=["日光東照宮を巡る旅"],
    )
    reflection = Reflection(
        id=None,
        plan_id=sample_travel_plan.id,
        user_id="test_user_004",
        photos=[photo],
        user_notes="江戸の面影が残る旅だった",
        pamphlet=pamphlet,
    )

    saved = repository.save(reflection)
    retrieved = repository.find_by_id(saved.id)

    assert retrieved is not None
    assert retrieved.pamphlet is not None
    assert retrieved.pamphlet.travel_summary == "江戸の歴史を感じる旅だった。"
    assert retrieved.pamphlet.spot_reflections[0]["spot_name"] == "江戸城"
    assert retrieved.pamphlet.next_trip_suggestions == ("日光東照宮を巡る旅",)


def test_save_update_reflection(db_session: Session, sample_reflection: ReflectionModel):
    """前提: 既存振り返りを取得し、update_notes()で変更
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
    """検証: 振り返りエンティティが返却される、PhotoとImageAnalysisが正しく復元される"""
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
    """検証: 振り返りエンティティが返却される"""
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


def test_photo_conversion_with_image_analysis(
    db_session: Session, sample_travel_plan: TravelPlanModel
):
    """検証: ImageAnalysisの説明文が正しく保存・復元される"""
    # Arrange
    repository = ReflectionRepository(db_session)
    photo1 = Photo(
        id="photo_osaka_001",
        spot_id="spot-001",
        url="https://example.com/photos/osaka_castle.jpg",
        analysis=ImageAnalysis(
            description="大阪城天守閣は豊臣秀吉ゆかりの城として知られ、"
            "石垣や堀が歴史的特徴となっている。"
            "出典: 大阪城公式サイト https://www.osakacastle.net/ 。",
        ),
        user_description="大阪城の壮大さに感動",
    )
    photo2 = Photo(
        id="photo_osaka_002",
        spot_id="spot-001",
        url="https://example.com/photos/osaka_moat.jpg",
        analysis=ImageAnalysis(
            description="大阪城の堀と石垣は防御構造として重要で、"
            "当時の築城技術を示している。"
            "出典: 大阪城公式サイト https://www.osakacastle.net/ 。",
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
    assert retrieved_photo1.spot_id == "spot-001"
    assert retrieved_photo1.url == "https://example.com/photos/osaka_castle.jpg"
    assert retrieved_photo1.user_description == "大阪城の壮大さに感動"
    assert retrieved_photo1.analysis.description.strip()

    # photo2の検証
    retrieved_photo2 = retrieved.photos[1]
    assert retrieved_photo2.id == "photo_osaka_002"
    assert retrieved_photo2.spot_id == "spot-001"
    assert retrieved_photo2.url == "https://example.com/photos/osaka_moat.jpg"
    assert retrieved_photo2.user_description == "堀と石垣の美しさ"
    assert retrieved_photo2.analysis.description.strip()


def test_save_update_not_found(db_session: Session):
    """検証: ValueErrorがraiseされる"""
    # Arrange
    repository = ReflectionRepository(db_session)
    photo = Photo(
        id="test_photo",
        spot_id="spot-001",
        url="https://example.com/test.jpg",
        analysis=ImageAnalysis(
            description="テスト用の歴史的説明文。出典: テスト https://example.com/test-source 。",
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
