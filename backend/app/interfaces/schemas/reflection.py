"""Reflection API スキーマ"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class UploadedImageResponse(BaseModel):
    """画像アップロードレスポンス（単体）"""

    id: str
    url: str
    file_name: str = Field(..., alias="fileName")
    content_type: str = Field(..., alias="contentType")

    model_config = {"populate_by_name": True}


class UploadImagesResponse(BaseModel):
    """画像アップロードレスポンス"""

    images: list[UploadedImageResponse]


class ReflectionPhotoRequest(BaseModel):
    """振り返り作成用の写真入力"""

    id: str
    spot_id: str = Field(..., alias="spotId")
    url: str
    user_description: str | None = Field(None, alias="userDescription")

    model_config = {"populate_by_name": True}

    @field_validator("id", "spot_id", "url")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """空文字列でないことを検証する"""
        if not value.strip():
            raise ValueError("must not be empty")
        return value

    @field_validator("user_description")
    @classmethod
    def validate_user_description(cls, value: str | None) -> str | None:
        """ユーザー説明の空文字列を拒否する"""
        if value is not None and not value.strip():
            raise ValueError("must not be empty")
        return value


class CreateReflectionRequest(BaseModel):
    """振り返り作成リクエスト"""

    plan_id: str = Field(..., min_length=1, alias="planId")
    user_notes: str | None = Field(None, alias="userNotes")

    model_config = {"populate_by_name": True}

    @field_validator("plan_id")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """空文字列でないことを検証する"""
        if not value.strip():
            raise ValueError("must not be empty")
        return value

    @field_validator("user_notes")
    @classmethod
    def validate_user_notes(cls, value: str | None) -> str | None:
        """ユーザー感想の空文字列をNoneとして扱う"""
        if value is None:
            return value
        if not value.strip():
            return None
        return value


class ReflectionPhotoResponse(BaseModel):
    """振り返り写真レスポンス"""

    id: str
    spot_id: str = Field(..., alias="spotId")
    url: str
    analysis: str
    user_description: str | None = Field(None, alias="userDescription")

    model_config = {"populate_by_name": True}


class ReflectionResponse(BaseModel):
    """振り返りレスポンス"""

    id: str
    plan_id: str = Field(..., alias="planId")
    user_id: str = Field(..., alias="userId")
    photos: list[ReflectionPhotoResponse]
    user_notes: str | None = Field(None, alias="userNotes")
    spot_notes: dict[str, str | None] = Field(default_factory=dict, alias="spotNotes")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True}


class SpotReflectionResponse(BaseModel):
    """スポット振り返りレスポンス"""

    spot_name: str = Field(..., alias="spotName", title="SpotName")
    reflection: str

    model_config = {"populate_by_name": True}


class ReflectionPamphletResponse(BaseModel):
    """振り返りパンフレットレスポンス"""

    travel_summary: str = Field(..., alias="travelSummary", title="TravelSummary")
    spot_reflections: list[SpotReflectionResponse] = Field(
        ...,
        alias="spotReflections",
        title="SpotReflections",
    )
    next_trip_suggestions: list[str] = Field(
        ...,
        alias="nextTripSuggestions",
        title="NextTripSuggestions",
    )

    model_config = {"populate_by_name": True}
