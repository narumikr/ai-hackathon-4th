"""スポット画像生成ジョブリポジトリの実装"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.application.ports.spot_image_job_repository import (
    ISpotImageJobRepository,
    SpotImageJobRecord,
)
from app.infrastructure.persistence.models import SpotImageJobModel


class SpotImageJobRepository(ISpotImageJobRepository):
    """スポット画像生成ジョブリポジトリ"""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_jobs(
        self,
        plan_id: str,
        spot_names: list[str],
        *,
        max_attempts: int = 3,
        commit: bool = True,
    ) -> int:
        if not plan_id or not plan_id.strip():
            raise ValueError("plan_id is required and must not be empty.")
        if max_attempts <= 0:
            raise ValueError("max_attempts must be a positive integer.")
        if not spot_names:
            return 0

        normalized_names = []
        for name in spot_names:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("spot_name must be a non-empty string.")
            normalized_names.append(name)

        # 重複を排除しつつ順序を保持する
        unique_names = list(dict.fromkeys(normalized_names))

        existing = (
            self._session.query(SpotImageJobModel.spot_name)
            .filter(SpotImageJobModel.plan_id == plan_id)
            .filter(SpotImageJobModel.spot_name.in_(unique_names))
            .all()
        )
        existing_names = {row[0] for row in existing}
        new_names = [name for name in unique_names if name not in existing_names]
        if not new_names:
            return 0

        now = datetime.now(UTC)
        jobs = [
            SpotImageJobModel(
                plan_id=plan_id,
                spot_name=spot_name,
                status="queued",
                attempts=0,
                max_attempts=max_attempts,
                created_at=now,
                updated_at=now,
            )
            for spot_name in new_names
        ]
        self._session.add_all(jobs)
        if commit:
            self._session.commit()
        else:
            self._session.flush()
        return len(jobs)

    def fetch_and_lock_jobs(self, limit: int, *, worker_id: str) -> list[SpotImageJobRecord]:
        if limit <= 0:
            raise ValueError("limit must be a positive integer.")
        if not worker_id or not worker_id.strip():
            raise ValueError("worker_id is required and must not be empty.")

        now = datetime.now(UTC)
        with self._session.begin():
            jobs = (
                self._session.query(SpotImageJobModel)
                .filter(SpotImageJobModel.status == "queued")
                .order_by(SpotImageJobModel.created_at.asc())
                .limit(limit)
                .with_for_update(skip_locked=True)
                .all()
            )
            for job in jobs:
                job.status = "processing"
                job.locked_at = now
                job.locked_by = worker_id
                job.updated_at = now

        return [
            SpotImageJobRecord(
                id=job.id,
                plan_id=job.plan_id,
                spot_name=job.spot_name,
                attempts=job.attempts,
                max_attempts=job.max_attempts,
                status=job.status,
            )
            for job in jobs
        ]

    def mark_succeeded(self, job_id: str) -> None:
        if not job_id or not job_id.strip():
            raise ValueError("job_id is required and must not be empty.")

        job = self._session.get(SpotImageJobModel, job_id)
        if job is None:
            raise ValueError(f"SpotImageJob not found: {job_id}")

        job.status = "succeeded"
        job.updated_at = datetime.now(UTC)
        job.locked_at = None
        job.locked_by = None
        self._session.commit()

    def mark_failed(self, job_id: str, *, error_message: str) -> None:
        if not job_id or not job_id.strip():
            raise ValueError("job_id is required and must not be empty.")
        if not error_message or not error_message.strip():
            raise ValueError("error_message is required and must not be empty.")

        job = self._session.get(SpotImageJobModel, job_id)
        if job is None:
            raise ValueError(f"SpotImageJob not found: {job_id}")

        job.attempts += 1
        job.last_error = error_message
        if job.attempts < job.max_attempts:
            job.status = "queued"
        else:
            job.status = "failed"
        job.updated_at = datetime.now(UTC)
        job.locked_at = None
        job.locked_by = None
        self._session.commit()
