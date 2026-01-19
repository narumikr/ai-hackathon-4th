"""TravelGuide API スキーマ"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.interfaces.schemas.travel_plan import LocationSchema


class HistoricalEventSchema(BaseModel):
    """歴史イベントスキーマ"""

    year: int
    event: str
    significance: str
    related_spots: list[str] = Field(..., alias="relatedSpots")

    model_config = {"populate_by_name": True}


class SpotDetailSchema(BaseModel):
    """スポット詳細スキーマ"""

    spot_name: str = Field(..., alias="spotName")
    historical_background: str = Field(..., alias="historicalBackground")
    highlights: list[str]
    recommended_visit_time: str = Field(..., alias="recommendedVisitTime")
    historical_significance: str = Field(..., alias="historicalSignificance")

    model_config = {"populate_by_name": True}


class CheckpointSchema(BaseModel):
    """チェックポイントスキーマ"""

    spot_name: str = Field(..., alias="spotName")
    checkpoints: list[str]
    historical_context: str = Field(..., alias="historicalContext")

    model_config = {"populate_by_name": True}


class MapMarkerSchema(BaseModel):
    """地図マーカースキーマ"""

    lat: float
    lng: float
    label: str


class MapDataSchema(BaseModel):
    """地図データスキーマ"""

    center: LocationSchema
    zoom: int
    markers: list[MapMarkerSchema]


class GenerateTravelGuideRequest(BaseModel):
    """旅行ガイド生成リクエスト"""

    plan_id: str = Field(..., min_length=1, alias="planId", description="旅行計画ID")

    model_config = {"populate_by_name": True}

    @field_validator("plan_id")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """空文字列でないことを検証する"""
        if not value.strip():
            raise ValueError("must not be empty")
        return value


class TravelGuideResponse(BaseModel):
    """旅行ガイドレスポンス"""

    id: str
    plan_id: str = Field(..., alias="planId")
    overview: str
    timeline: list[HistoricalEventSchema]
    spot_details: list[SpotDetailSchema] = Field(..., alias="spotDetails")
    checkpoints: list[CheckpointSchema]
    map_data: MapDataSchema = Field(..., alias="mapData")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = {"populate_by_name": True}
