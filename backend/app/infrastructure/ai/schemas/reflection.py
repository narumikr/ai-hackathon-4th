"""振り返りパンフレット生成用のPydanticスキーマ"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, field_validator

from .base import GeminiResponseSchema


class SpotReflectionSchema(GeminiResponseSchema):
    """スポット振り返りのスキーマ"""

    spot_name: Annotated[str, Field(description="観光スポット名", min_length=1, alias="spotName")]
    reflection: Annotated[
        str,
        Field(description="そのスポットでの学びや気づきの振り返り", min_length=10),
    ]


class ReflectionPamphletResponseSchema(GeminiResponseSchema):
    """振り返りパンフレット全体のレスポンススキーマ"""

    travel_summary: Annotated[
        str,
        Field(description="旅行全体の総括", min_length=10, alias="travelSummary"),
    ]
    spot_reflections: Annotated[
        list[SpotReflectionSchema],
        Field(description="各スポットごとの振り返り", min_length=1, alias="spotReflections"),
    ]
    next_trip_suggestions: Annotated[
        list[str],
        Field(description="次回旅行への提案リスト", min_length=1, alias="nextTripSuggestions"),
    ]

    @field_validator("next_trip_suggestions")
    @classmethod
    def validate_suggestions_not_empty(cls, v: list[str]) -> list[str]:
        """提案が空文字列を含まないことを検証"""
        if not v or any(not suggestion.strip() for suggestion in v):
            raise ValueError("next_trip_suggestions must contain non-empty strings")
        return v
