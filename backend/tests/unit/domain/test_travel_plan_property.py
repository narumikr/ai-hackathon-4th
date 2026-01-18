"""TravelPlan集約のプロパティテスト。"""

from datetime import UTC, datetime

from hypothesis import given, strategies as st

from app.domain.travel_plan.entity import TouristSpot, TravelPlan
from app.domain.travel_plan.value_objects import GenerationStatus, Location, PlanStatus


def _non_empty_printable_text(min_size: int = 1, max_size: int = 50) -> st.SearchStrategy[str]:
    """非空のprintable文字列を生成するStrategy。

    Hypothesis Strategy: テストデータ生成の設計図

    TravelPlanエンティティのバリデーション要件に適合:
    - 空文字列は拒否される (`not value or not value.strip()`)
    - 空白のみの文字列も拒否される

    Args:
        min_size: 最小文字数
        max_size: 最大文字数

    Returns:
        ASCII 32-126 (printable文字: 画面表示可能な文字) の文字列Strategy
    """
    # ASCII 32-126: スペースから~までのprintable文字のみ
    # 制御文字（改行・タブなど）や拡張ASCII文字を排除し、安定したテストデータを生成
    return st.text(
        alphabet=st.characters(min_codepoint=32, max_codepoint=126),
        min_size=min_size,
        max_size=max_size,
    ).filter(lambda value: value.strip() != "")  # 空白のみの文字列を除外


@st.composite
def _locations(draw: st.DrawFn) -> Location:
    """地理的に有効な位置情報を生成するStrategy。

    Hypothesis Composite Strategy: 複数の値を組み合わせて複雑なオブジェクトを生成

    Location値オブジェクトのバリデーション要件に適合:
    - 緯度: -90度 ≤ lat ≤ 90度
    - 経度: -180度 ≤ lng ≤ 180度
    - NaN/Infinityは不正値として除外

    Args:
        draw: Hypothesisの描画関数

    Returns:
        地理的に有効なLocation値オブジェクト
    """
    # 緯度: -90度（南極）から90度（北極）
    lat = draw(
        st.floats(
            min_value=-90,
            max_value=90,
            allow_nan=False,  # NaNを除外
            allow_infinity=False,  # 無限大を除外
        )
    )
    # 経度: -180度から180度（国際日付変更線）
    lng = draw(
        st.floats(
            min_value=-180,
            max_value=180,
            allow_nan=False,
            allow_infinity=False,
        )
    )
    return Location(lat=lat, lng=lng)


@st.composite
def _tourist_spots(draw: st.DrawFn) -> TouristSpot:
    """観光スポットエンティティを生成するStrategy。

    Hypothesis Composite Strategy: 複数のStrategyを組み合わせてエンティティを生成

    TouristSpotエンティティのバリデーション要件に適合:
    - id: 必須、非空文字列
    - name: 必須、非空文字列
    - location: 必須、Location値オブジェクト
    - description: オプショナル（Noneまたは非空文字列）
    - user_notes: オプショナル（Noneまたは非空文字列）

    Args:
        draw: Hypothesisの描画関数

    Returns:
        有効なTouristSpotエンティティ
    """
    # 必須フィールド
    spot_id = draw(_non_empty_printable_text(max_size=40))
    name = draw(_non_empty_printable_text(max_size=40))
    location = draw(_locations())

    # オプショナルフィールド: Noneまたは非空文字列
    description = draw(st.one_of(st.none(), _non_empty_printable_text(max_size=80)))
    user_notes = draw(st.one_of(st.none(), _non_empty_printable_text(max_size=80)))

    return TouristSpot(
        id=spot_id,
        name=name,
        location=location,
        description=description,
        user_notes=user_notes,
    )


@given(
    user_id=_non_empty_printable_text(max_size=40),
    title=_non_empty_printable_text(max_size=80),
    destination=_non_empty_printable_text(max_size=80),
    # min_size=1: 最低1つのスポットが必要
    # max_size=5: テスト実行時間を考慮し、十分な多様性を保ちつつ現実的な数に制限
    spots=st.lists(_tourist_spots(), min_size=1, max_size=5),
)
def test_travel_plan_property_travel_information_storage(
    user_id: str,
    title: str,
    destination: str,
    spots: list[TouristSpot],
) -> None:
    """Property 1: 旅行情報が保持されることを検証する。

    前提条件:
    - 有効なuser_id、title、destinationが生成される
    - 1〜5個の有効な観光スポットが生成される

    検証項目:
    - すべての入力データが一致して格納される
    - ステータスがPLANNING（デフォルト）になる
    - 日時フィールドが正しく初期化される
    - スポットリストの長さと内容が保持される
    """
    # テスト実行前の時刻を記録（検証用）
    now = datetime.now(UTC)

    # 実行: TravelPlan作成
    plan = TravelPlan(
        user_id=user_id,
        title=title,
        destination=destination,
        spots=spots,
    )

    # 検証: 入力データが一致して格納される
    assert plan.user_id == user_id
    assert plan.title == title
    assert plan.destination == destination
    assert plan.status == PlanStatus.PLANNING  # デフォルトはPLANNING
    assert plan.guide_generation_status == GenerationStatus.NOT_STARTED
    assert plan.reflection_generation_status == GenerationStatus.NOT_STARTED

    # 検証: 日時フィールドが正しく初期化される
    assert isinstance(plan.created_at, datetime)
    assert isinstance(plan.updated_at, datetime)
    # 生成時刻が未来になっていないことを確認（基準時刻以降であることを検証）
    assert plan.created_at >= now
    assert plan.updated_at >= now

    # 検証: スポットリストの長さが保持される
    assert len(plan.spots) == len(spots)

    # 検証: 各スポットの内容が一致して格納される
    for stored_spot, original_spot in zip(plan.spots, spots, strict=True):
        assert stored_spot.id == original_spot.id
        assert stored_spot.name == original_spot.name
        assert stored_spot.location.lat == original_spot.location.lat
        assert stored_spot.location.lng == original_spot.location.lng
        assert stored_spot.description == original_spot.description
        assert stored_spot.user_notes == original_spot.user_notes
