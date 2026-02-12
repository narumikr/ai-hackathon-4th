"""FastAPI application entry point"""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config.logging import setup_logging
from app.config.settings import get_settings
from app.infrastructure.firebase_admin import initialize_firebase_admin
from app.interfaces.api.v1 import reflections, spot_image_tasks, travel_guides, travel_plans, uploads
from app.interfaces.middleware import (
    generic_exception_handler,
    http_exception_handler,
    setup_cors,
    validation_exception_handler,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """アプリケーションのライフサイクル管理"""
    # ロギング設定の初期化
    setup_logging()

    # 起動時の処理
    logger.info("Starting up...")

    # Google Cloud認証情報の環境変数を設定
    settings = get_settings()
    if settings.google_application_credentials:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
        logger.info("Set GOOGLE_APPLICATION_CREDENTIALS.")

    # Firebase Admin SDKの初期化
    if settings.firebase_project_id:
        initialize_firebase_admin(
            project_id=settings.firebase_project_id,
            client_email=settings.firebase_client_email,
            private_key=settings.firebase_private_key,
        )
        logger.info("Firebase Admin SDK initialized successfully")
    else:
        logger.warning("FIREBASE_PROJECT_ID not set. Auth features will be disabled.")

    yield
    # 終了時の処理
    logger.info("Shutting down...")


# 設定の読み込み
settings = get_settings()

# FastAPIアプリケーション作成
app = FastAPI(
    title="Historical Travel Agent API",
    description="歴史学習特化型旅行AIエージェント - REST API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORSミドルウェアの設定
setup_cors(app)

# エラーハンドラーの登録
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# APIルーターの登録
app.include_router(travel_plans.router, prefix="/api/v1")
app.include_router(travel_guides.router, prefix="/api/v1")
app.include_router(reflections.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1")
app.include_router(spot_image_tasks.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """ルートエンドポイント"""
    return {"message": "Historical Travel Agent API"}


@app.get("/health")
async def health() -> dict[str, str]:
    """ヘルスチェックエンドポイント"""
    return {"status": "ok"}
