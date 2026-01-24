"""TravelPlan API スキーマ"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.domain.travel_plan.value_objects import PlanStatus
from app.interfaces.schemas.travel_guide import TravelGuideResponse


class TouristSpotSchema(BaseModel):
    """観光スポットスキーマ"""

    id: str | None = Field(None, description="スポットID")
    name: str = Field(..., min_length=1, description="スポット名")
    description: str | None = Field(None, description="説明")
    user_notes: str | None = Field(None, alias="userNotes", description="ユーザーメモ")

    model_config = {"populate_by_name": True}


class CreateTravelPlanRequest(BaseModel):
    """旅行計画作成リクエスト"""

    user_id: str = Field(..., min_length=1, alias="userId", description="ユーザーID")
    title: str = Field(..., min_length=1, description="旅行タイトル")
    destination: str = Field(..., min_length=1, description="目的地")
    spots: list[TouristSpotSchema] = Field(default_factory=list, description="観光スポットリスト")

    model_config = {"populate_by_name": True}

    @field_validator("user_id", "title", "destination")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """空文字列でないことを検証する"""
        if not value.strip():
            raise ValueError("must not be empty")
        return value


class UpdateTravelPlanRequest(BaseModel):
    """旅行計画更新リクエスト"""

    title: str | None = Field(None, min_length=1, description="旅行タイトル")
    destination: str | None = Field(None, min_length=1, description="目的地")
    spots: list[TouristSpotSchema] | None = Field(None, description="観光スポットリスト")
    status: str | None = Field(None, description="旅行状態")

    @field_validator("title", "destination")
    @classmethod
    def validate_not_empty(cls, value: str | None) -> str | None:
        """空文字列でないことを検証する"""
        if value is not None and not value.strip():
            raise ValueError("must not be empty")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        """旅行状態の妥当性を検証する"""
        if value is None:
            return None
        if not value.strip():
            raise ValueError("must not be empty")
        try:
            PlanStatus(value)
        except ValueError as exc:
            raise ValueError("invalid status") from exc
        return value


class TravelPlanResponse(BaseModel):
    """旅行計画レスポンス"""

    id: str
    user_id: str = Field(..., alias="userId")
    title: str
    destination: str
    spots: list[dict]
    status: str
    guide_generation_status: str = Field(..., alias="guideGenerationStatus")
    reflection_generation_status: str = Field(..., alias="reflectionGenerationStatus")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    guide: TravelGuideResponse | None = None

    model_config = {"populate_by_name": True}
