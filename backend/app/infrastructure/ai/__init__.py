"""AI infrastructure layer exports and factory functions."""

from app.application.ports.ai_service import IAIService
from app.config.settings import get_settings
from app.infrastructure.ai.adapters import GeminiAIService
from app.infrastructure.ai.gemini_client import GeminiClient

__all__ = [
    "IAIService",
    "GeminiClient",
    "GeminiAIService",
    "create_ai_service",
]


def create_ai_service() -> IAIService:
    """AIサービスのファクトリ関数

    設定から必要なパラメータを取得し、
    GeminiClientとGeminiAIServiceを初期化して返す

    Returns:
        IAIService: AIサービスのインスタンス
    """
    settings = get_settings()

    # GeminiClientを初期化
    gemini_client = GeminiClient(
        project_id=settings.google_cloud_project,
        location=settings.google_cloud_location,
        model_name=settings.gemini_model_name,
    )

    # GeminiAIServiceを生成（設定値をデフォルトパラメータとして渡す）
    ai_service = GeminiAIService(
        gemini_client=gemini_client,
        default_temperature=settings.gemini_temperature,
        default_max_output_tokens=settings.gemini_max_output_tokens,
        default_timeout_seconds=settings.gemini_timeout_seconds,
    )

    return ai_service
