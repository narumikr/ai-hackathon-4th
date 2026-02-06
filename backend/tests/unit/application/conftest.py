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

    def mark_failed(self, job_id: str, *, error_message: str) -> None:
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
