"""振り返りAPIエンドポイント"""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session, sessionmaker

from app.application.ports.ai_service import IAIService
from app.application.use_cases.generate_reflection import GenerateReflectionPamphletUseCase
from app.domain.reflection.exceptions import ReflectionNotFoundError
from app.domain.travel_guide.exceptions import TravelGuideNotFoundError
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.value_objects import GenerationStatus
from app.infrastructure.persistence.database import get_db
from app.infrastructure.repositories.reflection_repository import ReflectionRepository
from app.infrastructure.repositories.travel_guide_repository import TravelGuideRepository
from app.infrastructure.repositories.travel_plan_repository import TravelPlanRepository
from app.interfaces.api.dependencies import get_ai_service_dependency
from app.interfaces.middleware.auth import UserContext, require_auth
from app.interfaces.schemas.reflection import CreateReflectionRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reflections", tags=["reflections"])


def _update_reflection_status(
    plan_repository: TravelPlanRepository,
    plan_id: str,
    status_value: GenerationStatus,
    *,
    commit: bool = True,
) -> None:
    """振り返り生成ステータスを更新する"""
    travel_plan = plan_repository.find_by_id(plan_id)
    if travel_plan is None:
        raise TravelPlanNotFoundError(plan_id)
    travel_plan.update_generation_statuses(reflection_status=status_value)
    plan_repository.save(travel_plan, commit=commit)


def _update_reflection_status_or_raise(
    plan_repository: TravelPlanRepository,
    plan_id: str,
    status_value: GenerationStatus,
    *,
    commit: bool = True,
) -> None:
    """振り返り生成ステータスを更新して失敗時はHTTP例外に変換する"""
    try:
        _update_reflection_status(plan_repository, plan_id, status_value, commit=commit)
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
    status_code=status.HTTP_204_NO_CONTENT,
    summary="振り返り生成を開始",
)
async def create_reflection(
    request: CreateReflectionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),  # noqa: B008
    ai_service: IAIService = Depends(get_ai_service_dependency),  # noqa: B008
    auth: UserContext = Depends(require_auth),  # noqa: B008
) -> Response:
    """振り返り生成を開始する
    
    Args:
        request: 振り返り生成リクエスト
        background_tasks: バックグラウンドタスク
        db: SQLAlchemyセッション
        ai_service: AIサービス
        auth: 認証ユーザー（Firebase ID token検証済み）
    """
    plan_repository = TravelPlanRepository(db)
    travel_plan = plan_repository.find_by_id(request.plan_id)
    if travel_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {request.plan_id}",
        )

    if travel_plan.user_id != auth.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this travel plan.",
        )

    guide_repository = TravelGuideRepository(db)
    travel_guide = guide_repository.find_by_plan_id(request.plan_id)
    if travel_guide is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Travel guide has not been generated for this plan.",
        )

    if travel_plan.reflection_generation_status == GenerationStatus.PROCESSING:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    reflection_repository = ReflectionRepository(db)
    existing_reflection = reflection_repository.find_by_plan_id(request.plan_id)
    if existing_reflection is None or not existing_reflection.photos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Reflection photos have not been registered for this plan.",
        )

    _update_reflection_status_or_raise(
        plan_repository,
        request.plan_id,
        GenerationStatus.PROCESSING,
    )

    background_tasks.add_task(
        _run_reflection_generation,
        request.plan_id,
        auth.uid,
        request.user_notes,
        ai_service,
        db.get_bind(),
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def _run_reflection_generation(
    plan_id: str,
    user_id: str,
    user_notes: str | None,
    ai_service: IAIService,
    bind,
) -> None:
    """振り返り生成をバックグラウンドで実行する"""
    session_maker = sessionmaker(autocommit=False, autoflush=False, bind=bind)
    db = session_maker()
    try:
        plan_repository = TravelPlanRepository(db)
        guide_repository = TravelGuideRepository(db)
        reflection_repository = ReflectionRepository(db)

        generate_use_case = GenerateReflectionPamphletUseCase(
            plan_repository=plan_repository,
            guide_repository=guide_repository,
            reflection_repository=reflection_repository,
            ai_service=ai_service,
        )
        await generate_use_case.execute(
            plan_id=plan_id,
            user_id=user_id,
            user_notes=user_notes,
        )
    except (
        TravelPlanNotFoundError,
        TravelGuideNotFoundError,
        ReflectionNotFoundError,
        ValueError,
    ):
        logger.exception("Failed to generate reflection", extra={"plan_id": plan_id})
        try:
            failure_db = session_maker()
            try:
                plan_repository = TravelPlanRepository(failure_db)
                _update_reflection_status(
                    plan_repository,
                    plan_id,
                    GenerationStatus.FAILED,
                )
            finally:
                failure_db.close()
        except Exception:
            logger.exception(
                "Failed to update reflection status to failed", extra={"plan_id": plan_id}
            )
        raise
    except Exception:
        logger.exception("Failed to generate reflection", extra={"plan_id": plan_id})
        try:
            failure_db = session_maker()
            try:
                plan_repository = TravelPlanRepository(failure_db)
                _update_reflection_status(
                    plan_repository,
                    plan_id,
                    GenerationStatus.FAILED,
                )
            finally:
                failure_db.close()
        except Exception:
            logger.exception(
                "Failed to update reflection status to failed", extra={"plan_id": plan_id}
            )
        raise
    finally:
        db.close()
