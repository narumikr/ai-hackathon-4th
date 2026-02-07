"""Cloud Tasksディスパッチャのユニットテスト."""

from __future__ import annotations

from unittest.mock import Mock

import pytest
from google.api_core import exceptions as google_exceptions

from app.infrastructure.tasks.cloud_tasks_dispatcher import CloudTasksDispatcher


def _build_dispatcher_with_mocked_client(monkeypatch: pytest.MonkeyPatch) -> tuple[CloudTasksDispatcher, Mock]:
    mock_client = Mock()
    mock_client.queue_path.return_value = "projects/p/locations/l/queues/q"

    monkeypatch.setattr(
        "app.infrastructure.tasks.cloud_tasks_dispatcher.tasks_v2.CloudTasksClient",
        lambda: mock_client,
    )

    dispatcher = CloudTasksDispatcher(
        project_id="test-project",
        location="asia-northeast1",
        queue_name="spot-image-generation",
        target_url="https://example.com/api/v1/internal/tasks/spot-image",
        service_account_email="worker@example.com",
        dispatch_deadline_seconds=1800,
    )
    return dispatcher, mock_client


def test_enqueue_spot_image_task_allows_already_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    dispatcher, mock_client = _build_dispatcher_with_mocked_client(monkeypatch)
    mock_client.create_task.side_effect = google_exceptions.AlreadyExists("already exists")

    dispatcher.enqueue_spot_image_task(
        plan_id="plan-1",
        spot_name="清水寺",
        task_idempotency_key="spot-image-abc",
    )

    mock_client.create_task.assert_called_once()


def test_enqueue_spot_image_task_reraises_non_duplicate_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dispatcher, mock_client = _build_dispatcher_with_mocked_client(monkeypatch)
    mock_client.create_task.side_effect = RuntimeError("network failure")

    with pytest.raises(RuntimeError, match="network failure"):
        dispatcher.enqueue_spot_image_task(
            plan_id="plan-1",
            spot_name="清水寺",
            task_idempotency_key="spot-image-abc",
        )


def test_enqueue_spot_image_task_calls_create_task(monkeypatch: pytest.MonkeyPatch) -> None:
    dispatcher, mock_client = _build_dispatcher_with_mocked_client(monkeypatch)

    dispatcher.enqueue_spot_image_task(
        plan_id="plan-1",
        spot_name="清水寺",
        task_idempotency_key="spot-image-abc",
    )

    mock_client.create_task.assert_called_once()
