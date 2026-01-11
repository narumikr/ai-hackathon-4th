"""旅行計画APIエンドポイント."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.use_cases.create_travel_plan import CreateTravelPlanUseCase
from app.application.use_cases.get_travel_plan import (
    GetTravelPlanUseCase,
    ListTravelPlansUseCase,
)
from app.application.use_cases.update_travel_plan import UpdateTravelPlanUseCase
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.infrastructure.persistence.database import get_db
from app.infrastructure.repositories.travel_plan_repository import TravelPlanRepository
from app.interfaces.schemas.travel_plan import (
    CreateTravelPlanRequest,
    TravelPlanResponse,
    UpdateTravelPlanRequest,
)

router = APIRouter(prefix="/travel-plans", tags=["travel-plans"])


def get_repository(db: Session = Depends(get_db)) -> TravelPlanRepository:  # noqa: B008
    """TravelPlanRepositoryの依存性注入.

    Args:
        db: SQLAlchemyセッション

    Returns:
        TravelPlanRepository: リポジトリインスタンス
    """
    return TravelPlanRepository(db)


@router.post(
    "",
    response_model=TravelPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="旅行計画を作成",
)
def create_travel_plan(
    request: CreateTravelPlanRequest,
    repository: TravelPlanRepository = Depends(get_repository),  # noqa: B008
) -> TravelPlanResponse:
    """旅行計画を作成する.

    Args:
        request: 旅行計画作成リクエスト
        repository: TravelPlanRepository

    Returns:
        TravelPlanResponse: 作成された旅行計画

    Raises:
        HTTPException: バリデーションエラー（400）
    """
    use_case = CreateTravelPlanUseCase(repository)

    # Pydanticスキーマ → 辞書変換
    spots_dict = [spot.model_dump(by_alias=True) for spot in request.spots]

    try:
        dto = use_case.execute(
            user_id=request.user_id,
            title=request.title,
            destination=request.destination,
            spots=spots_dict,
        )
        return TravelPlanResponse(**dto.__dict__)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "",
    response_model=list[TravelPlanResponse],
    summary="旅行計画一覧を取得",
)
def list_travel_plans(
    user_id: str,
    repository: TravelPlanRepository = Depends(get_repository),  # noqa: B008
) -> list[TravelPlanResponse]:
    """ユーザーの旅行計画一覧を取得する.

    Args:
        user_id: ユーザーID
        repository: TravelPlanRepository

    Returns:
        list[TravelPlanResponse]: 旅行計画リスト
    """
    use_case = ListTravelPlansUseCase(repository)
    dtos = use_case.execute(user_id=user_id)
    return [TravelPlanResponse(**dto.__dict__) for dto in dtos]


@router.get(
    "/{plan_id}",
    response_model=TravelPlanResponse,
    summary="旅行計画を取得",
)
def get_travel_plan(
    plan_id: str,
    repository: TravelPlanRepository = Depends(get_repository),  # noqa: B008
) -> TravelPlanResponse:
    """旅行計画を取得する.

    Args:
        plan_id: 旅行計画ID
        repository: TravelPlanRepository

    Returns:
        TravelPlanResponse: 旅行計画

    Raises:
        HTTPException: 旅行計画が見つからない（404）
    """
    use_case = GetTravelPlanUseCase(repository)

    try:
        dto = use_case.execute(plan_id=plan_id)
        return TravelPlanResponse(**dto.__dict__)
    except TravelPlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        ) from e


@router.put(
    "/{plan_id}",
    response_model=TravelPlanResponse,
    summary="旅行計画を更新",
)
def update_travel_plan(
    plan_id: str,
    request: UpdateTravelPlanRequest,
    repository: TravelPlanRepository = Depends(get_repository),  # noqa: B008
) -> TravelPlanResponse:
    """旅行計画を更新する.

    Args:
        plan_id: 旅行計画ID
        request: 旅行計画更新リクエスト
        repository: TravelPlanRepository

    Returns:
        TravelPlanResponse: 更新された旅行計画

    Raises:
        HTTPException: 旅行計画が見つからない（404）、バリデーションエラー（400）
    """
    use_case = UpdateTravelPlanUseCase(repository)

    # Pydanticスキーマ → 辞書変換
    spots_dict = None
    if request.spots is not None:
        spots_dict = [spot.model_dump(by_alias=True) for spot in request.spots]

    try:
        dto = use_case.execute(
            plan_id=plan_id,
            title=request.title,
            destination=request.destination,
            spots=spots_dict,
        )
        return TravelPlanResponse(**dto.__dict__)
    except TravelPlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
