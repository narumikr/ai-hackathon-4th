"""TravelPlan集約のプロパティテスト."""

from datetime import datetime

from hypothesis import given, strategies as st

from app.domain.travel_plan.entity import TouristSpot, TravelPlan
from app.domain.travel_plan.value_objects import Location, PlanStatus


def _non_empty_printable_text(min_size: int = 1, max_size: int = 50) -> st.SearchStrategy[str]:
    return st.text(
        alphabet=st.characters(min_codepoint=32, max_codepoint=126),
        min_size=min_size,
        max_size=max_size,
    ).filter(lambda value: value.strip() != "")


@st.composite
def _locations(draw: st.DrawFn) -> Location:
    lat = draw(
        st.floats(
            min_value=-90,
            max_value=90,
            allow_nan=False,
            allow_infinity=False,
        )
    )
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
    spot_id = draw(_non_empty_printable_text(max_size=40))
    name = draw(_non_empty_printable_text(max_size=40))
    location = draw(_locations())
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
    spots=st.lists(_tourist_spots(), min_size=1, max_size=5),
)
def test_travel_plan_property_travel_information_storage(
    user_id: str,
    title: str,
    destination: str,
    spots: list[TouristSpot],
) -> None:
    """Property 1: 旅行情報が保持されることを検証する."""
    plan = TravelPlan(
        user_id=user_id,
        title=title,
        destination=destination,
        spots=spots,
    )

    assert plan.user_id == user_id
    assert plan.title == title
    assert plan.destination == destination
    assert plan.status == PlanStatus.PLANNING
    assert isinstance(plan.created_at, datetime)
    assert isinstance(plan.updated_at, datetime)
    assert len(plan.spots) == len(spots)

    for stored_spot, original_spot in zip(plan.spots, spots, strict=True):
        assert stored_spot.id == original_spot.id
        assert stored_spot.name == original_spot.name
        assert stored_spot.location.lat == original_spot.location.lat
        assert stored_spot.location.lng == original_spot.location.lng
        assert stored_spot.description == original_spot.description
        assert stored_spot.user_notes == original_spot.user_notes
