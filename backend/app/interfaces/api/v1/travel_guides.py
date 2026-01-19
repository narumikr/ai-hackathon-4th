"""旅行ガイドAPIエンドポイント"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.dto.travel_guide_dto import TravelGuideDTO
from app.application.ports.ai_service import IAIService
from app.application.use_cases.generate_travel_guide import GenerateTravelGuideUseCase
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.value_objects import GenerationStatus
from app.infrastructure.ai.exceptions import (
    AIServiceConnectionError,
    AIServiceInvalidRequestError,
    AIServiceQuotaExceededError,
)
from app.infrastructure.persistence.database import get_db
from app.infrastructure.repositories.travel_guide_repository import TravelGuideRepository
from app.infrastructure.repositories.travel_plan_repository import TravelPlanRepository
from app.interfaces.api.dependencies import get_ai_service_dependency
from app.interfaces.schemas.travel_guide import (
    GenerateTravelGuideRequest,
    TravelGuideResponse,
)

router = APIRouter(prefix="/travel-guides", tags=["travel-guides"])


def get_plan_repository(db: Session = Depends(get_db)) -> TravelPlanRepository:  # noqa: B008
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


def _update_guide_status(
    plan_repository: TravelPlanRepository,
    plan_id: str,
    status_value: GenerationStatus,
    *,
    commit: bool = True,
) -> None:
    """旅行ガイド生成ステータスを更新する"""
    travel_plan = plan_repository.find_by_id(plan_id)
    if travel_plan is None:
        raise TravelPlanNotFoundError(plan_id)
    travel_plan.update_generation_statuses(guide_status=status_value)
    plan_repository.save(travel_plan, commit=commit)


def _update_guide_status_or_raise(
    plan_repository: TravelPlanRepository,
    plan_id: str,
    status_value: GenerationStatus,
    *,
    commit: bool = True,
) -> None:
    """旅行ガイド生成ステータスを更新して失敗時はHTTP例外に変換する"""
    try:
        _update_guide_status(plan_repository, plan_id, status_value, commit=commit)
    except TravelPlanNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{guide_id}",
    response_model=TravelGuideResponse,
    summary="旅行ガイドを取得",
)
def get_travel_guide(
    guide_id: str,
    repository: TravelGuideRepository = Depends(get_guide_repository),  # noqa: B008
) -> TravelGuideResponse:
    """旅行ガイドを取得する

    Args:
        guide_id: 旅行ガイドID
        repository: TravelGuideRepository

    Returns:
        TravelGuideResponse: 旅行ガイド

    Raises:
        HTTPException: 旅行ガイドが見つからない（404）
    """
    guide = repository.find_by_id(guide_id)
    if guide is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel guide not found: {guide_id}",
        )

    dto = TravelGuideDTO.from_entity(guide)
    return TravelGuideResponse(**dto.__dict__)


@router.post(
    "",
    response_model=TravelGuideResponse,
    status_code=status.HTTP_201_CREATED,
    summary="旅行ガイドを生成",
)
async def generate_travel_guide(
    request: GenerateTravelGuideRequest,
    db: Session = Depends(get_db),  # noqa: B008
    ai_service: IAIService = Depends(get_ai_service_dependency),  # noqa: B008
) -> TravelGuideResponse:
    """旅行ガイドを生成する

    Args:
        request: 旅行ガイド生成リクエスト
        db: SQLAlchemyセッション
        ai_service: AIサービス

    Returns:
        TravelGuideResponse: 生成された旅行ガイド

    Raises:
        HTTPException: 旅行計画が見つからない（404）、バリデーションエラー（400）など
    """
    plan_id = request.plan_id

    plan_repository = TravelPlanRepository(db)
    guide_repository = TravelGuideRepository(db)
    if plan_repository.find_by_id(plan_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        )

    use_case = GenerateTravelGuideUseCase(
        plan_repository=plan_repository,
        guide_repository=guide_repository,
        ai_service=ai_service,
    )

    try:
        dto = await use_case.execute(plan_id=plan_id, commit=False)
        db.commit()
        return TravelGuideResponse(**dto.__dict__)
    except TravelPlanNotFoundError as exc:
        db.rollback()
        _update_guide_status_or_raise(
            plan_repository,
            plan_id,
            GenerationStatus.FAILED,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        ) from exc
    except AIServiceInvalidRequestError as exc:
        db.rollback()
        _update_guide_status_or_raise(
            plan_repository,
            plan_id,
            GenerationStatus.FAILED,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except AIServiceQuotaExceededError as exc:
        db.rollback()
        _update_guide_status_or_raise(
            plan_repository,
            plan_id,
            GenerationStatus.FAILED,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc
    except AIServiceConnectionError as exc:
        db.rollback()
        _update_guide_status_or_raise(
            plan_repository,
            plan_id,
            GenerationStatus.FAILED,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        db.rollback()
        _update_guide_status_or_raise(
            plan_repository,
            plan_id,
            GenerationStatus.FAILED,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
