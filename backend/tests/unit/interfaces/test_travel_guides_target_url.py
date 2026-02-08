"""旅行ガイドAPIのCloud Tasks向けURL生成テスト。"""

from __future__ import annotations

import pytest

from app.interfaces.api.v1.travel_guides import _build_spot_image_task_target_url


class _DummyRequest:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url


def test_build_spot_image_task_target_url_forces_https() -> None:
    request = _DummyRequest("http://example.com/")

    result = _build_spot_image_task_target_url(request)  # type: ignore[arg-type]

    assert result == "https://example.com/api/v1/internal/tasks/spot-image"


def test_build_spot_image_task_target_url_keeps_host_and_port() -> None:
    request = _DummyRequest("http://example.com:8080/base/")

    result = _build_spot_image_task_target_url(request)  # type: ignore[arg-type]

    assert result == "https://example.com:8080/base/api/v1/internal/tasks/spot-image"


def test_build_spot_image_task_target_url_raises_when_base_url_is_empty() -> None:
    request = _DummyRequest("   ")

    with pytest.raises(ValueError, match="http_request.base_url is required"):
        _build_spot_image_task_target_url(request)  # type: ignore[arg-type]
