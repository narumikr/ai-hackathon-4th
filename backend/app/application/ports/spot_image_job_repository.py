"""スポット画像生成ジョブリポジトリのインターフェース"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SpotImageJobRecord:
    """スポット画像生成ジョブの読み取り用レコード"""

    id: str
    plan_id: str
    spot_name: str
    attempts: int
    max_attempts: int
    status: str


class ISpotImageJobRepository(ABC):
    """スポット画像生成ジョブリポジトリのインターフェース"""

    @abstractmethod
    def create_jobs(
        self,
        plan_id: str,
        spot_names: list[str],
        *,
        max_attempts: int = 3,
        commit: bool = True,
    ) -> int:
        """スポット画像生成ジョブを作成する

        Args:
            plan_id: 旅行計画ID
            spot_names: スポット名のリスト
            max_attempts: 最大リトライ回数
            commit: Trueの場合はコミットする

        Returns:
            int: 作成されたジョブ数
        """
        raise NotImplementedError

    @abstractmethod
    def fetch_and_lock_jobs(
        self,
        limit: int,
        *,
        worker_id: str,
        stale_after_seconds: int,
    ) -> list[SpotImageJobRecord]:
        """ジョブを取得してロックする

        Args:
            limit: 取得件数
            worker_id: ワーカー識別子
            stale_after_seconds: この秒数を超えてロックされているprocessingジョブを再取得対象にする

        Returns:
            list[SpotImageJobRecord]: ロック済みジョブのリスト
        """
        raise NotImplementedError

    @abstractmethod
    def mark_succeeded(self, job_id: str) -> None:
        """ジョブを成功として更新する"""
        raise NotImplementedError

    @abstractmethod
    def mark_failed(self, job_id: str, *, error_message: str) -> None:
        """ジョブを失敗として更新する"""
        raise NotImplementedError
