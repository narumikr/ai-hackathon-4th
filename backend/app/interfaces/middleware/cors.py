"""CORS設定モジュール."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings


def setup_cors(app: FastAPI) -> None:
    """CORSミドルウェアを設定する.

    Args:
        app: FastAPIアプリケーションインスタンス
    """
    settings = get_settings()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
