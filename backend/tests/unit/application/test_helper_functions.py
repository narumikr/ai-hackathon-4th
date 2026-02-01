"""ヘルパー関数の動作確認テスト"""

from app.application.use_cases.generate_travel_guide import (
    _create_tourist_spots,
    _detect_new_spots,
    _normalize_spot_name,
)
from app.domain.travel_guide.value_objects import SpotDetail
from app.domain.travel_plan.entity import TouristSpot


def test_normalize_spot_name_trims_whitespace() -> None:
    """空白文字のトリミングを確認"""
    assert _normalize_spot_name("  清水寺  ") == "清水寺"
    assert _normalize_spot_name("金閣寺") == "金閣寺"
    assert _normalize_spot_name("\t二条城\n") == "二条城"


def test_normalize_spot_name_preserves_case() -> None:
    """大文字小文字の保持を確認"""
    assert _normalize_spot_name("Tokyo Tower") == "Tokyo Tower"
    assert _normalize_spot_name("KYOTO") == "KYOTO"


def test_detect_new_spots_with_new_spots() -> None:
    """新規スポットのみの場合"""
    spot_details = [
        SpotDetail(
            spot_name="二条城",
            historical_background="test",
            highlights=("test",),
            recommended_visit_time="test",
            historical_significance="test",
        ),
    ]
    existing_spots = [
        TouristSpot(id="1", name="清水寺", description=None, user_notes=None),
    ]
    result = _detect_new_spots(spot_details, existing_spots)
    assert result == ["二条城"]


def test_detect_new_spots_with_existing_only() -> None:
    """既存スポットのみの場合"""
    spot_details = [
        SpotDetail(
            spot_name="清水寺",
            historical_background="test",
            highlights=("test",),
            recommended_visit_time="test",
            historical_significance="test",
        ),
    ]
    existing_spots = [
        TouristSpot(id="1", name="清水寺", description=None, user_notes=None),
    ]
    result = _detect_new_spots(spot_details, existing_spots)
    assert result == []


def test_detect_new_spots_with_duplicates_in_spot_details() -> None:
    """spotDetails内の重複排除を確認"""
    spot_details = [
        SpotDetail(
            spot_name="二条城",
            historical_background="test",
            highlights=("test",),
            recommended_visit_time="test",
            historical_significance="test",
        ),
        SpotDetail(
            spot_name="二条城",
            historical_background="test2",
            highlights=("test2",),
            recommended_visit_time="test2",
            historical_significance="test2",
        ),
    ]
    existing_spots = [
        TouristSpot(id="1", name="清水寺", description=None, user_notes=None),
    ]
    result = _detect_new_spots(spot_details, existing_spots)
    assert result == ["二条城"]  # 最初の出現のみ


def test_create_tourist_spots_creates_spots() -> None:
    """TouristSpotの作成を確認"""
    new_spot_names = ["二条城", "伏見稲荷大社"]
    result = _create_tourist_spots(new_spot_names)
    assert len(result) == 2
    assert result[0].name == "二条城"
    assert result[1].name == "伏見稲荷大社"
    assert result[0].description is None
    assert result[0].user_notes is None
    assert result[1].description is None
    assert result[1].user_notes is None


def test_create_tourist_spots_generates_unique_ids() -> None:
    """IDの一意性を確認"""
    new_spot_names = ["スポット1", "スポット2", "スポット3"]
    result = _create_tourist_spots(new_spot_names)
    ids = [spot.id for spot in result]
    assert len(ids) == len(set(ids))  # すべてのIDが一意
