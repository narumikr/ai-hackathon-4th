"""スポット画像タスクディスパッチのインターフェース."""

from abc import ABC, abstractmethod


class ISpotImageTaskDispatcher(ABC):
    """スポット画像タスクを外部実行基盤に配送するポート."""

    @abstractmethod
    def enqueue_spot_image_task(
        self,
        plan_id: str,
        spot_name: str,
        *,
        task_idempotency_key: str | None = None,
        target_url: str | None = None,
    ) -> None:
        """スポット画像生成タスクをenqueueする."""
        raise NotImplementedError
