"""旅行計画APIエンドポイント"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.application.use_cases.create_travel_plan import CreateTravelPlanUseCase
from app.application.use_cases.delete_travel_plan import DeleteTravelPlanUseCase
from app.application.use_cases.get_travel_plan import (
    GetTravelPlanUseCase,
    ListTravelPlansUseCase,
)
from app.application.use_cases.update_travel_plan import UpdateTravelPlanUseCase
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.infrastructure.persistence.database import get_db
from app.infrastructure.repositories.reflection_repository import ReflectionRepository
from app.infrastructure.repositories.travel_guide_repository import TravelGuideRepository
from app.infrastructure.repositories.travel_plan_repository import TravelPlanRepository
from app.interfaces.middleware.auth import UserContext, require_auth
from app.interfaces.schemas.travel_plan import (
    CreateTravelPlanRequest,
    TravelPlanListResponse,
    TravelPlanResponse,
    UpdateTravelPlanRequest,
)

router = APIRouter(prefix="/travel-plans", tags=["travel-plans"])


def get_repository(db: Session = Depends(get_db)) -> TravelPlanRepository:  # noqa: B008
    """TravelPlanRepositoryの依存性注入

    Args:
        db: SQLAlchemyセッション

    Returns:
        TravelPlanRepository: リポジトリインスタンス
    """
    return TravelPlanRepository(db)


def get_guide_repository(db: Session = Depends(get_db)) -> TravelGuideRepository:  # noqa: B008
    """TravelGuideRepositoryの依存性注入

    Args:
        db: SQLAlchemyセッション

    Returns:
        TravelGuideRepository: リポジトリインスタンス
    """
    return TravelGuideRepository(db)


def get_reflection_repository(
    db: Session = Depends(get_db),  # noqa: B008
) -> ReflectionRepository:  # noqa: B008
    """ReflectionRepositoryの依存性注入

    Args:
        db: SQLAlchemyセッション

    Returns:
        ReflectionRepository: リポジトリインスタンス
    """
    return ReflectionRepository(db)


@router.post(
    "",
    response_model=TravelPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="旅行計画を作成",
)
def create_travel_plan(
    request: CreateTravelPlanRequest,
    repository: TravelPlanRepository = Depends(get_repository),  # noqa: B008
    auth: UserContext = Depends(require_auth),  # noqa: B008
) -> TravelPlanResponse:
    """旅行計画を作成する

    Args:
        request: 旅行計画作成リクエスト
        repository: TravelPlanRepository
        auth: 認証ユーザー（Firebase ID token検証済み）

    Returns:
        TravelPlanResponse: 作成された旅行計画

    Raises:
        HTTPException: バリデーションエラー（400）、認証エラー（401）
    """
    use_case = CreateTravelPlanUseCase(repository)

    # Pydanticスキーマ → 辞書変換
    spots_dict = [spot.model_dump(by_alias=True) for spot in request.spots]

    try:
        dto = use_case.execute(
            user_id=auth.uid,
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
    response_model=list[TravelPlanListResponse],
    summary="旅行計画一覧を取得",
)
def list_travel_plans(
    repository: TravelPlanRepository = Depends(get_repository),  # noqa: B008
    auth: UserContext = Depends(require_auth),  # noqa: B008
) -> list[TravelPlanListResponse]:
    """ユーザーの旅行計画一覧を取得する

    Args:
        repository: TravelPlanRepository
        auth: 認証ユーザー（Firebase ID token検証済み）

    Returns:
        list[TravelPlanListResponse]: 旅行計画リスト
    """
    use_case = ListTravelPlansUseCase(repository)
    try:
        dtos = use_case.execute(user_id=auth.uid)
        return [TravelPlanListResponse.from_dto(dto) for dto in dtos]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/{plan_id}",
    response_model=TravelPlanResponse,
    summary="旅行計画を取得",
)
def get_travel_plan(
    plan_id: str,
    repository: TravelPlanRepository = Depends(get_repository),  # noqa: B008
    guide_repository: TravelGuideRepository = Depends(get_guide_repository),  # noqa: B008
    reflection_repository: ReflectionRepository = Depends(get_reflection_repository),  # noqa: B008
    auth: UserContext = Depends(require_auth),  # noqa: B008
) -> TravelPlanResponse:
    """旅行計画を取得する

    Args:
        plan_id: 旅行計画ID
        repository: TravelPlanRepository
        auth: 認証ユーザー（Firebase ID token検証済み）

    Returns:
        TravelPlanResponse: 旅行計画

    Raises:
        HTTPException: 旅行計画が見つからない（404）、認証エラー（401）
    """
    use_case = GetTravelPlanUseCase(
        repository,
        guide_repository=guide_repository,
        reflection_repository=reflection_repository,
    )

    try:
        dto = use_case.execute(plan_id=plan_id)
        return TravelPlanResponse(**dto.__dict__)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
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
    auth: UserContext = Depends(require_auth),  # noqa: B008
) -> TravelPlanResponse:
    """旅行計画を更新する

    Args:
        plan_id: 旅行計画ID
        request: 旅行計画更新リクエスト
        repository: TravelPlanRepository
        auth: 認証ユーザー（Firebase ID token検証済み）

    Returns:
        TravelPlanResponse: 更新された旅行計画

    Raises:
        HTTPException: 旅行計画が見つからない（404）、バリデーションエラー（400）、認証エラー（401）
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
            status=request.status,
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


@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="旅行計画を削除",
)
def delete_travel_plan(
    plan_id: str,
    repository: TravelPlanRepository = Depends(get_repository),  # noqa: B008
    auth: UserContext = Depends(require_auth),  # noqa: B008
) -> Response:
    """旅行計画を削除する

    Args:
        plan_id: 旅行計画ID
        repository: TravelPlanRepository
        auth: 認証ユーザー（Firebase ID token検証済み）

    Returns:
        Response: 204 No Content

    Raises:
        HTTPException: 旅行計画が見つからない（404）、認証エラー（401）
    """
    use_case = DeleteTravelPlanUseCase(repository)

    try:
        use_case.execute(plan_id=plan_id)
    except TravelPlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        ) from e

    return Response(status_code=status.HTTP_204_NO_CONTENT)
