"""スポット画像タスクAPIのユニットテスト."""

from __future__ import annotations

import pytest

from app.interfaces.api.v1 import spot_image_tasks


class _FakeJob:
    def __init__(self, job_id: str) -> None:
        self.id = job_id


class _ClaimingJobRepository:
    def __init__(self, _db) -> None:
        self.succeeded_job_ids: list[str] = []
        self.failed_job_ids: list[str] = []

    def claim_job(self, plan_id: str, spot_name: str, *, worker_id: str):
        return _FakeJob("job-1")

    def mark_succeeded(self, job_id: str) -> None:
        self.succeeded_job_ids.append(job_id)

    def mark_failed(self, job_id: str, *, error_message: str) -> None:
        self.failed_job_ids.append(job_id)


class _SkippingJobRepository(_ClaimingJobRepository):
    def claim_job(self, plan_id: str, spot_name: str, *, worker_id: str):
        return None


class _FakeSpotImagesUseCase:
    def __init__(self, **_kwargs) -> None:
        pass

    async def generate_for_spot(self, plan_id: str, spot_name: str):
        return "https://example.com/image.png", "succeeded", None


@pytest.mark.asyncio
async def test_run_spot_image_task_returns_succeeded(monkeypatch: pytest.MonkeyPatch) -> None:
    job_repo = _ClaimingJobRepository(None)

    monkeypatch.setattr(spot_image_tasks, "SpotImageJobRepository", lambda _db: job_repo)
    monkeypatch.setattr(spot_image_tasks, "TravelGuideRepository", lambda _db: object())
    monkeypatch.setattr(spot_image_tasks, "GenerateSpotImagesUseCase", _FakeSpotImagesUseCase)
    monkeypatch.setattr(spot_image_tasks, "get_image_generation_service", lambda: object())
    monkeypatch.setattr(spot_image_tasks, "get_storage_service", lambda: object())

    response = await spot_image_tasks.run_spot_image_task(
        request=spot_image_tasks.SpotImageTaskRequest(plan_id="plan-1", spot_name="清水寺"),
        db=object(),
    )
    assert response == {"status": "succeeded"}
    assert job_repo.succeeded_job_ids == ["job-1"]


@pytest.mark.asyncio
async def test_run_spot_image_task_returns_skipped_when_not_claimable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(spot_image_tasks, "SpotImageJobRepository", lambda _db: _SkippingJobRepository(None))
    monkeypatch.setattr(spot_image_tasks, "TravelGuideRepository", lambda _db: object())
    monkeypatch.setattr(spot_image_tasks, "GenerateSpotImagesUseCase", _FakeSpotImagesUseCase)
    monkeypatch.setattr(spot_image_tasks, "get_image_generation_service", lambda: object())
    monkeypatch.setattr(spot_image_tasks, "get_storage_service", lambda: object())

    response = await spot_image_tasks.run_spot_image_task(
        request=spot_image_tasks.SpotImageTaskRequest(plan_id="plan-1", spot_name="清水寺"),
        db=object(),
    )
    assert response == {"status": "skipped"}
