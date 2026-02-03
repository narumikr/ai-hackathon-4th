"""AI APIレスポンス用Pydanticスキーマ"""

from .base import GeminiResponseSchema
from .evaluation import SpotEvaluation, TravelGuideEvaluationSchema
from .reflection import ReflectionPamphletResponseSchema, SpotReflectionSchema
from .travel_guide import (
    CheckpointSchema,
    HistoricalEventSchema,
    SpotDetailSchema,
    TravelGuideResponseSchema,
)

__all__ = [
    "GeminiResponseSchema",
    "TravelGuideResponseSchema",
    "HistoricalEventSchema",
    "SpotDetailSchema",
    "CheckpointSchema",
    "ReflectionPamphletResponseSchema",
    "SpotReflectionSchema",
    "TravelGuideEvaluationSchema",
    "SpotEvaluation",
]
