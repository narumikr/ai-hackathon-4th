"""ローカルワーカーモード用のタスクディスパッチャ."""

import logging

from app.application.ports.spot_image_task_dispatcher import ISpotImageTaskDispatcher

logger = logging.getLogger(__name__)


class LocalWorkerDispatcher(ISpotImageTaskDispatcher):
    """ローカルの常駐worker運用を前提とした実装."""

    def enqueue_spot_image_task(
        self,
        plan_id: str,
        spot_name: str,
        *,
        task_idempotency_key: str | None = None,
        target_url: str | None = None,
    ) -> None:
        if not plan_id or not plan_id.strip():
            raise ValueError("plan_id is required and must not be empty.")
        if not spot_name or not spot_name.strip():
            raise ValueError("spot_name is required and must not be empty.")
        logger.debug(
            "Skipping external enqueue in local_worker mode",
            extra={
                "plan_id": plan_id,
                "spot_name": spot_name,
                "task_idempotency_key": task_idempotency_key,
                "target_url": target_url,
            },
        )
