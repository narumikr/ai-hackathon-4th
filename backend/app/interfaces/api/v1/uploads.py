"""画像アップロードAPIエンドポイント"""

import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.application.ports.ai_service import IAIService
from app.application.ports.storage_service import IStorageService
from app.application.use_cases.analyze_photos import AnalyzePhotosUseCase
from app.infrastructure.persistence.database import get_db
from app.infrastructure.repositories.reflection_repository import ReflectionRepository
from app.infrastructure.repositories.travel_plan_repository import TravelPlanRepository
from app.infrastructure.storage.exceptions import (
    FileSizeExceededError,
    StorageOperationError,
    UnsupportedImageFormatError,
)
from app.interfaces.api.dependencies import (
    get_ai_service_dependency,
    get_storage_service_dependency,
)

router = APIRouter(prefix="/spot-reflections", tags=["spot-reflections"])


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
    status_code=status.HTTP_204_NO_CONTENT,
    summary="スポットの写真と感想を登録",
)
async def upload_images(
    request: Request,  # noqa: B008
    plan_id: str = Form(..., alias="planId"),  # noqa: B008
    user_id: str = Form(..., alias="userId"),  # noqa: B008
    spot_id: str = Form(..., alias="spotId"),  # noqa: B008
    spot_note: str | None = Form(None, alias="spotNote"),  # noqa: B008
    files: list[UploadFile] = File(...),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    ai_service: IAIService = Depends(get_ai_service_dependency),  # noqa: B008
    storage_service: IStorageService = Depends(get_storage_service_dependency),  # noqa: B008
) -> Response:
    """スポットごとの写真と感想を登録する"""
    plan_id = _ensure_non_empty(plan_id, "plan_id")
    user_id = _ensure_non_empty(user_id, "user_id")
    spot_id = _ensure_non_empty(spot_id, "spot_id")
    form_data = await request.form()
    spot_note_provided = "spotNote" in form_data
    if spot_note is not None:
        spot_note = spot_note.strip()
        if not spot_note:
            spot_note = None

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

    plan_spot_ids = {spot.id for spot in travel_plan.spots}
    if spot_id not in plan_spot_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"spot_id is not found in travel plan: {spot_id}",
        )

    photos: list[dict] = []

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

        photos.append(
            {
                "id": photo_id,
                "spotId": spot_id,
                "url": url,
            }
        )

    reflection_repository = ReflectionRepository(db)
    analyze_use_case = AnalyzePhotosUseCase(
        plan_repository=plan_repository,
        reflection_repository=reflection_repository,
        ai_service=ai_service,
    )
    await analyze_use_case.execute(
        plan_id=plan_id,
        user_id=user_id,
        photos=photos,
        spot_note=spot_note,
        spot_note_provided=spot_note_provided,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
