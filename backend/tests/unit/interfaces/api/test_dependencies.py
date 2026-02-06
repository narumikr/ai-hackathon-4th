"""依存性注入のテスト"""

import pytest

from app.application.ports.ai_service import IAIService
from app.application.ports.storage_service import IStorageService
from app.application.use_cases.generate_spot_images import GenerateSpotImagesUseCase
from app.config.settings import Settings
from app.infrastructure.ai.adapters import GeminiAIService
from app.infrastructure.ai.gemini_client import GeminiClient
from app.infrastructure.ai.image_generation_client import ImageGenerationClient
from app.interfaces.api.dependencies import (
    create_spot_images_use_case,
    get_ai_service,
    get_storage_service,
)


def test_get_ai_service_returns_gemini_ai_service(monkeypatch: pytest.MonkeyPatch) -> None:
    """AIサービスの依存性注入がGeminiAIServiceを返すことを確認する"""
    # 環境変数を設定
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "asia-northeast1")

    # キャッシュをクリア
    from app.config.settings import get_settings

    get_settings.cache_clear()
    get_ai_service.cache_clear()

    # 実行
    ai_service = get_ai_service()

    # 検証
    assert isinstance(ai_service, GeminiAIService)
    assert isinstance(ai_service, IAIService)


def test_get_ai_service_raises_error_when_project_not_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """GOOGLE_CLOUD_PROJECTが設定されていない場合にエラーが発生することを確認する"""
    # 環境変数をクリア
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_LOCATION", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/testdb")

    # キャッシュをクリア（設定とAIサービスの両方）
    from app.config.settings import Settings, get_settings

    # .env 由来の値を読まないようにする
    monkeypatch.setitem(Settings.model_config, "env_file", None)

    get_settings.cache_clear()
    get_ai_service.cache_clear()

    # 実行 & 検証
    with pytest.raises(ValueError, match="GOOGLE_CLOUD_PROJECT environment variable is required"):
        get_ai_service()


def test_get_storage_service_returns_storage_service() -> None:
    """ストレージサービスの依存性注入がIStorageServiceを返すことを確認する"""
    # キャッシュをクリア
    get_storage_service.cache_clear()

    # 実行
    storage_service = get_storage_service()

    # 検証
    assert isinstance(storage_service, IStorageService)


def test_create_spot_images_use_case_returns_use_case(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """スポット画像生成ユースケースの作成が正しく動作することを確認する"""
    # 環境変数を設定
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "asia-northeast1")
    monkeypatch.setenv("IMAGE_GENERATION_MAX_CONCURRENT", "5")

    # キャッシュをクリア（設定、AIサービス、ストレージサービス）
    from app.config.settings import get_settings

    get_settings.cache_clear()
    get_ai_service.cache_clear()
    get_storage_service.cache_clear()

    # 依存性を取得
    ai_service = get_ai_service()
    storage_service = get_storage_service()

    # モックリポジトリを作成
    class MockGuideRepository:
        pass

    guide_repository = MockGuideRepository()

    # 実行
    use_case = create_spot_images_use_case(
        ai_service=ai_service,
        storage_service=storage_service,
        guide_repository=guide_repository,
    )

    # 検証
    assert isinstance(use_case, GenerateSpotImagesUseCase)
    assert use_case._ai_service is ai_service
    assert use_case._storage_service is storage_service
    assert use_case._guide_repository is guide_repository
    assert use_case._max_concurrent == 5


def test_ai_service_has_both_clients(monkeypatch: pytest.MonkeyPatch) -> None:
    """AIサービスがGeminiClientとImageGenerationClientの両方を持つことを確認する"""
    # 環境変数を設定
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "asia-northeast1")

    # キャッシュをクリア
    from app.config.settings import get_settings

    get_settings.cache_clear()
    get_ai_service.cache_clear()

    # 実行
    ai_service = get_ai_service()

    # 検証
    assert isinstance(ai_service, GeminiAIService)
    assert hasattr(ai_service, "client")
    assert hasattr(ai_service, "image_client")
    assert isinstance(ai_service.client, GeminiClient)
    assert isinstance(ai_service.image_client, ImageGenerationClient)
