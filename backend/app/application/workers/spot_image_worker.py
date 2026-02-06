"""スポット画像生成ワーカー"""

from __future__ import annotations

import asyncio
import logging
import os
import socket
import uuid

from app.application.use_cases.generate_spot_images import GenerateSpotImagesUseCase
from app.config.settings import get_settings
from app.infrastructure.persistence.database import SessionLocal
from app.infrastructure.repositories.spot_image_job_repository import SpotImageJobRepository
from app.infrastructure.repositories.travel_guide_repository import TravelGuideRepository
from app.interfaces.api.dependencies import get_ai_service, get_storage_service

logger = logging.getLogger(__name__)


def _build_worker_id() -> str:
    hostname = socket.gethostname()
    suffix = uuid.uuid4().hex[:8]
    return f"{hostname}-{suffix}"


def _apply_settings_env() -> None:
    settings = get_settings()
    if settings.google_application_credentials:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
    if settings.google_cloud_project:
        os.environ["GOOGLE_CLOUD_PROJECT"] = settings.google_cloud_project
    if settings.google_cloud_location:
        os.environ["GOOGLE_CLOUD_LOCATION"] = settings.google_cloud_location


async def _process_job(job, *, ai_service, storage_service) -> None:
    session = SessionLocal()
    try:
        guide_repository = TravelGuideRepository(session)
        job_repository = SpotImageJobRepository(session)
        use_case = GenerateSpotImagesUseCase(
            ai_service=ai_service,
            storage_service=storage_service,
            guide_repository=guide_repository,
        )

        image_url, status, error_message = await use_case.generate_for_spot(
            plan_id=job.plan_id,
            spot_name=job.spot_name,
        )

        if status == "succeeded":
            job_repository.mark_succeeded(job.id)
            logger.info(
                "Spot image generation succeeded",
                extra={
                    "plan_id": job.plan_id,
                    "spot_name": job.spot_name,
                    "has_image_url": image_url is not None,
                },
            )
        else:
            job_repository.mark_failed(
                job.id,
                error_message=error_message or "image generation failed",
            )
            logger.warning(
                "Spot image generation failed",
                extra={
                    "plan_id": job.plan_id,
                    "spot_name": job.spot_name,
                },
            )
    except Exception as exc:
        logger.exception(
            "Unexpected error while processing spot image job",
            extra={
                "plan_id": getattr(job, "plan_id", None),
                "spot_name": getattr(job, "spot_name", None),
                "job_id": getattr(job, "id", None),
            },
        )
        try:
            session.rollback()
            job_repository.mark_failed(
                job.id,
                error_message=str(exc) or "unexpected error",
            )
        except Exception:
            logger.exception(
                "Failed to update job status to failed",
                extra={
                    "job_id": getattr(job, "id", None),
                },
            )
    finally:
        session.close()


async def run_worker() -> None:
    _apply_settings_env()
    settings = get_settings()
    max_concurrent = settings.image_generation_max_concurrent
    if max_concurrent <= 0:
        raise ValueError("image_generation_max_concurrent must be a positive integer.")

    worker_id = _build_worker_id()
    logger.info("Spot image worker started", extra={"worker_id": worker_id})

    ai_service = get_ai_service()
    storage_service = get_storage_service()

    semaphore = asyncio.Semaphore(max_concurrent)
    poll_interval = 1.0

    while True:
        session = SessionLocal()
        try:
            job_repository = SpotImageJobRepository(session)
            jobs = job_repository.fetch_and_lock_jobs(max_concurrent, worker_id=worker_id)
        finally:
            session.close()

        if not jobs:
            await asyncio.sleep(poll_interval)
            continue

        async def _run(job):
            async with semaphore:
                await _process_job(job, ai_service=ai_service, storage_service=storage_service)

        await asyncio.gather(*[_run(job) for job in jobs])


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
