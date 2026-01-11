"""エラーハンドリングミドルウェア."""

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """HTTPException のハンドラー.

    Args:
        request: リクエストオブジェクト
        exc: HTTPException

    Returns:
        JSONResponse: 構造化されたエラーレスポンス
    """
    logger.error(
        f"HTTP error occurred: {exc.status_code} - {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "message": str(exc.detail),
                "status_code": exc.status_code,
            }
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """バリデーションエラーのハンドラー.

    Args:
        request: リクエストオブジェクト
        exc: RequestValidationError

    Returns:
        JSONResponse: 構造化されたエラーレスポンス
    """
    logger.warning(
        f"Validation error occurred: {exc.errors()}",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "validation_error",
                "message": "リクエストのバリデーションに失敗しました",
                "details": exc.errors(),
            }
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """予期しないエラーのハンドラー.

    Args:
        request: リクエストオブジェクト
        exc: Exception

    Returns:
        JSONResponse: 構造化されたエラーレスポンス
    """
    logger.exception(
        f"Unexpected error occurred: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "internal_error",
                "message": "内部サーバーエラーが発生しました",
            }
        },
    )
