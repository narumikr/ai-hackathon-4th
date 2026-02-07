"""AI infrastructure layer exports and factory functions."""

from app.application.ports.ai_service import IAIService
from app.application.ports.image_generation_service import IImageGenerationService
from app.config.settings import get_settings
from app.infrastructure.ai.adapters import GeminiAIService
from app.infrastructure.ai.gemini_client import GeminiClient
from app.infrastructure.ai.image_generation_client import ImageGenerationClient

__all__ = [
    "IAIService",
    "IImageGenerationService",
    "GeminiClient",
    "ImageGenerationClient",
    "GeminiAIService",
    "create_ai_service",
]


def create_ai_service() -> GeminiAIService:
    """AIサービスのファクトリ関数

    設定から必要なパラメータを取得し、
    GeminiClientとGeminiAIServiceを初期化して返す

    Returns:
        GeminiAIService: AIサービスのインスタンス（IAIServiceとIImageGenerationServiceの両方を実装）

    Raises:
        ValueError: GOOGLE_CLOUD_PROJECTが設定されていない場合
    """
    settings = get_settings()

    if not settings.google_cloud_project:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required for AI service")

    # GeminiClientを初期化
    gemini_client = GeminiClient(
        project_id=settings.google_cloud_project,
        location=settings.google_cloud_location,
        model_name=settings.gemini_model_name,
    )

    # ImageGenerationClientを初期化
    image_generation_client = ImageGenerationClient(
        project_id=settings.google_cloud_project,
        location=settings.image_generation_location,
        model_name=settings.image_generation_model,
    )

    # GeminiAIServiceを生成（設定値をデフォルトパラメータとして渡す）
    ai_service = GeminiAIService(
        gemini_client=gemini_client,
        image_generation_client=image_generation_client,
        default_temperature=settings.gemini_temperature,
        default_max_output_tokens=settings.gemini_max_output_tokens,
        default_timeout_seconds=settings.gemini_timeout_seconds,
    )

    return ai_service
