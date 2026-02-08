"""application層ユニットテスト共通fixture"""

import pytest


class FakeSpotImageJobRepository:
    """テスト用のスポット画像生成ジョブリポジトリ"""

    def create_jobs(
        self,
        plan_id: str,
        spot_names: list[str],
        *,
        max_attempts: int = 3,
        commit: bool = True,
    ) -> int:
        return len(spot_names)

    def fetch_and_lock_jobs(self, limit: int, *, worker_id: str):
        raise NotImplementedError

    def mark_succeeded(self, job_id: str) -> None:
        raise NotImplementedError

    def mark_failed(self, job_id: str, *, error_message: str):
        raise NotImplementedError

    def requeue_failed_job(self, job_id: str):
        raise NotImplementedError


class FailingSpotImageJobRepository(FakeSpotImageJobRepository):
    """create_jobsで失敗するテスト用リポジトリ"""

    def create_jobs(
        self,
        plan_id: str,
        spot_names: list[str],
        *,
        max_attempts: int = 3,
        commit: bool = True,
    ) -> int:
        raise ValueError("job registration failed")


@pytest.fixture
def fake_job_repository() -> FakeSpotImageJobRepository:
    return FakeSpotImageJobRepository()


@pytest.fixture
def failing_job_repository() -> FailingSpotImageJobRepository:
    return FailingSpotImageJobRepository()


class FakeSpotImageTaskDispatcher:
    """テスト用タスクディスパッチャ."""

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


@pytest.fixture
def fake_task_dispatcher() -> FakeSpotImageTaskDispatcher:
    return FakeSpotImageTaskDispatcher()
