"""TravelGuide Aggregateのプロパティテスト"""

from __future__ import annotations

from hypothesis import given, strategies as st

from app.domain.travel_guide.services import TravelGuideComposer
from app.domain.travel_guide.value_objects import Checkpoint, HistoricalEvent, MapData, SpotDetail


def _non_empty_printable_text(min_size: int = 1, max_size: int = 50) -> st.SearchStrategy[str]:
    """非空のprintable文字列を生成するStrategy

    TravelGuide集約の必須フィールドのバリデーション要件に適合:
    - 空文字列は拒否される
    - 空白のみの文字列も拒否される
    """
    return st.text(
        alphabet=st.characters(min_codepoint=32, max_codepoint=126),
        min_size=min_size,
        max_size=max_size,
    ).filter(lambda value: value.strip() != "")


@st.composite
def _spot_details_list(draw: st.DrawFn) -> list[SpotDetail]:
    """ユニークなspot_nameを持つSpotDetailのリストを生成するStrategy"""
    spot_names = draw(
        st.lists(
            _non_empty_printable_text(max_size=40),
            min_size=1,
            max_size=5,
            unique=True,
        )
    )
    details: list[SpotDetail] = []
    for name in spot_names:
        details.append(
            SpotDetail(
                spot_name=name,
                historical_background=draw(_non_empty_printable_text(max_size=120)),
                highlights=tuple(
                    draw(
                        st.lists(
                            _non_empty_printable_text(max_size=40),
                            min_size=1,
                            max_size=4,
                        )
                    )
                ),
                recommended_visit_time=draw(_non_empty_printable_text(max_size=40)),
                historical_significance=draw(_non_empty_printable_text(max_size=120)),
            )
        )
    return details


@st.composite
def _checkpoints(draw: st.DrawFn, spot_names: list[str]) -> list[Checkpoint]:
    """spot_namesに紐づいたCheckpointのリストを生成するStrategy"""
    selected_names = draw(
        st.lists(
            st.sampled_from(spot_names),
            min_size=1,
            max_size=len(spot_names),
            unique=True,
        )
    )
    checkpoints: list[Checkpoint] = []
    for name in selected_names:
        checkpoints.append(
            Checkpoint(
                spot_name=name,
                checkpoints=tuple(
                    draw(
                        st.lists(
                            _non_empty_printable_text(max_size=40),
                            min_size=1,
                            max_size=4,
                        )
                    )
                ),
                historical_context=draw(_non_empty_printable_text(max_size=120)),
            )
        )
    return checkpoints


@st.composite
def _timeline(draw: st.DrawFn, spot_names: list[str]) -> list[HistoricalEvent]:
    """年代順に並んだHistoricalEventのリストを生成するStrategy"""
    years = draw(st.lists(st.integers(min_value=0, max_value=2500), min_size=1, max_size=6))
    sorted_years = sorted(years)
    events: list[HistoricalEvent] = []
    for year in sorted_years:
        related_spots = tuple(
            draw(
                st.lists(
                    st.sampled_from(spot_names),
                    min_size=1,
                    max_size=min(3, len(spot_names)),
                    unique=True,
                )
            )
        )
        events.append(
            HistoricalEvent(
                year=year,
                event=draw(_non_empty_printable_text(max_size=80)),
                significance=draw(_non_empty_printable_text(max_size=120)),
                related_spots=related_spots,
            )
        )
    return events


@st.composite
def _map_data(draw: st.DrawFn, spot_names: list[str]) -> MapData:
    """スポット名に紐づいたMapDataを生成するStrategy"""
    markers_count = draw(st.integers(min_value=1, max_value=min(5, len(spot_names))))
    marker_names = draw(
        st.lists(
            st.sampled_from(spot_names),
            min_size=markers_count,
            max_size=markers_count,
            unique=True,
        )
    )
    markers = []
    for name in marker_names:
        markers.append(
            {
                "lat": draw(st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False)),
                "lng": draw(st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)),
                "label": name,
            }
        )
    return {
        "center": {
            "lat": draw(st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False)),
            "lng": draw(st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False)),
        },
        "zoom": draw(st.integers(min_value=1, max_value=20)),
        "markers": markers,
    }


