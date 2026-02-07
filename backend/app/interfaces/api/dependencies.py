"""API依存性注入の定義"""

from functools import lru_cache

from app.application.ports.ai_service import IAIService
from app.application.ports.image_generation_service import IImageGenerationService
from app.application.ports.storage_service import IStorageService
from app.application.use_cases.generate_spot_images import GenerateSpotImagesUseCase
from app.config.settings import Settings, get_settings
from app.infrastructure.ai.adapters import GeminiAIService
from app.infrastructure.ai.gemini_client import GeminiClient
from app.infrastructure.ai.image_generation_client import ImageGenerationClient
from app.infrastructure.storage.factory import create_storage_service


async def get_settings_dependency() -> Settings:
    """設定のシングルトンインスタンスを取得する依存性

    Returns:
        Settings: アプリケーション設定
    """
    return get_settings()


@lru_cache(maxsize=1)
def get_storage_service() -> IStorageService:
    """ストレージサービスのシングルトンインスタンスを取得する

    Returns:
        IStorageService: ストレージサービス実装
    """
    settings = get_settings()
    return create_storage_service(settings)


async def get_storage_service_dependency() -> IStorageService:
    """ストレージサービスの依存性

    Returns:
        IStorageService: ストレージサービス
    """
    return get_storage_service()


@lru_cache(maxsize=1)
def get_ai_service() -> GeminiAIService:
    """AIサービスのシングルトンインスタンスを取得する

    Returns:
        GeminiAIService: AIサービス実装（IAIServiceとIImageGenerationServiceの両方を実装）

    Raises:
        ValueError: GOOGLE_CLOUD_PROJECTが設定されていない場合
    """
    settings = get_settings()

    if not settings.google_cloud_project:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required for AI service")

    gemini_client = GeminiClient(
        project_id=settings.google_cloud_project,
        location=settings.google_cloud_location,
        model_name=settings.gemini_model_name,
    )

    image_generation_client = ImageGenerationClient(
        project_id=settings.google_cloud_project,
        location=settings.image_generation_location,
        model_name=settings.image_generation_model,
    )

    return GeminiAIService(
        gemini_client=gemini_client,
        image_generation_client=image_generation_client,
        default_temperature=settings.gemini_temperature,
        default_max_output_tokens=settings.gemini_max_output_tokens,
        default_timeout_seconds=settings.gemini_timeout_seconds,
    )


async def get_ai_service_dependency() -> IAIService:
    """AIサービスの依存性

    Returns:
        IAIService: AIサービス
    """
    return get_ai_service()


def get_image_generation_service() -> IImageGenerationService:
    """画像生成サービスのインスタンスを取得する

    Returns:
        IImageGenerationService: 画像生成サービス実装
    """
    return get_ai_service()


def create_spot_images_use_case(
    image_generation_service: IImageGenerationService,
    storage_service: IStorageService,
    guide_repository,  # ITravelGuideRepository
) -> GenerateSpotImagesUseCase:
    """スポット画像生成ユースケースを作成する

    Args:
        image_generation_service: 画像生成サービス
        storage_service: ストレージサービス
        guide_repository: 旅行ガイドリポジトリ

    Returns:
        GenerateSpotImagesUseCase: スポット画像生成ユースケース

    Note:
        max_concurrentは設定から取得されます
    """
    settings = get_settings()
    return GenerateSpotImagesUseCase(
        image_generation_service=image_generation_service,
        storage_service=storage_service,
        guide_repository=guide_repository,
        max_concurrent=settings.image_generation_max_concurrent,
    )


# 将来的にデータベースセッションやリポジトリの依存性を追加予定
# 例:
# async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
#     """データベースセッションの依存性"""
#     async with async_session_maker() as session:
#         yield session
