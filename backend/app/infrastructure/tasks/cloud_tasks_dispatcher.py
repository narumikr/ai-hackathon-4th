"""Cloud Tasksディスパッチャ."""

from __future__ import annotations

import json
import logging

from google.api_core import exceptions as google_exceptions
from google.cloud import tasks_v2

from app.application.ports.spot_image_task_dispatcher import ISpotImageTaskDispatcher

logger = logging.getLogger(__name__)


class CloudTasksDispatcher(ISpotImageTaskDispatcher):
    """Cloud Tasksへスポット画像生成タスクを配送する実装."""

    def __init__(
        self,
        *,
        project_id: str,
        location: str,
        queue_name: str,
        target_url: str,
        service_account_email: str,
        dispatch_deadline_seconds: int = 1800,
    ) -> None:
        if not project_id or not project_id.strip():
            raise ValueError("project_id is required and must not be empty.")
        if not location or not location.strip():
            raise ValueError("location is required and must not be empty.")
        if not queue_name or not queue_name.strip():
            raise ValueError("queue_name is required and must not be empty.")
        if not service_account_email or not service_account_email.strip():
            raise ValueError("service_account_email is required and must not be empty.")
        if dispatch_deadline_seconds <= 0:
            raise ValueError("dispatch_deadline_seconds must be a positive integer.")

        self._client = tasks_v2.CloudTasksClient()
        self._queue_path = self._client.queue_path(project_id, location, queue_name)
        self._target_url = target_url.strip() if target_url else ""
        self._service_account_email = service_account_email
        self._dispatch_deadline_seconds = dispatch_deadline_seconds

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

        resolved_target_url = target_url or self._target_url
        if not resolved_target_url or not resolved_target_url.strip():
            raise ValueError("target_url is required and must not be empty.")

        payload = {
            "plan_id": plan_id,
            "spot_name": spot_name,
        }
        request_body = json.dumps(payload).encode("utf-8")

        task: dict = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": resolved_target_url,
                "headers": {"Content-Type": "application/json"},
                "body": request_body,
                "oidc_token": {
                    "service_account_email": self._service_account_email,
                    "audience": resolved_target_url,
                },
            },
            "dispatch_deadline": {"seconds": self._dispatch_deadline_seconds},
        }
        if task_idempotency_key:
            safe_name = task_idempotency_key.strip()
            if safe_name:
                task["name"] = f"{self._queue_path}/tasks/{safe_name}"

        try:
            self._client.create_task(request={"parent": self._queue_path, "task": task})
        except google_exceptions.AlreadyExists:
            logger.info(
                "Cloud Tasks task already exists. Skipping duplicate enqueue.",
                extra={
                    "plan_id": plan_id,
                    "spot_name": spot_name,
                    "task_idempotency_key": task_idempotency_key,
                },
            )
