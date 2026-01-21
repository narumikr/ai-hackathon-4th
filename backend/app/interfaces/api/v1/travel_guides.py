"""旅行ガイドAPIエンドポイント"""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from app.application.dto.travel_plan_dto import TravelPlanDTO
from app.application.ports.ai_service import IAIService
from app.application.use_cases.generate_travel_guide import GenerateTravelGuideUseCase
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.value_objects import GenerationStatus
from app.infrastructure.persistence.database import get_db
from app.infrastructure.repositories.travel_guide_repository import TravelGuideRepository
from app.infrastructure.repositories.travel_plan_repository import TravelPlanRepository
from app.interfaces.api.dependencies import get_ai_service_dependency
from app.interfaces.schemas.travel_guide import GenerateTravelGuideRequest
from app.interfaces.schemas.travel_plan import TravelPlanResponse

logger = logging.getLogger(__name__)

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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=TravelPlanResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="旅行ガイド生成を開始",
)
async def generate_travel_guide(
    request: GenerateTravelGuideRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),  # noqa: B008
    ai_service: IAIService = Depends(get_ai_service_dependency),  # noqa: B008
) -> TravelPlanResponse:
    """旅行ガイド生成を開始する

    Args:
        request: 旅行ガイド生成リクエスト
        background_tasks: バックグラウンドタスク
        db: SQLAlchemyセッション
        ai_service: AIサービス

    Returns:
        TravelPlanResponse: 旅行計画（生成中ステータス）

    Raises:
        HTTPException: 旅行計画が見つからない（404）、バリデーションエラー（400）など
    """
    plan_id = request.plan_id

    plan_repository = TravelPlanRepository(db)
    travel_plan = plan_repository.find_by_id(plan_id)
    if travel_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        )

    if travel_plan.guide_generation_status == GenerationStatus.PROCESSING:
        dto = TravelPlanDTO.from_entity(travel_plan)
        return TravelPlanResponse(**dto.__dict__)

    _update_guide_status_or_raise(
        plan_repository,
        plan_id,
        GenerationStatus.PROCESSING,
    )

    background_tasks.add_task(_run_travel_guide_generation, plan_id, ai_service, db.get_bind())

    updated_plan = plan_repository.find_by_id(plan_id)
    dto = TravelPlanDTO.from_entity(updated_plan or travel_plan)
    return TravelPlanResponse(**dto.__dict__)


async def _run_travel_guide_generation(plan_id: str, ai_service: IAIService, bind) -> None:
    """旅行ガイド生成をバックグラウンドで実行する"""
    session_maker = sessionmaker(autocommit=False, autoflush=False, bind=bind)
    db = session_maker()
    try:
        plan_repository = TravelPlanRepository(db)
        guide_repository = TravelGuideRepository(db)
        use_case = GenerateTravelGuideUseCase(
            plan_repository=plan_repository,
            guide_repository=guide_repository,
            ai_service=ai_service,
        )
        await use_case.execute(plan_id=plan_id)
    except Exception:
        logger.exception("Failed to generate travel guide", extra={"plan_id": plan_id})
        try:
            failure_db = session_maker()
            try:
                plan_repository = TravelPlanRepository(failure_db)
                _update_guide_status(plan_repository, plan_id, GenerationStatus.FAILED)
            finally:
                failure_db.close()
        except Exception:
            logger.exception(
                "Failed to update travel guide status to failed", extra={"plan_id": plan_id}
            )
        raise
    finally:
        db.close()
