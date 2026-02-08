"""GeminiAIServiceのユニットテスト"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.infrastructure.ai.adapters import GeminiAIService
from app.infrastructure.ai.gemini_client import GeminiClient
from app.infrastructure.ai.image_generation_client import ImageGenerationClient


@pytest.fixture
def mock_gemini_client():
    """モックGeminiClientのフィクスチャ

    前提条件: GeminiClientの全メソッドをモック化する
    """
    mock_client = MagicMock(spec=GeminiClient)
    mock_client.generate_content = AsyncMock()
    mock_client.generate_content_with_schema = AsyncMock()
    return mock_client


@pytest.fixture
def mock_image_generation_client():
    """モックImageGenerationClientのフィクスチャ

    前提条件: ImageGenerationClientの全メソッドをモック化する
    """
    mock_client = MagicMock(spec=ImageGenerationClient)
    mock_client.generate_image = AsyncMock()
    return mock_client


@pytest.fixture
def gemini_service(mock_gemini_client, mock_image_generation_client):
    """GeminiAIServiceのフィクスチャ

    前提条件: モックGeminiClientとImageGenerationClientを使用してGeminiAIServiceを初期化する
    """
    return GeminiAIService(
        gemini_client=mock_gemini_client,
        image_generation_client=mock_image_generation_client,
        default_temperature=0.7,
        default_max_output_tokens=8192,
        default_timeout_seconds=60,
    )


@pytest.mark.asyncio
async def test_generate_text(gemini_service, mock_gemini_client):
    """基本的なテキスト生成

    前提条件: GeminiClientのgenerate_contentメソッドが正常なレスポンスを返す
    検証項目:
    - GeminiClientのgenerate_contentが適切なパラメータで呼び出されること
    - 生成されたテキストが返されること
    """
    # モックの戻り値を設定
    expected_text = "生成されたテキスト"
    mock_gemini_client.generate_content.return_value = expected_text

    # テキスト生成を実行
    result = await gemini_service.generate_text(
        prompt="テストプロンプト",
        system_instruction="システム命令",
        temperature=0.7,
        max_output_tokens=1024,
    )

    # 検証
    assert result == expected_text
    mock_gemini_client.generate_content.assert_called_once_with(
        prompt="テストプロンプト",
        system_instruction="システム命令",
        temperature=0.7,
        max_output_tokens=1024,
        timeout=60,
    )


@pytest.mark.asyncio
async def test_generate_with_search(gemini_service, mock_gemini_client):
    """Google Search統合

    前提条件: GeminiClientのgenerate_contentメソッドがgoogle_searchツールを使用してレスポンスを返す
    検証項目:
    - GeminiClientのgenerate_contentがtools=["google_search", "validate_url"]で呼び出されること
    - 検索結果を含むテキストが返されること
    """
    # モックの戻り値を設定
    expected_text = "検索結果を含む生成テキスト"
    mock_gemini_client.generate_content.return_value = expected_text

    # Google Search統合でテキスト生成を実行
    result = await gemini_service.generate_with_search(
        prompt="最新の観光情報を教えて",
        system_instruction="観光ガイド",
        temperature=0.0,
        max_output_tokens=2048,
    )

    # 検証
    assert result == expected_text
    mock_gemini_client.generate_content.assert_called_once_with(
        prompt="最新の観光情報を教えて",
        system_instruction="観光ガイド",
        tools=["google_search", "validate_url"],
        temperature=0.0,
        max_output_tokens=2048,
        timeout=120,
    )


@pytest.mark.asyncio
async def test_analyze_image(gemini_service, mock_gemini_client):
    """画像分析

    前提条件: GeminiClientのgenerate_contentメソッドが画像URIを使用してレスポンスを返す
    検証項目:
    - GeminiClientのgenerate_contentがimages=[image_uri]で呼び出されること
    - 画像分析結果のテキストが返されること
    """
    # モックの戻り値を設定
    expected_text = "この画像には富士山が写っています"
    mock_gemini_client.generate_content.return_value = expected_text

    # 画像分析を実行
    result = await gemini_service.analyze_image(
        prompt="この画像について説明してください",
        image_uri="gs://bucket/image.jpg",
        system_instruction="画像分析AI",
        temperature=0.7,
        max_output_tokens=1024,
    )

    # 検証
    assert result == expected_text
    mock_gemini_client.generate_content.assert_called_once_with(
        prompt="この画像について説明してください",
        system_instruction="画像分析AI",
        tools=None,
        images=["gs://bucket/image.jpg"],
        temperature=0.7,
        max_output_tokens=1024,
        timeout=60,
    )


@pytest.mark.asyncio
async def test_generate_structured_data(gemini_service, mock_gemini_client):
    """JSON構造化出力

    前提条件: GeminiClientのgenerate_content_with_schemaメソッドが構造化データを返す
    検証項目:
    - GeminiClientのgenerate_content_with_schemaが適切なパラメータで呼び出されること
    - スキーマに従った構造化データが返されること
    """
    # モックの戻り値を設定
    expected_data = {"name": "富士山", "type": "自然", "height": 3776}
    mock_gemini_client.generate_content_with_schema.return_value = expected_data

    # JSON構造化出力を実行
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "height": {"type": "number"},
        },
    }
    result = await gemini_service.generate_structured_data(
        prompt="富士山の情報を返してください",
        response_schema=schema,
        system_instruction="観光情報AI",
        temperature=0.0,
        max_output_tokens=1024,
    )

    # 検証
    assert result == expected_data
    mock_gemini_client.generate_content_with_schema.assert_called_once_with(
        prompt="富士山の情報を返してください",
        response_schema=schema,
        system_instruction="観光情報AI",
        temperature=0.0,
        max_output_tokens=1024,
        timeout=60,
    )


@pytest.mark.asyncio
async def test_generate_text_with_defaults(gemini_service, mock_gemini_client):
    """デフォルトパラメータでのテキスト生成

    前提条件: オプションパラメータを省略してgenerate_textを呼び出す
    検証項目:
    - 設定のデフォルト値が適用されること
    - 生成されたテキストが返されること
    """
    # モックの戻り値を設定
    expected_text = "デフォルト設定で生成されたテキスト"
    mock_gemini_client.generate_content.return_value = expected_text

    # デフォルトパラメータでテキスト生成を実行
    result = await gemini_service.generate_text(
        prompt="テストプロンプト",
    )

    # 検証（設定から取得したデフォルト値が使用される）
    assert result == expected_text
    mock_gemini_client.generate_content.assert_called_once_with(
        prompt="テストプロンプト",
        system_instruction=None,
        temperature=0.7,  # fixtureで設定したdefault_temperature
        max_output_tokens=8192,  # fixtureで設定したdefault_max_output_tokens
        timeout=60,
    )


@pytest.mark.asyncio
async def test_generate_image(gemini_service, mock_image_generation_client):
    """画像生成

    前提条件: ImageGenerationClientのgenerate_imageメソッドが画像データを返す
    検証項目:
    - ImageGenerationClientのgenerate_imageが適切なパラメータで呼び出されること
    - 生成された画像データ（bytes）が返されること
    """
    # モックの戻り値を設定
    expected_image_data = b"fake_image_data"
    mock_image_generation_client.generate_image.return_value = expected_image_data

    # 画像生成を実行
    result = await gemini_service.generate_image(
        prompt="A realistic photo of a historical temple in Kyoto",
        aspect_ratio="16:9",
        timeout=60,
    )

    # 検証
    assert result == expected_image_data
    mock_image_generation_client.generate_image.assert_called_once_with(
        prompt="A realistic photo of a historical temple in Kyoto",
        aspect_ratio="16:9",
        timeout=60,
    )


@pytest.mark.asyncio
async def test_generate_image_prompt(gemini_service, mock_gemini_client):
    """画像生成プロンプトの生成

    前提条件: GeminiClientのgenerate_contentメソッドがプロンプトを返す
    検証項目:
    - GeminiClientのgenerate_contentが適切なパラメータで呼び出されること
    - 生成されたプロンプトが返されること
    - プロンプトテンプレートにスポット名と歴史的背景が含まれること
    """
    # モックの戻り値を設定
    expected_prompt = (
        "京都の金閣寺の写真。1397年に建立された金色の寺院。リアルで写真のようなスタイル。"
    )
    mock_gemini_client.generate_content.return_value = expected_prompt

    # 画像生成プロンプトを生成
    result = await gemini_service.generate_image_prompt(
        spot_name="金閣寺",
        historical_background="1397年に建立された金色の寺院",
        temperature=0.7,
    )

    # 検証
    assert result == expected_prompt
    mock_gemini_client.generate_content.assert_called_once()
    call_kwargs = mock_gemini_client.generate_content.call_args.kwargs

    # プロンプトにスポット名と歴史的背景が含まれることを確認
    assert "金閣寺" in call_kwargs["prompt"]
    assert "1397年に建立された金色の寺院" in call_kwargs["prompt"]
    assert "Vertex AI Image Generation API" in call_kwargs["prompt"]
    assert "リアルで写真のようなスタイル" in call_kwargs["prompt"]

    # パラメータの確認
    assert call_kwargs["temperature"] == 0.7
    assert call_kwargs["max_output_tokens"] == 2048
    assert call_kwargs["timeout"] == 60
