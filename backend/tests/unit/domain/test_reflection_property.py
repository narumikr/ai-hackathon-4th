"""Reflection Aggregateのプロパティテスト"""

from __future__ import annotations

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from app.domain.reflection.entity import Photo, Reflection
from app.domain.reflection.exceptions import InvalidReflectionError
from app.domain.reflection.services import ReflectionAnalyzer
from app.domain.reflection.value_objects import ImageAnalysis, SpotReflection


def _non_empty_printable_text(min_size: int = 1, max_size: int = 50) -> st.SearchStrategy[str]:
    """非空のprintable文字列を生成するStrategy

    Hypothesis Strategy: テストデータ生成の設計図

    振り返り集約のバリデーション要件に適合:
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
def _image_analysis_inputs(
    draw: st.DrawFn,
) -> tuple[list[str], list[str], list[str], float]:
    """ImageAnalysis用の入力データを生成するStrategy

    Hypothesis Composite Strategy: 複数の値を組み合わせて複雑なデータ構造を生成

    ImageAnalysis値オブジェクトのバリデーション要件に適合:
    - 各リストは空でも可（allow_empty=True）
    - ただし、3つのリスト全てが空になることは許可されない
    - confidence: 0 ≤ confidence ≤ 1
    - NaN/Infinityは不正値として除外

    Args:
        draw: Hypothesisの描画関数

    Returns:
        (detected_spots, historical_elements, landmarks, confidence)のタプル
    """
    # 各リストは0〜5個の要素を持つ（空リストも許可）
    detected_spots = draw(
        st.lists(_non_empty_printable_text(max_size=40), min_size=0, max_size=5)
    )
    historical_elements = draw(
        st.lists(_non_empty_printable_text(max_size=40), min_size=0, max_size=5)
    )
    landmarks = draw(st.lists(_non_empty_printable_text(max_size=40), min_size=0, max_size=5))
    # 少なくとも1つのリストに要素が含まれることを保証
    assume(detected_spots or historical_elements or landmarks)
    # confidence: 0から1の範囲の浮動小数点数
    confidence = draw(
        st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    return detected_spots, historical_elements, landmarks, confidence


@st.composite
def _photo_list(draw: st.DrawFn) -> list[Photo]:
    """ユニークなIDを持つPhotoのリストを生成するStrategy

    Hypothesis Composite Strategy: 複数のPhotoエンティティを組み合わせてリストを生成

    Photoエンティティおよびリストのバリデーション要件に適合:
    - id: 必須、非空文字列、リスト内でユニーク
    - url: 必須、非空文字列
    - analysis: 必須、ImageAnalysis値オブジェクト
    - user_description: オプショナル（Noneまたは非空文字列）
    - リスト内でphoto_idの重複は許可されない

    Args:
        draw: Hypothesisの描画関数

    Returns:
        1〜5個のPhotoを含むリスト
    """
    # ユニークなphoto_idを1〜5個生成
    photo_ids = draw(
        st.lists(
            _non_empty_printable_text(max_size=40),
            min_size=1,
            max_size=5,
            unique=True,  # ID重複を防止
        )
    )
    photos: list[Photo] = []
    for photo_id in photo_ids:
        # 各写真に対してImageAnalysisを生成
        detected_spots, historical_elements, landmarks, confidence = draw(_image_analysis_inputs())
        analysis = ImageAnalysis(
            detected_spots=detected_spots,
            historical_elements=historical_elements,
            landmarks=landmarks,
            confidence=confidence,
        )
        photos.append(
            Photo(
                id=photo_id,
                url=draw(_non_empty_printable_text(max_size=120)),
                analysis=analysis,
                # user_descriptionはオプショナル（Noneまたは非空文字列）
                user_description=draw(
                    st.one_of(st.none(), _non_empty_printable_text(max_size=120))
                ),
            )
        )
    return photos


@st.composite
def _spot_reflections(draw: st.DrawFn) -> list[SpotReflection]:
    """SpotReflectionのリストを生成するStrategy

    Hypothesis Composite Strategy: ユニークなspot_nameを持つSpotReflectionリストを生成

    SpotReflectionおよびReflectionAnalyzerのバリデーション要件に適合:
    - spot_name: 必須、非空文字列、リスト内でユニーク
    - reflection: 必須、非空文字列
    - リスト内でspot_nameの重複は許可されない

    Args:
        draw: Hypothesisの描画関数

    Returns:
        1〜5個のSpotReflectionを含むリスト
    """
    # ユニークなspot_nameを1〜5個生成
    spot_names = draw(
        st.lists(
            _non_empty_printable_text(max_size=40),
            min_size=1,
            max_size=5,
            unique=True,  # spot_name重複を防止
        )
    )
    reflections: list[SpotReflection] = []
    for name in spot_names:
        reflections.append(
            {
                "spot_name": name,
                "reflection": draw(_non_empty_printable_text(max_size=120)),
            }
        )
    return reflections


@given(
    photo_id=_non_empty_printable_text(max_size=40),
    url=_non_empty_printable_text(max_size=120),
    analysis_data=_image_analysis_inputs(),
)
def test_reflection_property_image_analysis_execution(
    photo_id: str,
    url: str,
    analysis_data: tuple[list[str], list[str], list[str], float],
) -> None:
    """Property 10: Image analysis executionを検証する

    前提条件:
    - 有効なphoto_id、url、分析データが生成される
    - 分析データには少なくとも1つの検出結果（detected_spots/historical_elements/landmarks）が含まれる
    - confidenceは0〜1の範囲の浮動小数点数

    検証項目:
    - ImageAnalysisが正しく生成される
    - PhotoにImageAnalysisが正しく格納される
    - 各フィールド（detected_spots, historical_elements, landmarks）がタプルに変換されて保持される
    - 少なくとも1つの分析結果が存在する
    """
    # 入力データの取得
    detected_spots, historical_elements, landmarks, confidence = analysis_data

    # 実行: ImageAnalysis作成
    analysis = ImageAnalysis(
        detected_spots=detected_spots,
        historical_elements=historical_elements,
        landmarks=landmarks,
        confidence=confidence,
    )
    # 実行: Photo作成
    photo = Photo(id=photo_id, url=url, analysis=analysis)

    # 検証1: ImageAnalysisが正しく格納される
    assert photo.analysis == analysis

    # 検証2: detected_spotsがタプルに変換されて保持される
    assert analysis.detected_spots == tuple(detected_spots)

    # 検証3: historical_elementsがタプルに変換されて保持される
    assert analysis.historical_elements == tuple(historical_elements)

    # 検証4: landmarksがタプルに変換されて保持される
    assert analysis.landmarks == tuple(landmarks)

    # 検証5: 少なくとも1つの分析結果が存在する
    assert analysis.detected_spots or analysis.historical_elements or analysis.landmarks


@given(
    plan_id=_non_empty_printable_text(max_size=40),
    user_id=_non_empty_printable_text(max_size=40),
    photos=_photo_list(),
    user_notes=st.one_of(st.none(), _non_empty_printable_text(max_size=120)),
)
def test_reflection_property_information_integration(
    plan_id: str,
    user_id: str,
    photos: list[Photo],
    user_notes: str | None,
) -> None:
    """Property 11: Information integrationを検証する

    前提条件:
    - 有効なplan_id、user_idが生成される
    - 1〜5個のユニークなIDを持つPhotoが生成される
    - user_notesはNoneまたは非空文字列

    検証項目:
    - すべての入力データ（plan_id, user_id, photos, user_notes）が一致して格納される
    - photosの防御的コピーが機能する（外部からの変更を防止）
    """
    # 実行: Reflection作成
    reflection = Reflection(
        plan_id=plan_id,
        user_id=user_id,
        photos=photos,
        user_notes=user_notes,
    )

    # 検証1: plan_idが正しく格納される
    assert reflection.plan_id == plan_id

    # 検証2: user_idが正しく格納される
    assert reflection.user_id == user_id

    # 検証3: user_notesが正しく格納される
    assert reflection.user_notes == user_notes

    # 検証4: photosリストの内容が一致して格納される
    assert reflection.photos == photos

    # 検証5: photosプロパティが防御的コピーを返す（外部変更を防止）
    copied_photos = reflection.photos
    copied_photos.append(photos[0])
    # 内部リストは変更されず、元の長さを保持する
    assert len(reflection.photos) == len(photos)


@given(
    photos=_photo_list(),
    travel_summary=_non_empty_printable_text(max_size=200),
    spot_reflections=_spot_reflections(),
    next_trip_suggestions=st.lists(
        _non_empty_printable_text(max_size=120),
        min_size=1,
        max_size=5,
    ),
)
def test_reflection_property_information_reorganization(
    photos: list[Photo],
    travel_summary: str,
    spot_reflections: list[SpotReflection],
    next_trip_suggestions: list[str],
) -> None:
    """Property 12: Information reorganizationを検証する

    前提条件:
    - 1〜5個のPhotoが生成される
    - 有効なtravel_summaryが生成される
    - 1〜5個のユニークなspot_nameを持つSpotReflectionが生成される
    - 1〜5個のnext_trip_suggestionsが生成される

    検証項目:
    - spot_reflectionsの順序と内容が保持されて再整理される
    - next_trip_suggestionsの順序と内容が保持されて再整理される
    """
    analyzer = ReflectionAnalyzer()

    pamphlet = analyzer.build_pamphlet(
        photos=photos,
        travel_summary=travel_summary,
        spot_reflections=spot_reflections,
        next_trip_suggestions=next_trip_suggestions,
    )

    # 検証1: spot_reflectionsの順序と内容が保持される
    assert pamphlet.spot_reflections == tuple(spot_reflections)

    # 検証2: next_trip_suggestionsの順序と内容が保持される
    assert pamphlet.next_trip_suggestions == tuple(next_trip_suggestions)


@given(
    photos=_photo_list(),
    travel_summary=_non_empty_printable_text(max_size=200),
    spot_reflections=_spot_reflections(),
    next_trip_suggestions=st.lists(
        _non_empty_printable_text(max_size=120),
        min_size=1,
        max_size=5,
    ),
)
def test_reflection_property_reflection_pamphlet_generation(
    photos: list[Photo],
    travel_summary: str,
    spot_reflections: list[SpotReflection],
    next_trip_suggestions: list[str],
) -> None:
    """Property 13: Reflection pamphlet generationを検証する

    前提条件:
    - 1〜5個のPhotoが生成される
    - 有効なtravel_summaryが生成される
    - 1〜5個のユニークなspot_nameを持つSpotReflectionが生成される
    - 1〜5個のnext_trip_suggestionsが生成される

    検証項目:
    - ReflectionPamphletが正しく生成される
    - 入力データ（travel_summary, spot_reflections, next_trip_suggestions）がタプルに変換されて保持される
    - 必須フィールドが非空である（完全性）
    """
    # ReflectionAnalyzerのインスタンスを作成
    analyzer = ReflectionAnalyzer()

    # 実行: ReflectionPamphlet生成
    pamphlet = analyzer.build_pamphlet(
        photos=photos,
        travel_summary=travel_summary,
        spot_reflections=spot_reflections,
        next_trip_suggestions=next_trip_suggestions,
    )

    # 検証1: travel_summaryが正しく保持される
    assert pamphlet.travel_summary == travel_summary

    # 検証2: spot_reflectionsがタプルに変換されて保持される
    assert pamphlet.spot_reflections == tuple(spot_reflections)

    # 検証3: next_trip_suggestionsがタプルに変換されて保持される
    assert pamphlet.next_trip_suggestions == tuple(next_trip_suggestions)

    # 検証4: spot_reflectionsが非空である（完全性）
    assert pamphlet.spot_reflections

    # 検証5: next_trip_suggestionsが非空である（完全性）
    assert pamphlet.next_trip_suggestions


@given(
    photos=_photo_list(),
    travel_summary=_non_empty_printable_text(max_size=200),
    spot_reflections=_spot_reflections(),
    next_trip_suggestions=st.lists(
        _non_empty_printable_text(max_size=120),
        min_size=1,
        max_size=5,
    ),
)
def test_reflection_property_reflection_pamphlet_completeness(
    photos: list[Photo],
    travel_summary: str,
    spot_reflections: list[SpotReflection],
    next_trip_suggestions: list[str],
) -> None:
    """Property 14: Reflection pamphlet completenessを検証する

    前提条件:
    - 1〜5個のPhotoが生成される
    - 有効なtravel_summaryが生成される
    - 1〜5個のユニークなspot_nameを持つSpotReflectionが生成される
    - 1〜5個のnext_trip_suggestionsが生成される

    検証項目:
    - travel_summaryが非空である
    - spot_reflectionsが旅行全体の振り返り情報を含む
    - next_trip_suggestionsが次の旅の提案を含む
    """
    analyzer = ReflectionAnalyzer()

    pamphlet = analyzer.build_pamphlet(
        photos=photos,
        travel_summary=travel_summary,
        spot_reflections=spot_reflections,
        next_trip_suggestions=next_trip_suggestions,
    )

    # 検証1: travel_summaryが非空である
    assert pamphlet.travel_summary.strip()

    # 検証2: spot_reflectionsが非空であり、内容が欠落していない
    assert pamphlet.spot_reflections
    for item in pamphlet.spot_reflections:
        assert item["spot_name"].strip()
        assert item["reflection"].strip()

    # 検証3: next_trip_suggestionsが非空であり、内容が欠落していない
    assert pamphlet.next_trip_suggestions
    for suggestion in pamphlet.next_trip_suggestions:
        assert suggestion.strip()

@given(
    travel_summary=_non_empty_printable_text(max_size=200),
    spot_reflections=_spot_reflections(),
    next_trip_suggestions=st.lists(
        _non_empty_printable_text(max_size=120),
        min_size=1,
        max_size=5,
    ),
)
def test_reflection_property_rejects_empty_photos(
    travel_summary: str,
    spot_reflections: list[SpotReflection],
    next_trip_suggestions: list[str],
) -> None:
    """バリデーションエラーケース: 空のphotosリストを拒否する

    前提条件:
    - photosが空リスト

    検証項目:
    - 空のphotosリストはInvalidReflectionErrorを発生させる
    """
    analyzer = ReflectionAnalyzer()

    # 検証: 空のphotosリストはInvalidReflectionErrorを発生させる
    with pytest.raises(InvalidReflectionError, match="photos must be a non-empty list"):
        analyzer.build_pamphlet(
            photos=[],  # 空リスト
            travel_summary=travel_summary,
            spot_reflections=spot_reflections,
            next_trip_suggestions=next_trip_suggestions,
        )


@given(
    photos=_photo_list(),
    travel_summary=_non_empty_printable_text(max_size=200),
    next_trip_suggestions=st.lists(
        _non_empty_printable_text(max_size=120),
        min_size=1,
        max_size=5,
    ),
)
def test_reflection_property_rejects_empty_spot_reflections(
    photos: list[Photo],
    travel_summary: str,
    next_trip_suggestions: list[str],
) -> None:
    """バリデーションエラーケース: 空のspot_reflectionsリストを拒否する

    前提条件:
    - spot_reflectionsが空リスト

    検証項目:
    - 空のspot_reflectionsリストはInvalidReflectionErrorを発生させる
    """
    analyzer = ReflectionAnalyzer()

    # 検証: 空のspot_reflectionsリストはInvalidReflectionErrorを発生させる
    with pytest.raises(InvalidReflectionError, match="spot_reflections must be a non-empty list"):
        analyzer.build_pamphlet(
            photos=photos,
            travel_summary=travel_summary,
            spot_reflections=[],  # 空リスト
            next_trip_suggestions=next_trip_suggestions,
        )


@given(
    photos=_photo_list(),
    travel_summary=_non_empty_printable_text(max_size=200),
    spot_reflections=_spot_reflections(),
)
def test_reflection_property_rejects_duplicate_spot_names(
    photos: list[Photo],
    travel_summary: str,
    spot_reflections: list[SpotReflection],
) -> None:
    """バリデーションエラーケース: 重複したspot_nameを拒否する

    前提条件:
    - spot_reflectionsに重複したspot_nameが含まれる

    検証項目:
    - 重複したspot_nameを持つspot_reflectionsはInvalidReflectionErrorを発生させる
    """
    analyzer = ReflectionAnalyzer()

    # 前提条件: 最初のspot_reflectionを複製して重複させる
    duplicate_spot_reflections = [spot_reflections[0]] + spot_reflections

    # 検証: 重複したspot_nameを持つspot_reflectionsはInvalidReflectionErrorを発生させる
    with pytest.raises(InvalidReflectionError, match="duplicate spot_name"):
        analyzer.build_pamphlet(
            photos=photos,
            travel_summary=travel_summary,
            spot_reflections=duplicate_spot_reflections,
            next_trip_suggestions=["suggestion1"],
        )


@given(
    photos=_photo_list(),
    travel_summary=_non_empty_printable_text(max_size=200),
    spot_reflections=_spot_reflections(),
)
def test_reflection_property_rejects_empty_next_trip_suggestions(
    photos: list[Photo],
    travel_summary: str,
    spot_reflections: list[SpotReflection],
) -> None:
    """バリデーションエラーケース: 空のnext_trip_suggestionsリストを拒否する

    前提条件:
    - next_trip_suggestionsが空リスト

    検証項目:
    - 空のnext_trip_suggestionsリストはInvalidReflectionErrorを発生させる
    """
    analyzer = ReflectionAnalyzer()

    # 検証: 空のnext_trip_suggestionsリストはInvalidReflectionErrorを発生させる
    with pytest.raises(
        InvalidReflectionError, match="next_trip_suggestions must be a non-empty list"
    ):
        analyzer.build_pamphlet(
            photos=photos,
            travel_summary=travel_summary,
            spot_reflections=spot_reflections,
            next_trip_suggestions=[],  # 空リスト
        )
