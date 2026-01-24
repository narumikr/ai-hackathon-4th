"""TravelPlan Aggregateの値オブジェクト"""

from enum import Enum


class PlanStatus(str, Enum):
    """旅行計画のステータス"""

    PLANNING = "planning"
    COMPLETED = "completed"


class GenerationStatus(str, Enum):
    """AI生成のステータス"""

    NOT_STARTED = "not_started"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
