"""旅行ガイド生成用のPydanticスキーマ"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, field_validator

from .base import GeminiResponseSchema


class HistoricalEventSchema(GeminiResponseSchema):
    """歴史的イベントのスキーマ"""

    year: Annotated[int, Field(description="歴史的出来事の発生年（西暦）")]
    event: Annotated[str, Field(description="歴史的出来事の名称", min_length=1)]
    significance: Annotated[str, Field(description="歴史的意義の説明", min_length=5)]
    related_spots: Annotated[
        list[str],
        Field(
            description="関連する観光スポット名のリスト",
            min_length=1,
            alias="relatedSpots",
        ),
    ]

    @field_validator("related_spots")
    @classmethod
    def validate_related_spots_not_empty(cls, v: list[str]) -> list[str]:
        """関連スポットが空文字列を含まないことを検証"""
        if not v or any(not spot.strip() for spot in v):
            raise ValueError("related_spots must contain non-empty strings")
        return v


class SpotDetailSchema(GeminiResponseSchema):
    """観光スポット詳細のスキーマ"""

    spot_name: Annotated[str, Field(description="観光スポット名", min_length=1, alias="spotName")]
    historical_background: Annotated[
        str,
        Field(description="歴史的背景の詳細説明", min_length=5, alias="historicalBackground"),
    ]
    highlights: Annotated[
        list[str],
        Field(description="見どころのリスト", min_length=1),
    ]
    recommended_visit_time: Annotated[
        str,
        Field(
            description="推奨訪問時間（例: 朝、午後、夕方など）",
            min_length=1,
            alias="recommendedVisitTime",
        ),
    ]
    historical_significance: Annotated[
        str,
        Field(description="歴史的意義の説明", min_length=5, alias="historicalSignificance"),
    ]

    @field_validator("highlights")
    @classmethod
    def validate_highlights_not_empty(cls, v: list[str]) -> list[str]:
        """見どころが空文字列を含まないことを検証"""
        if not v or any(not highlight.strip() for highlight in v):
            raise ValueError("highlights must contain non-empty strings")
        return v


class CheckpointSchema(GeminiResponseSchema):
    """学習チェックポイントのスキーマ"""

    spot_name: Annotated[str, Field(description="観光スポット名", min_length=1, alias="spotName")]
    checkpoints: Annotated[
        list[str],
        Field(description="チェックポイント項目のリスト", min_length=1),
    ]
    historical_context: Annotated[
        str,
        Field(description="歴史的コンテキストの説明", min_length=5, alias="historicalContext"),
    ]

    @field_validator("checkpoints")
    @classmethod
    def validate_checkpoints_not_empty(cls, v: list[str]) -> list[str]:
        """チェックポイントが空文字列を含まないことを検証"""
        if not v or any(not checkpoint.strip() for checkpoint in v):
            raise ValueError("checkpoints must contain non-empty strings")
        return v


class TravelGuideResponseSchema(GeminiResponseSchema):
    """旅行ガイド全体のレスポンススキーマ"""

    overview: Annotated[
        str,
        Field(
            description=(
                "旅行全体の概要。以下の4要素を含む充実した概要文（200-400文字程度）: "
                "1) 旅行のテーマや目的、2) 訪問スポットの関連性、3) 歴史的時代背景、4) おすすめポイント"
            ),
            min_length=100,
        ),
    ]
    timeline: Annotated[
        list[HistoricalEventSchema],
        Field(description="歴史的出来事の年表", min_length=1),
    ]
    spot_details: Annotated[
        list[SpotDetailSchema],
        Field(description="各観光スポットの詳細情報", min_length=1, alias="spotDetails"),
    ]
    checkpoints: Annotated[
        list[CheckpointSchema],
        Field(description="各スポットでの学習チェックポイント", min_length=1),
    ]


class TravelGuideOutlineSchema(GeminiResponseSchema):
    """旅行ガイド骨子（overview/timeline）のレスポンススキーマ."""

    overview: Annotated[
        str,
        Field(
            description=(
                "旅行全体の概要。以下の4要素を含む充実した概要文（200-400文字程度）: "
                "1) 旅行のテーマや目的、2) 訪問スポットの関連性、3) 歴史的時代背景、4) おすすめポイント"
            ),
            min_length=100,
        ),
    ]
    timeline: Annotated[
        list[HistoricalEventSchema],
        Field(description="歴史的出来事の年表", min_length=1),
    ]


class TravelGuideDetailsSchema(GeminiResponseSchema):
    """旅行ガイド詳細（spotDetails/checkpoints）のレスポンススキーマ."""

    spot_details: Annotated[
        list[SpotDetailSchema],
        Field(description="各観光スポットの詳細情報", min_length=1, alias="spotDetails"),
    ]
    checkpoints: Annotated[
        list[CheckpointSchema],
        Field(description="各スポットでの学習チェックポイント", min_length=1),
    ]
