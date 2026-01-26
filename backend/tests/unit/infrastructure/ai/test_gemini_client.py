"""GeminiClientのユニットテスト"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.api_core import exceptions as google_exceptions

from app.infrastructure.ai.exceptions import (
    AIServiceConnectionError,
    AIServiceInvalidRequestError,
    AIServiceQuotaExceededError,
)
from app.infrastructure.ai.gemini_client import GeminiClient


def _build_response_with_text(text: str) -> MagicMock:
    """候補テキストを含むレスポンスを構築する"""
    response = MagicMock()
    response.text = text
    return response


def _build_client_and_async_client() -> tuple[GeminiClient, MagicMock]:
    """テスト用のGeminiClientと内部の非同期クライアントを構築する"""
    with patch("app.infrastructure.ai.gemini_client.genai.Client") as mock_client_class:
        mock_async_client = MagicMock()
        mock_async_client.models.generate_content = AsyncMock()
        mock_client = MagicMock()
        mock_client.aio = mock_async_client
        mock_client_class.return_value = mock_client
        client = GeminiClient(
            project_id="test-project",
            location="asia-northeast1",
            model_name="gemini-2.5-flash",
        )
    return client, mock_async_client


@pytest.mark.asyncio
async def test_generate_text_success():
    """テキスト生成の成功ケース

    前提条件: SDKが正常なレスポンスを返す
    検証項目: 生成されたテキストが返されること
    """
    mock_response = _build_response_with_text("生成されたテキスト")
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    result = await gemini_client.generate_content(
        prompt="テストプロンプト",
        system_instruction="システム命令",
        temperature=0.7,
        max_output_tokens=1024,
    )

    assert result == "生成されたテキスト"
    mock_async_client.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_with_search_success():
    """Google Search統合の成功ケース

    前提条件: Google Searchツールを指定してSDKが正常なレスポンスを返す
    検証項目: 検索結果を含むテキストが返されること
    """
    mock_response = _build_response_with_text("検索結果を含む生成テキスト")
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    result = await gemini_client.generate_content(
        prompt="最新の観光情報を教えて",
        tools=["google_search"],
        temperature=0.0,
    )

    assert result == "検索結果を含む生成テキスト"
    mock_async_client.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_image_success():
    """画像分析の成功ケース

    前提条件: 画像URIを含むリクエストでSDKが正常なレスポンスを返す
    検証項目: 画像分析結果のテキストが返されること
    """
    mock_response = _build_response_with_text("この画像には富士山が写っています")
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    result = await gemini_client.generate_content(
        prompt="この画像について説明してください",
        images=["gs://bucket/image.jpg"],
        temperature=0.7,
    )

    assert result == "この画像には富士山が写っています"
    mock_async_client.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_structured_data_success():
    """JSON構造化出力の成功ケース

    前提条件: JSONスキーマを指定してSDKが正常なレスポンスを返す
    検証項目: スキーマに従った構造化データが返されること
    """
    expected_data = {"name": "富士山", "type": "自然"}
    mock_response = _build_response_with_text(json.dumps(expected_data))
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
        },
    }
    result = await gemini_client.generate_content_with_schema(
        prompt="富士山の情報を返してください",
        response_schema=schema,
        temperature=0.0,
    )

    assert result == expected_data
    mock_async_client.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_handle_api_error():
    """APIエラーハンドリング

    前提条件: SDKが不正リクエストエラーを返す
    検証項目: AIServiceInvalidRequestError例外が発生すること
    """
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(
        side_effect=google_exceptions.InvalidArgument("Invalid request")
    )

    with pytest.raises(AIServiceInvalidRequestError):
        await gemini_client.generate_content(prompt="テストプロンプト")


@pytest.mark.asyncio
async def test_retry_on_transient_error():
    """一時的エラーのリトライ動作

    前提条件: 最初の2回はクォータ超過エラー、3回目は成功
    検証項目: リトライ後に正常なレスポンスが返されること
    """
    mock_response = _build_response_with_text("リトライ後の成功レスポンス")
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(
        side_effect=[
            google_exceptions.ResourceExhausted("Quota exceeded"),
            google_exceptions.ResourceExhausted("Quota exceeded"),
            mock_response,
        ]
    )

    with patch.object(gemini_client, "_exponential_backoff", new=AsyncMock()):
        result = await gemini_client.generate_content(
            prompt="テストプロンプト",
            max_retries=3,
        )

        assert result == "リトライ後の成功レスポンス"
        assert mock_async_client.models.generate_content.call_count == 3


@pytest.mark.asyncio
async def test_max_retries_exceeded():
    """最大リトライ回数超過

    前提条件: すべてのリトライでクォータ超過エラーが発生
    検証項目: AIServiceQuotaExceededError例外が発生すること
    """
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(
        side_effect=google_exceptions.ResourceExhausted("Quota exceeded")
    )

    with patch.object(gemini_client, "_exponential_backoff", new=AsyncMock()):
        with pytest.raises(AIServiceQuotaExceededError):
            await gemini_client.generate_content(
                prompt="テストプロンプト",
                max_retries=3,
            )

        assert mock_async_client.models.generate_content.call_count == 3


@pytest.mark.asyncio
async def test_connection_error():
    """接続エラー

    前提条件: SDKがタイムアウトエラーを返す
    検証項目: AIServiceConnectionError例外が発生すること
    """
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(
        side_effect=google_exceptions.DeadlineExceeded("Timeout")
    )

    with patch.object(gemini_client, "_exponential_backoff", new=AsyncMock()):
        with pytest.raises(AIServiceConnectionError):
            await gemini_client.generate_content(
                prompt="テストプロンプト",
                max_retries=3,
            )
