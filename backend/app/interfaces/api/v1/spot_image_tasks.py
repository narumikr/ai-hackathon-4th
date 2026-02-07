"""Cloud Tasksからのスポット画像タスク受信API."""

from __future__ import annotations

import logging
import socket
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.use_cases.generate_spot_images import GenerateSpotImagesUseCase
from app.infrastructure.persistence.database import get_db
from app.infrastructure.repositories.spot_image_job_repository import SpotImageJobRepository
from app.infrastructure.repositories.travel_guide_repository import TravelGuideRepository
from app.interfaces.api.dependencies import get_image_generation_service, get_storage_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal/tasks", tags=["spot-image-tasks"])


class SpotImageTaskRequest(BaseModel):
    """スポット画像タスクの受信ペイロード."""

    plan_id: str
    spot_name: str


def _build_worker_id() -> str:
    hostname = socket.gethostname()
    suffix = uuid.uuid4().hex[:8]
    return f"cloud-task-{hostname}-{suffix}"


@router.post(
    "/spot-image",
    status_code=status.HTTP_200_OK,
    summary="Cloud Tasksからスポット画像生成を実行",
)
async def run_spot_image_task(
    request: SpotImageTaskRequest,
    db: Session = Depends(get_db),  # noqa: B008
) -> dict[str, str]:
    plan_id = request.plan_id.strip()
    spot_name = request.spot_name.strip()
    if not plan_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="plan_id is required.")
    if not spot_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="spot_name is required."
        )

    worker_id = _build_worker_id()
    job_repository = SpotImageJobRepository(db)
    claimed_job = job_repository.claim_job(
        plan_id=plan_id, spot_name=spot_name, worker_id=worker_id
    )
    if claimed_job is None:
        logger.info(
            "Spot image task skipped because no claimable job exists",
            extra={"plan_id": plan_id, "spot_name": spot_name},
        )
        return {"status": "skipped"}

    guide_repository = TravelGuideRepository(db)
    use_case = GenerateSpotImagesUseCase(
        image_generation_service=get_image_generation_service(),
        storage_service=get_storage_service(),
        guide_repository=guide_repository,
    )
    try:
        _, result_status, error_message = await use_case.generate_for_spot(
            plan_id=plan_id,
            spot_name=spot_name,
        )
        if result_status == "succeeded":
            job_repository.mark_succeeded(claimed_job.id)
            return {"status": "succeeded"}

        job_repository.mark_failed(
            claimed_job.id,
            error_message=error_message or "image generation failed",
        )
        # 再試行ポリシーはCloud Tasks側に委譲するため5xxを返す
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="spot image generation failed",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Unexpected error while handling spot image task",
            extra={"plan_id": plan_id, "spot_name": spot_name, "job_id": claimed_job.id},
        )
        job_repository.mark_failed(claimed_job.id, error_message=str(exc) or "unexpected error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="spot image generation failed unexpectedly",
        ) from exc
