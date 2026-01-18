"""TravelPlanユースケースのテスト"""

import pytest
from sqlalchemy.orm import Session

from app.application.use_cases.create_travel_plan import CreateTravelPlanUseCase
from app.application.use_cases.get_travel_plan import (
    GetTravelPlanUseCase,
    ListTravelPlansUseCase,
)
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.infrastructure.repositories.travel_plan_repository import TravelPlanRepository


def test_create_travel_plan_use_case_creates_plan(db_session: Session):
    """前提条件: 有効な旅行計画入力
    実行: 旅行計画を作成する
    検証: DTOと永続化結果が一致する
    """
    # 前提条件: 有効な旅行計画入力
    repository = TravelPlanRepository(db_session)
    use_case = CreateTravelPlanUseCase(repository)
    spots = [
        {
            "name": "清水寺",
            "location": {"lat": 34.9949, "lng": 135.785},
            "description": "京都を代表する寺院",
            "userNotes": "早朝訪問予定",
        }
    ]

    # 実行: 旅行計画を作成する
    dto = use_case.execute(
        user_id="test_user_001",
        title="京都歴史ツアー",
        destination="京都",
        spots=spots,
    )

    # 検証: DTOと永続化結果が一致する
    assert dto.id
    assert dto.user_id == "test_user_001"
    assert dto.title == "京都歴史ツアー"
    assert dto.destination == "京都"
    assert dto.status == "planning"
    assert len(dto.spots) == 1
    assert dto.spots[0]["name"] == "清水寺"
    assert dto.spots[0]["id"]

    saved_plan = repository.find_by_id(dto.id)
    assert saved_plan is not None
    assert saved_plan.title == "京都歴史ツアー"


def test_create_travel_plan_use_case_invalid_spot_raises(db_session: Session):
    """前提条件: スポット名が空の入力
    実行: 旅行計画を作成する
    検証: ValueErrorが発生する
    """
    # 前提条件: スポット名が空の入力
    repository = TravelPlanRepository(db_session)
    use_case = CreateTravelPlanUseCase(repository)
    spots = [
        {
            "name": " ",
            "location": {"lat": 34.9949, "lng": 135.785},
        }
    ]

    # 実行 & 検証: ValueErrorが発生する
    with pytest.raises(ValueError, match="spots\\[0\\].name is required"):
        use_case.execute(
            user_id="test_user_001",
            title="京都歴史ツアー",
            destination="京都",
            spots=spots,
        )


def test_create_travel_plan_use_case_allows_empty_spots(db_session: Session):
    """前提条件: spotsが空配列の入力
    実行: 旅行計画を作成する
    検証: spotsが空配列で保存される
    """
    # 前提条件: spotsが空配列の入力
    repository = TravelPlanRepository(db_session)
    use_case = CreateTravelPlanUseCase(repository)

    # 実行: 旅行計画を作成する
    dto = use_case.execute(
        user_id="test_user_002",
        title="札幌散策プラン",
        destination="札幌",
        spots=[],
    )

    # 検証: spotsが空配列で保存される
    assert dto.id
    assert dto.spots == []


def test_get_travel_plan_use_case_returns_plan(db_session: Session, sample_travel_plan):
    """前提条件: サンプルTravelPlanが存在する
    実行: 旅行計画を取得する
    検証: DTOの内容が一致する
    """
    # 前提条件: サンプルTravelPlanが存在する
    repository = TravelPlanRepository(db_session)
    use_case = GetTravelPlanUseCase(repository)

    # 実行: 旅行計画を取得する
    dto = use_case.execute(plan_id=sample_travel_plan.id)

    # 検証: DTOの内容が一致する
    assert dto.id == sample_travel_plan.id
    assert dto.title == sample_travel_plan.title
    assert dto.destination == sample_travel_plan.destination
    assert len(dto.spots) == len(sample_travel_plan.spots)


def test_get_travel_plan_use_case_not_found(db_session: Session):
    """前提条件: 存在しない旅行計画ID
    実行: 旅行計画を取得する
    検証: TravelPlanNotFoundErrorが発生する
    """
    # 前提条件: 存在しない旅行計画ID
    repository = TravelPlanRepository(db_session)
    use_case = GetTravelPlanUseCase(repository)

    # 実行 & 検証: TravelPlanNotFoundErrorが発生する
    with pytest.raises(TravelPlanNotFoundError):
        use_case.execute(plan_id="non-existent-id")


def test_list_travel_plans_use_case_returns_list(
    db_session: Session, sample_travel_plan
):
    """前提条件: ユーザーの旅行計画が存在する
    実行: 旅行計画一覧を取得する
    検証: 旅行計画が返る
    """
    # 前提条件: ユーザーの旅行計画が存在する
    repository = TravelPlanRepository(db_session)
    use_case = ListTravelPlansUseCase(repository)

    # 実行: 旅行計画一覧を取得する
    dtos = use_case.execute(user_id=sample_travel_plan.user_id)

    # 検証: 旅行計画が返る
    assert isinstance(dtos, list)
    assert len(dtos) >= 1
    assert any(dto.id == sample_travel_plan.id for dto in dtos)
