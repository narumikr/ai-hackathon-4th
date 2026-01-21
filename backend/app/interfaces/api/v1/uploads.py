"""画像アップロードAPIエンドポイント"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.application.ports.storage_service import IStorageService
from app.infrastructure.persistence.database import get_db
from app.infrastructure.repositories.travel_plan_repository import TravelPlanRepository
from app.infrastructure.storage.exceptions import (
    FileSizeExceededError,
    StorageOperationError,
    UnsupportedImageFormatError,
)
from app.interfaces.api.dependencies import get_storage_service_dependency
from app.interfaces.schemas.reflection import UploadedImageResponse, UploadImagesResponse

router = APIRouter(prefix="/upload-images", tags=["uploads"])


def _resolve_extension(filename: str | None, content_type: str | None) -> str:
    """ファイル拡張子を決定する"""
    if not content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="content_type is required for uploaded files.",
        )

    content_type_map = {
        "image/jpeg": ("jpg", "jpeg"),
        "image/jpg": ("jpg", "jpeg"),
        "image/png": ("png",),
        "image/webp": ("webp",),
    }
    normalized_content_type = content_type.lower()
    extensions = content_type_map.get(normalized_content_type)
    if not extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"unsupported content_type: {content_type}.",
        )

    if filename:
        suffix = Path(filename).suffix.lower().lstrip(".")
        if suffix:
            if suffix not in extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="file extension does not match content_type.",
                )
            return suffix

    return extensions[0]


def _ensure_non_empty(value: str, field_name: str) -> str:
    """必須文字列のバリデーションを行う"""
    if not value or not value.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} is required and must not be empty.",
        )
    return value.strip()


@router.post(
    "",
    response_model=UploadImagesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="画像をアップロード",
)
async def upload_images(
    plan_id: str = Form(..., alias="planId"),  # noqa: B008
    user_id: str = Form(..., alias="userId"),  # noqa: B008
    files: list[UploadFile] = File(...),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    storage_service: IStorageService = Depends(get_storage_service_dependency),  # noqa: B008
) -> UploadImagesResponse:
    """画像をアップロードする"""
    plan_id = _ensure_non_empty(plan_id, "plan_id")
    user_id = _ensure_non_empty(user_id, "user_id")

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="files must be a non-empty list.",
        )

    plan_repository = TravelPlanRepository(db)
    travel_plan = plan_repository.find_by_id(plan_id)
    if travel_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        )
    if travel_plan.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id does not match the travel plan owner.",
        )

    uploaded: list[UploadedImageResponse] = []

    for file in files:
        content_type = file.content_type
        if not content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="content_type is required for uploaded files.",
            )

        file_bytes = await file.read()
        extension = _resolve_extension(file.filename, content_type)
        photo_id = str(uuid.uuid4())
        destination = f"reflections/{plan_id}/{photo_id}.{extension}"

        try:
            url = await storage_service.upload_file(
                file_data=file_bytes,
                destination=destination,
                content_type=content_type,
            )
        except UnsupportedImageFormatError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except FileSizeExceededError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except StorageOperationError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
            ) from exc

        uploaded.append(
            UploadedImageResponse(
                id=photo_id,
                url=url,
                fileName=file.filename or destination,
                contentType=content_type,
            )
        )

    return UploadImagesResponse(images=uploaded)
