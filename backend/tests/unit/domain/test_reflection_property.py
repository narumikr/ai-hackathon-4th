"""Reflection Aggregateのプロパティテスト"""

from __future__ import annotations

from hypothesis import assume, given
from hypothesis import strategies as st

from app.domain.reflection.entity import Photo, Reflection
from app.domain.reflection.services import ReflectionAnalyzer
from app.domain.reflection.value_objects import ImageAnalysis, SpotReflection


def _non_empty_printable_text(min_size: int = 1, max_size: int = 50) -> st.SearchStrategy[str]:
    """非空のprintable文字列を生成するStrategy"""
    return st.text(
        alphabet=st.characters(min_codepoint=32, max_codepoint=126),
        min_size=min_size,
        max_size=max_size,
    ).filter(lambda value: value.strip() != "")


@st.composite
def _image_analysis_inputs(
    draw: st.DrawFn,
) -> tuple[list[str], list[str], list[str], float]:
    """ImageAnalysis用の入力データを生成するStrategy"""
    detected_spots = draw(
        st.lists(_non_empty_printable_text(max_size=40), min_size=0, max_size=5)
    )
    historical_elements = draw(
        st.lists(_non_empty_printable_text(max_size=40), min_size=0, max_size=5)
    )
    landmarks = draw(st.lists(_non_empty_printable_text(max_size=40), min_size=0, max_size=5))
    assume(detected_spots or historical_elements or landmarks)
    confidence = draw(
        st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
    )
    return detected_spots, historical_elements, landmarks, confidence


@st.composite
def _photo_list(draw: st.DrawFn) -> list[Photo]:
    """ユニークなIDを持つPhotoのリストを生成するStrategy"""
    photo_ids = draw(
        st.lists(
            _non_empty_printable_text(max_size=40),
            min_size=1,
            max_size=5,
            unique=True,
        )
    )
    photos: list[Photo] = []
    for photo_id in photo_ids:
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
                user_description=draw(
                    st.one_of(st.none(), _non_empty_printable_text(max_size=120))
                ),
            )
        )
    return photos


@st.composite
def _spot_reflections(draw: st.DrawFn) -> list[SpotReflection]:
    """SpotReflectionのリストを生成するStrategy"""
    spot_names = draw(
        st.lists(
            _non_empty_printable_text(max_size=40),
            min_size=1,
            max_size=5,
            unique=True,
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
    """Property 10: Image analysis executionを検証する"""
    detected_spots, historical_elements, landmarks, confidence = analysis_data
    analysis = ImageAnalysis(
        detected_spots=detected_spots,
        historical_elements=historical_elements,
        landmarks=landmarks,
        confidence=confidence,
    )
    photo = Photo(id=photo_id, url=url, analysis=analysis)

    assert photo.analysis == analysis
    assert analysis.detected_spots == tuple(detected_spots)
    assert analysis.historical_elements == tuple(historical_elements)
    assert analysis.landmarks == tuple(landmarks)
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
    """Property 11: Information integrationを検証する"""
    reflection = Reflection(
        plan_id=plan_id,
        user_id=user_id,
        photos=photos,
        user_notes=user_notes,
    )

    assert reflection.plan_id == plan_id
    assert reflection.user_id == user_id
    assert reflection.user_notes == user_notes
    assert reflection.photos == photos

    copied_photos = reflection.photos
    copied_photos.append(photos[0])
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
def test_reflection_property_reflection_pamphlet_generation(
    photos: list[Photo],
    travel_summary: str,
    spot_reflections: list[SpotReflection],
    next_trip_suggestions: list[str],
) -> None:
    """Property 13: Reflection pamphlet generationを検証する"""
    analyzer = ReflectionAnalyzer()

    pamphlet = analyzer.build_pamphlet(
        photos=photos,
        travel_summary=travel_summary,
        spot_reflections=spot_reflections,
        next_trip_suggestions=next_trip_suggestions,
    )

    assert pamphlet.travel_summary == travel_summary
    assert pamphlet.spot_reflections == tuple(spot_reflections)
    assert pamphlet.next_trip_suggestions == tuple(next_trip_suggestions)
    assert pamphlet.spot_reflections
    assert pamphlet.next_trip_suggestions
