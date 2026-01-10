"""FastAPI main module tests."""

from __future__ import annotations

import importlib
import sys

from fastapi.testclient import TestClient


def _load_app_with_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/app")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")

    sys.modules.pop("main", None)
    main = importlib.import_module("main")
    return main.app


def test_root_returns_message(monkeypatch):
    app = _load_app_with_env(monkeypatch)
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Historical Travel Agent API"}


def test_health_returns_ok(monkeypatch):
    app = _load_app_with_env(monkeypatch)
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
