"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config.settings import get_settings
from app.interfaces.api.v1 import travel_plans
from app.interfaces.middleware import (
    generic_exception_handler,
    http_exception_handler,
    setup_cors,
    validation_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """アプリケーションのライフサイクル管理."""
    # 起動時の処理
    print("Starting up...")
    yield
    # 終了時の処理
    print("Shutting down...")


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


@app.get("/")
async def root() -> dict[str, str]:
    """ルートエンドポイント."""
    return {"message": "Historical Travel Agent API"}


@app.get("/health")
async def health() -> dict[str, str]:
    """ヘルスチェックエンドポイント."""
    return {"status": "ok"}
