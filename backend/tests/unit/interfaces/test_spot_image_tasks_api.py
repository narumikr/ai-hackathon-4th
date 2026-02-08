"""スポット画像タスクAPIのユニットテスト."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.interfaces.api.v1 import spot_image_tasks


class _FakeJob:
    def __init__(self, job_id: str) -> None:
        self.id = job_id


class _ClaimingJobRepository:
    def __init__(self, _db) -> None:
        self.succeeded_job_ids: list[str] = []
        self.failed_job_ids: list[str] = []
        self.requeued_job_ids: list[str] = []

    def claim_job(self, plan_id: str, spot_name: str, *, worker_id: str):
        return _FakeJob("job-1")

    def mark_succeeded(self, job_id: str) -> None:
        self.succeeded_job_ids.append(job_id)

    def mark_failed(self, job_id: str, *, error_message: str):
        self.failed_job_ids.append(job_id)
        return type(
            "_MarkedJob",
            (),
            {
                "id": job_id,
                "plan_id": "plan-1",
                "spot_name": "清水寺",
                "attempts": 1,
                "max_attempts": 3,
                "status": "queued",
            },
        )()

    def requeue_failed_job(self, job_id: str):
        self.requeued_job_ids.append(job_id)
        return type(
            "_RequeuedJob",
            (),
            {
                "id": job_id,
                "plan_id": "plan-1",
                "spot_name": "清水寺",
                "attempts": 0,
                "max_attempts": 3,
                "status": "queued",
            },
        )()


class _SkippingJobRepository(_ClaimingJobRepository):
    def claim_job(self, plan_id: str, spot_name: str, *, worker_id: str):
        return None


class _FakeSpotImagesUseCase:
    def __init__(self, **_kwargs) -> None:
        pass

    async def generate_for_spot(self, plan_id: str, spot_name: str):
        return "https://example.com/image.png", "succeeded", None


class _FailingSpotImagesUseCase:
    def __init__(self, **_kwargs) -> None:
        pass

    async def generate_for_spot(self, plan_id: str, spot_name: str):
        return None, "failed", "quota exceeded"


class _TerminalFailureJobRepository(_ClaimingJobRepository):
    def mark_failed(self, job_id: str, *, error_message: str):
        self.failed_job_ids.append(job_id)
        return type(
            "_TerminalFailedJob",
            (),
            {
                "id": job_id,
                "plan_id": "plan-1",
                "spot_name": "清水寺",
                "attempts": 3,
                "max_attempts": 3,
                "status": "failed",
            },
        )()


class _FakeTaskDispatcher:
    def __init__(self) -> None:
        self.enqueued: list[tuple[str, str, str | None, str | None]] = []

    def enqueue_spot_image_task(
        self,
        plan_id: str,
        spot_name: str,
        *,
        task_idempotency_key: str | None = None,
        target_url: str | None = None,
    ) -> None:
        self.enqueued.append((plan_id, spot_name, task_idempotency_key, target_url))


def _build_http_request(headers: dict[str, str]) -> Request:
    scope_headers = [(key.lower().encode("latin-1"), value.encode("latin-1")) for key, value in headers.items()]
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/internal/tasks/spot-image",
        "headers": scope_headers,
    }
    return Request(scope)


@pytest.mark.asyncio
async def test_run_spot_image_task_returns_succeeded(monkeypatch: pytest.MonkeyPatch) -> None:
    job_repo = _ClaimingJobRepository(None)

    monkeypatch.setenv("CLOUD_TASKS_QUEUE_NAME", "spot-image-generation")
    from app.config.settings import get_settings

    get_settings.cache_clear()
    monkeypatch.setattr(spot_image_tasks, "SpotImageJobRepository", lambda _db: job_repo)
    monkeypatch.setattr(spot_image_tasks, "TravelGuideRepository", lambda _db: object())
    monkeypatch.setattr(spot_image_tasks, "GenerateSpotImagesUseCase", _FakeSpotImagesUseCase)
    monkeypatch.setattr(spot_image_tasks, "get_image_generation_service", lambda: object())
    monkeypatch.setattr(spot_image_tasks, "get_storage_service", lambda: object())

    response = await spot_image_tasks.run_spot_image_task(
        request=spot_image_tasks.SpotImageTaskRequest(plan_id="plan-1", spot_name="清水寺"),
        http_request=_build_http_request(
            {
                "X-Cloudtasks-Taskname": "task-1",
                "X-Cloudtasks-Queuename": "spot-image-generation",
            }
        ),
        db=object(),
    )
    assert response == {"status": "succeeded"}
    assert job_repo.succeeded_job_ids == ["job-1"]


@pytest.mark.asyncio
async def test_run_spot_image_task_returns_skipped_when_not_claimable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CLOUD_TASKS_QUEUE_NAME", "spot-image-generation")
    from app.config.settings import get_settings

    get_settings.cache_clear()
    monkeypatch.setattr(spot_image_tasks, "SpotImageJobRepository", lambda _db: _SkippingJobRepository(None))
    monkeypatch.setattr(spot_image_tasks, "TravelGuideRepository", lambda _db: object())
    monkeypatch.setattr(spot_image_tasks, "GenerateSpotImagesUseCase", _FakeSpotImagesUseCase)
    monkeypatch.setattr(spot_image_tasks, "get_image_generation_service", lambda: object())
    monkeypatch.setattr(spot_image_tasks, "get_storage_service", lambda: object())

    response = await spot_image_tasks.run_spot_image_task(
        request=spot_image_tasks.SpotImageTaskRequest(plan_id="plan-1", spot_name="清水寺"),
        http_request=_build_http_request(
            {
                "X-Cloudtasks-Taskname": "task-1",
                "X-Cloudtasks-Queuename": "spot-image-generation",
            }
        ),
        db=object(),
    )
    assert response == {"status": "skipped"}


@pytest.mark.asyncio
async def test_run_spot_image_task_raises_403_without_cloud_tasks_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CLOUD_TASKS_QUEUE_NAME", "spot-image-generation")
    from app.config.settings import get_settings

    get_settings.cache_clear()

    with pytest.raises(HTTPException) as exc_info:
        await spot_image_tasks.run_spot_image_task(
            request=spot_image_tasks.SpotImageTaskRequest(plan_id="plan-1", spot_name="清水寺"),
            http_request=_build_http_request({}),
            db=object(),
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_run_spot_image_task_raises_403_when_queue_name_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CLOUD_TASKS_QUEUE_NAME", "spot-image-generation")
    from app.config.settings import get_settings

    get_settings.cache_clear()

    with pytest.raises(HTTPException) as exc_info:
        await spot_image_tasks.run_spot_image_task(
            request=spot_image_tasks.SpotImageTaskRequest(plan_id="plan-1", spot_name="清水寺"),
            http_request=_build_http_request(
                {
                    "X-Cloudtasks-Taskname": "task-1",
                    "X-Cloudtasks-Queuename": "another-queue",
                }
            ),
            db=object(),
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_run_spot_image_task_requeues_when_terminal_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job_repo = _TerminalFailureJobRepository(None)
    task_dispatcher = _FakeTaskDispatcher()

    monkeypatch.setenv("CLOUD_TASKS_QUEUE_NAME", "spot-image-generation")
    from app.config.settings import get_settings

    get_settings.cache_clear()
    spot_image_tasks.get_spot_image_task_dispatcher.cache_clear()
    monkeypatch.setattr(spot_image_tasks, "SpotImageJobRepository", lambda _db: job_repo)
    monkeypatch.setattr(spot_image_tasks, "TravelGuideRepository", lambda _db: object())
    monkeypatch.setattr(spot_image_tasks, "GenerateSpotImagesUseCase", _FailingSpotImagesUseCase)
    monkeypatch.setattr(spot_image_tasks, "get_image_generation_service", lambda: object())
    monkeypatch.setattr(spot_image_tasks, "get_storage_service", lambda: object())
    monkeypatch.setattr(spot_image_tasks, "get_spot_image_task_dispatcher", lambda: task_dispatcher)

    response = await spot_image_tasks.run_spot_image_task(
        request=spot_image_tasks.SpotImageTaskRequest(plan_id="plan-1", spot_name="清水寺"),
        http_request=_build_http_request(
            {
                "X-Cloudtasks-Taskname": "task-1",
                "X-Cloudtasks-Queuename": "spot-image-generation",
            }
        ),
        db=object(),
    )

    assert response == {"status": "requeued"}
    assert job_repo.requeued_job_ids == ["job-1"]
    assert len(task_dispatcher.enqueued) == 1
    enqueued = task_dispatcher.enqueued[0]
    assert enqueued[0] == "plan-1"
    assert enqueued[1] == "清水寺"
    assert enqueued[2] is not None
    assert enqueued[2].startswith("spot-image-requeue-")

