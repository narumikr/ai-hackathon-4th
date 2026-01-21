"""振り返りAPIエンドポイント"""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from app.application.dto.travel_plan_dto import TravelPlanDTO
from app.application.ports.ai_service import IAIService
from app.application.use_cases.analyze_photos import AnalyzePhotosUseCase
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
from app.interfaces.schemas.reflection import CreateReflectionRequest
from app.interfaces.schemas.travel_plan import TravelPlanResponse

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
    response_model=TravelPlanResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="振り返り生成を開始",
)
async def create_reflection(
    request: CreateReflectionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),  # noqa: B008
    ai_service: IAIService = Depends(get_ai_service_dependency),  # noqa: B008
) -> TravelPlanResponse:
    """振り返り生成を開始する"""
    plan_repository = TravelPlanRepository(db)
    travel_plan = plan_repository.find_by_id(request.plan_id)
    if travel_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {request.plan_id}",
        )

    if travel_plan.user_id != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id does not match the travel plan owner.",
        )

    if travel_plan.reflection_generation_status == GenerationStatus.PROCESSING:
        dto = TravelPlanDTO.from_entity(travel_plan)
        return TravelPlanResponse(**dto.__dict__)

    _update_reflection_status_or_raise(
        plan_repository,
        request.plan_id,
        GenerationStatus.PROCESSING,
    )

    photo_inputs = [photo.model_dump(by_alias=True) for photo in request.photos]

    background_tasks.add_task(
        _run_reflection_generation,
        request.plan_id,
        request.user_id,
        request.user_notes,
        photo_inputs,
        ai_service,
        db.get_bind(),
    )

    updated_plan = plan_repository.find_by_id(request.plan_id)
    dto = TravelPlanDTO.from_entity(updated_plan or travel_plan)
    return TravelPlanResponse(**dto.__dict__)


async def _run_reflection_generation(
    plan_id: str,
    user_id: str,
    user_notes: str,
    photos: list[dict],
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

        analyze_use_case = AnalyzePhotosUseCase(
            plan_repository=plan_repository,
            reflection_repository=reflection_repository,
            ai_service=ai_service,
        )
        await analyze_use_case.execute(
            plan_id=plan_id,
            user_id=user_id,
            photos=photos,
        )

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
