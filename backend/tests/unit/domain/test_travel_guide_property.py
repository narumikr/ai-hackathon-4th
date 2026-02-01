"""TravelGuide Aggregateのプロパティテスト"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.domain.travel_guide.exceptions import InvalidTravelGuideError
from app.domain.travel_guide.services import TravelGuideComposer
from app.domain.travel_guide.value_objects import Checkpoint, HistoricalEvent, SpotDetail

# TravelGuide生成用の入力データの型定義
type TravelGuideInputs = tuple[
    str,  # plan_id
    str,  # overview
    list[HistoricalEvent],  # timeline
    list[SpotDetail],  # spot_details
    list[Checkpoint],  # checkpoints
    list[str],  # spot_names
]


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
def _travel_guide_inputs(draw: st.DrawFn) -> TravelGuideInputs:
    """TravelGuide生成用の整合データをまとめて生成するStrategy"""
    plan_id = draw(_non_empty_printable_text(max_size=40))
    overview = draw(_non_empty_printable_text(max_size=120))
    spot_details = draw(_spot_details_list())
    spot_names = [detail.spot_name for detail in spot_details]
    timeline = draw(_timeline(spot_names))
    checkpoints = draw(_checkpoints(spot_names))
    return plan_id, overview, timeline, spot_details, checkpoints, spot_names


@given(data=_travel_guide_inputs())
def test_travel_guide_property_timeline_generation(data: TravelGuideInputs) -> None:
    """Property 3: Timeline generationを検証する"""
    plan_id, overview, timeline, spot_details, checkpoints, _ = data
    composer = TravelGuideComposer()

    guide = composer.compose(
        plan_id=plan_id,
        overview=overview,
        timeline=timeline,
        spot_details=spot_details,
        checkpoints=checkpoints,
    )

    # 検証1: タイムラインが年代順にソートされていること
    years = [event.year for event in guide.timeline]
    assert years == sorted(years)

    # 検証2: タイムラインの長さが保持されていること
    assert len(guide.timeline) == len(timeline)

    # 検証3: 各イベントのフィールドが正しく保持されていること
    for stored_event, original_event in zip(guide.timeline, timeline, strict=True):
        assert stored_event.year == original_event.year
        assert stored_event.event == original_event.event
        assert stored_event.significance == original_event.significance
        assert stored_event.related_spots == original_event.related_spots


@given(data=_travel_guide_inputs())
def test_travel_guide_property_travel_guide_completeness(data: TravelGuideInputs) -> None:
    """Property 5: Travel guide completenessを検証する"""
    plan_id, overview, timeline, spot_details, checkpoints, spot_names = data
    composer = TravelGuideComposer()

    guide = composer.compose(
        plan_id=plan_id,
        overview=overview,
        timeline=timeline,
        spot_details=spot_details,
        checkpoints=checkpoints,
    )

    # 検証1: 全フィールドが正しく保持されていること
    assert guide.plan_id == plan_id
    assert guide.overview == overview
    assert guide.timeline == timeline
    assert guide.spot_details == spot_details
    assert guide.checkpoints == checkpoints

    # 検証2: 必須フィールドが非空であること（完全性）
    assert guide.timeline
    assert guide.spot_details
    assert guide.checkpoints

    # 検証3: spot_namesの一貫性が保たれていること
    assert {detail.spot_name for detail in guide.spot_details} == set(spot_names)


@given(data=_travel_guide_inputs())
def test_travel_guide_property_checkpoint_list_inclusion(data: TravelGuideInputs) -> None:
    """Property 8: Checkpoint list inclusionを検証する"""
    plan_id, overview, timeline, spot_details, checkpoints, spot_names = data
    composer = TravelGuideComposer()
    spot_name_set = set(spot_names)

    guide = composer.compose(
        plan_id=plan_id,
        overview=overview,
        timeline=timeline,
        spot_details=spot_details,
        checkpoints=checkpoints,
    )

    # 検証1: チェックポイントリストが存在すること
    assert guide.checkpoints

    # 検証2: チェックポイントがspot_detailsに含まれるスポットを参照していること
    checkpoint_spot_names = {checkpoint.spot_name for checkpoint in guide.checkpoints}
    assert checkpoint_spot_names.issubset(spot_name_set)

    # 検証3: チェックポイントの内容が保持されていること
    assert len(guide.checkpoints) == len(checkpoints)
    for stored_checkpoint, original_checkpoint in zip(guide.checkpoints, checkpoints, strict=True):
        assert stored_checkpoint.spot_name == original_checkpoint.spot_name
        assert stored_checkpoint.checkpoints == original_checkpoint.checkpoints
        assert stored_checkpoint.historical_context == original_checkpoint.historical_context


@given(data=_travel_guide_inputs())
def test_travel_guide_property_content_integration_completeness(
    data: TravelGuideInputs,
) -> None:
    """Property 9: Content integration completenessを検証する"""
    plan_id, overview, timeline, spot_details, checkpoints, spot_names = data
    composer = TravelGuideComposer()
    spot_name_set = set(spot_names)

    guide = composer.compose(
        plan_id=plan_id,
        overview=overview,
        timeline=timeline,
        spot_details=spot_details,
        checkpoints=checkpoints,
    )

    # 検証1: タイムラインがガイドに統合されていること
    assert guide.timeline
    for event in guide.timeline:
        assert set(event.related_spots).issubset(spot_name_set)

    # 検証2: 歴史背景と見どころがガイドに統合されていること
    assert guide.spot_details
    for detail in guide.spot_details:
        assert detail.historical_background.strip()
        assert detail.highlights
        for highlight in detail.highlights:
            assert highlight.strip()


@given(data=_travel_guide_inputs())
def test_travel_guide_property_rejects_duplicate_spot_names(data: TravelGuideInputs) -> None:
    """バリデーションエラーケース: 重複したspot_nameを持つspot_detailsを拒否する"""
    plan_id, overview, timeline, spot_details, checkpoints, _ = data
    composer = TravelGuideComposer()

    # 前提条件: 最初のspot_detailを複製して重複させる
    duplicate_spot_details = [spot_details[0]] + spot_details

    # 検証: 重複したspot_nameを持つspot_detailsはInvalidTravelGuideErrorを発生させる
    with pytest.raises(InvalidTravelGuideError, match="duplicate spot_name"):
        composer.compose(
            plan_id=plan_id,
            overview=overview,
            timeline=timeline,
            spot_details=duplicate_spot_details,
            checkpoints=checkpoints,
        )


@given(data=_travel_guide_inputs())
def test_travel_guide_property_rejects_invalid_checkpoint_spot_name(
    data: TravelGuideInputs,
) -> None:
    """バリデーションエラーケース: 存在しないspot_nameを参照するcheckpointを拒否する"""
    plan_id, overview, timeline, spot_details, checkpoints, _ = data
    composer = TravelGuideComposer()

    # 前提条件: 存在しないspot_nameを参照するcheckpointを追加
    invalid_checkpoint = Checkpoint(
        spot_name="NonExistentSpot",
        checkpoints=("checkpoint1",),
        historical_context="context",
    )
    invalid_checkpoints = checkpoints + [invalid_checkpoint]

    # 検証: 存在しないspot_nameを参照するcheckpointはInvalidTravelGuideErrorを発生させる
    with pytest.raises(InvalidTravelGuideError, match="checkpoint spot_name not found"):
        composer.compose(
            plan_id=plan_id,
            overview=overview,
            timeline=timeline,
            spot_details=spot_details,
            checkpoints=invalid_checkpoints,
        )


@given(data=_travel_guide_inputs())
def test_travel_guide_property_rejects_invalid_timeline_related_spots(
    data: TravelGuideInputs,
) -> None:
    """バリデーションエラーケース: 存在しないspot_nameを参照するtimeline.related_spotsを拒否する"""
    plan_id, overview, timeline, spot_details, checkpoints, _ = data
    composer = TravelGuideComposer()

    # 前提条件: 存在しないspot_nameを参照するtimelineイベントを追加
    invalid_event = HistoricalEvent(
        year=9999,
        event="Invalid event",
        significance="significance",
        related_spots=("NonExistentSpot",),
    )
    invalid_timeline = timeline + [invalid_event]

    # 検証: 存在しないspot_nameを参照するrelated_spotsはInvalidTravelGuideErrorを発生させる
    with pytest.raises(
        InvalidTravelGuideError, match="timeline related_spots contains unsupported names"
    ):
        composer.compose(
            plan_id=plan_id,
            overview=overview,
            timeline=invalid_timeline,
            spot_details=spot_details,
            checkpoints=checkpoints,
        )