@st.composite
def _travel_guide_inputs(draw: st.DrawFn) -> tuple[
    str,
    str,
    list[HistoricalEvent],
    list[SpotDetail],
    list[Checkpoint],
    MapData,
    list[str],
]:
    """TravelGuide生成用の整合データをまとめて生成するStrategy"""
    plan_id = draw(_non_empty_printable_text(max_size=40))
    overview = draw(_non_empty_printable_text(max_size=120))
    spot_details = draw(_spot_details_list())
    spot_names = [detail.spot_name for detail in spot_details]
    timeline = draw(_timeline(spot_names))
    checkpoints = draw(_checkpoints(spot_names))
    map_data = draw(_map_data(spot_names))
    return plan_id, overview, timeline, spot_details, checkpoints, map_data, spot_names


@given(data=_travel_guide_inputs())
def test_travel_guide_property_timeline_generation(
    data: tuple[
        str,
        str,
        list[HistoricalEvent],
        list[SpotDetail],
        list[Checkpoint],
        MapData,
        list[str],
    ],
) -> None:
    """Property 3: Timeline generationを検証する"""
    plan_id, overview, timeline, spot_details, checkpoints, map_data, _ = data
    composer = TravelGuideComposer()

    guide = composer.compose(
        plan_id=plan_id,
        overview=overview,
        timeline=timeline,
        spot_details=spot_details,
        checkpoints=checkpoints,
        map_data=map_data,
    )

    years = [event.year for event in guide.timeline]
    assert years == sorted(years)
    assert len(guide.timeline) == len(timeline)
    for stored_event, original_event in zip(guide.timeline, timeline, strict=True):
        assert stored_event.year == original_event.year
        assert stored_event.event == original_event.event
        assert stored_event.significance == original_event.significance
        assert stored_event.related_spots == original_event.related_spots


@given(data=_travel_guide_inputs())
def test_travel_guide_property_map_generation_with_historical_context(
    data: tuple[
        str,
        str,
        list[HistoricalEvent],
        list[SpotDetail],
        list[Checkpoint],
        MapData,
        list[str],
    ],
) -> None:
    """Property 4: Map generation with historical contextを検証する"""
    plan_id, overview, timeline, spot_details, checkpoints, map_data, spot_names = data
    composer = TravelGuideComposer()

    guide = composer.compose(
        plan_id=plan_id,
        overview=overview,
        timeline=timeline,
        spot_details=spot_details,
        checkpoints=checkpoints,
        map_data=map_data,
    )

    stored_map = guide.map_data
    marker_labels = {marker["label"] for marker in stored_map["markers"]}
    assert marker_labels
    assert marker_labels.issubset(set(spot_names))
    assert stored_map == map_data


@given(data=_travel_guide_inputs())
def test_travel_guide_property_travel_guide_completeness(
    data: tuple[
        str,
        str,
        list[HistoricalEvent],
        list[SpotDetail],
        list[Checkpoint],
        MapData,
        list[str],
    ],
) -> None:
    """Property 5: Travel guide completenessを検証する"""
    plan_id, overview, timeline, spot_details, checkpoints, map_data, spot_names = data
    composer = TravelGuideComposer()

    guide = composer.compose(
        plan_id=plan_id,
        overview=overview,
        timeline=timeline,
        spot_details=spot_details,
        checkpoints=checkpoints,
        map_data=map_data,
    )

    assert guide.plan_id == plan_id
    assert guide.overview == overview
    assert guide.timeline == timeline
    assert guide.spot_details == spot_details
    assert guide.checkpoints == checkpoints
    assert guide.map_data == map_data

    assert guide.timeline
    assert guide.spot_details
    assert guide.checkpoints
    assert guide.map_data["markers"]
    assert {detail.spot_name for detail in guide.spot_details} == set(spot_names)
