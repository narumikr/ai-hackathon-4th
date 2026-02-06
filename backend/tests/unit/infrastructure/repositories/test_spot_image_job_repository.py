"""SpotImageJobRepositoryのテスト."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.infrastructure.persistence.models import SpotImageJobModel
from app.infrastructure.repositories.spot_image_job_repository import SpotImageJobRepository


def test_fetch_and_lock_jobs_locks_queued_job(db_session: Session) -> None:
    """queuedジョブを取得してprocessingへ更新することを確認する."""
    # Arrange
    now = datetime.now(UTC)
    job = SpotImageJobModel(
        plan_id="plan-001",
        spot_name="金閣寺",
        status="queued",
        attempts=0,
        max_attempts=3,
        created_at=now,
        updated_at=now,
    )
    db_session.add(job)
    db_session.commit()

    repository = SpotImageJobRepository(db_session)

    # Act
    jobs = repository.fetch_and_lock_jobs(
        10,
        worker_id="worker-1",
        stale_after_seconds=900,
    )

    # Assert
    assert len(jobs) == 1
    assert jobs[0].id == job.id
    assert jobs[0].status == "processing"

    locked = db_session.get(SpotImageJobModel, job.id)
    assert locked is not None
    assert locked.status == "processing"
    assert locked.locked_by == "worker-1"
    assert locked.locked_at is not None


def test_fetch_and_lock_jobs_reclaims_stale_processing_job(db_session: Session) -> None:
    """staleなprocessingジョブを再取得してロックし直すことを確認する."""
    # Arrange
    now = datetime.now(UTC)
    stale_locked_at = now - timedelta(minutes=20)
    job = SpotImageJobModel(
        plan_id="plan-002",
        spot_name="清水寺",
        status="processing",
        attempts=1,
        max_attempts=3,
        created_at=now - timedelta(minutes=30),
        updated_at=now - timedelta(minutes=20),
        locked_at=stale_locked_at,
        locked_by="old-worker",
    )
    db_session.add(job)
    db_session.commit()

    repository = SpotImageJobRepository(db_session)

    # Act
    jobs = repository.fetch_and_lock_jobs(
        10,
        worker_id="worker-2",
        stale_after_seconds=900,
    )

    # Assert
    assert len(jobs) == 1
    assert jobs[0].id == job.id
    assert jobs[0].attempts == 1
    assert jobs[0].status == "processing"

    reclaimed = db_session.get(SpotImageJobModel, job.id)
    assert reclaimed is not None
    assert reclaimed.status == "processing"
    assert reclaimed.attempts == 1
    assert reclaimed.locked_by == "worker-2"
    assert reclaimed.locked_at is not None
    assert reclaimed.locked_at != stale_locked_at


def test_fetch_and_lock_jobs_does_not_reclaim_fresh_processing_job(db_session: Session) -> None:
    """新しいprocessingジョブは再取得しないことを確認する."""
    # Arrange
    now = datetime.now(UTC)
    job = SpotImageJobModel(
        plan_id="plan-003",
        spot_name="伏見稲荷大社",
        status="processing",
        attempts=0,
        max_attempts=3,
        created_at=now - timedelta(minutes=10),
        updated_at=now - timedelta(minutes=5),
        locked_at=now - timedelta(minutes=5),
        locked_by="active-worker",
    )
    db_session.add(job)
    db_session.commit()

    repository = SpotImageJobRepository(db_session)

    # Act
    jobs = repository.fetch_and_lock_jobs(
        10,
        worker_id="worker-3",
        stale_after_seconds=900,
    )

    # Assert
    assert jobs == []

    remained = db_session.get(SpotImageJobModel, job.id)
    assert remained is not None
    assert remained.status == "processing"
    assert remained.locked_by == "active-worker"


def test_fetch_and_lock_jobs_reclaims_processing_job_with_null_locked_at(db_session: Session) -> None:
    """locked_atがNULLのprocessingジョブは異常状態として回収する."""
    # Arrange
    now = datetime.now(UTC)
    job = SpotImageJobModel(
        plan_id="plan-004",
        spot_name="東大寺",
        status="processing",
        attempts=2,
        max_attempts=3,
        created_at=now - timedelta(minutes=40),
        updated_at=now - timedelta(minutes=20),
        locked_at=None,
        locked_by="unknown-worker",
    )
    db_session.add(job)
    db_session.commit()

    repository = SpotImageJobRepository(db_session)

    # Act
    jobs = repository.fetch_and_lock_jobs(
        10,
        worker_id="worker-4",
        stale_after_seconds=900,
    )

    # Assert
    assert len(jobs) == 1
    assert jobs[0].id == job.id
    assert jobs[0].status == "processing"

    reclaimed = db_session.get(SpotImageJobModel, job.id)
    assert reclaimed is not None
    assert reclaimed.locked_by == "worker-4"
    assert reclaimed.locked_at is not None


def test_fetch_and_lock_jobs_raises_when_stale_after_seconds_invalid(db_session: Session) -> None:
    """stale_after_secondsが不正な場合は早期失敗する."""
    repository = SpotImageJobRepository(db_session)

    with pytest.raises(ValueError, match="stale_after_seconds must be a positive integer."):
        repository.fetch_and_lock_jobs(
            10,
            worker_id="worker-5",
            stale_after_seconds=0,
        )
