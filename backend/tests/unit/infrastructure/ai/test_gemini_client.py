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
    part = MagicMock()
    part.text = text
    content = MagicMock()
    content.parts = [part]
    candidate = MagicMock()
    candidate.content = content
    response = MagicMock()
    response.candidates = [candidate]
    return response


@pytest.fixture
def gemini_client():
    """GeminiClientのフィクスチャ

    前提条件: テスト用の設定でGeminiClientを初期化する
    """
    return GeminiClient(
        project_id="test-project",
        location="asia-northeast1",
        model_name="gemini-2.5-flash",
    )


@pytest.mark.asyncio
async def test_generate_text_success(gemini_client):
    """テキスト生成の成功ケース

    前提条件: GenerativeModelが正常なレスポンスを返す
    検証項目: 生成されたテキストが返されること
    """
    # モックレスポンスの準備
    mock_response = _build_response_with_text("生成されたテキスト")

    # GenerativeModelをモック
    with patch(
        "app.infrastructure.ai.gemini_client.GenerativeModel"
    ) as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model

        # テキスト生成を実行
        result = await gemini_client.generate_content(
            prompt="テストプロンプト",
            system_instruction="システム命令",
            temperature=0.7,
            max_output_tokens=1024,
        )

        # 検証
        assert result == "生成されたテキスト"
        mock_model.generate_content_async.assert_called_once()


@pytest.mark.asyncio
async def test_generate_with_search_success(gemini_client):
    """Google Search統合の成功ケース

    前提条件: Google Searchツールを指定してGenerativeModelが正常なレスポンスを返す
    検証項目: 検索結果を含むテキストが返されること
    """
    # モックレスポンスの準備
    mock_response = _build_response_with_text("検索結果を含む生成テキスト")

    # モックツール
    mock_tool = MagicMock()

    # GapicToolをモック
    mock_gapic_tool = MagicMock()
    mock_gapic_tool.GoogleSearch = MagicMock(return_value=MagicMock())

    # GenerativeModelをモック
    with patch(
        "app.infrastructure.ai.gemini_client.GenerativeModel"
    ) as mock_model_class, patch(
        "app.infrastructure.ai.gemini_client.GapicTool", mock_gapic_tool
    ), patch(
        "app.infrastructure.ai.gemini_client.Tool"
    ) as mock_tool_class:
        mock_tool_class._from_gapic.return_value = mock_tool

        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model

        # Google Search統合でテキスト生成を実行
        result = await gemini_client.generate_content(
            prompt="最新の観光情報を教えて",
            tools=["google_search"],
            temperature=0.0,
        )

        # 検証
        assert result == "検索結果を含む生成テキスト"
        mock_model.generate_content_async.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_image_success(gemini_client):
    """画像分析の成功ケース

    前提条件: 画像URIを含むリクエストでGenerativeModelが正常なレスポンスを返す
    検証項目: 画像分析結果のテキストが返されること
    """
    # モックレスポンスの準備
    mock_response = _build_response_with_text("この画像には富士山が写っています")

    # GenerativeModelをモック
    with patch(
        "app.infrastructure.ai.gemini_client.GenerativeModel"
    ) as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model

        # 画像分析を実行
        result = await gemini_client.generate_content(
            prompt="この画像について説明してください",
            images=["gs://bucket/image.jpg"],
            temperature=0.7,
        )

        # 検証
        assert result == "この画像には富士山が写っています"
        mock_model.generate_content_async.assert_called_once()


@pytest.mark.asyncio
async def test_generate_structured_data_success(gemini_client):
    """JSON構造化出力の成功ケース

    前提条件: JSONスキーマを指定してGenerativeModelが正常なレスポンスを返す
    検証項目: スキーマに従った構造化データが返されること
    """
    # モックレスポンスの準備
    expected_data = {"name": "富士山", "type": "自然"}
    mock_response = _build_response_with_text(json.dumps(expected_data))

    # GenerativeModelをモック
    with patch(
        "app.infrastructure.ai.gemini_client.GenerativeModel"
    ) as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model

        # JSON構造化出力を実行
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

        # 検証
        assert result == expected_data
        mock_model.generate_content_async.assert_called_once()


@pytest.mark.asyncio
async def test_handle_api_error(gemini_client):
    """APIエラーハンドリング

    前提条件: GenerativeModelが不正リクエストエラーを返す
    検証項目: AIServiceInvalidRequestError例外が発生すること
    """
    # GenerativeModelをモック（エラーを返す）
    with patch(
        "app.infrastructure.ai.gemini_client.GenerativeModel"
    ) as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(
            side_effect=google_exceptions.InvalidArgument("Invalid request")
        )
        mock_model_class.return_value = mock_model

        # エラーが発生することを検証
        with pytest.raises(AIServiceInvalidRequestError):
            await gemini_client.generate_content(
                prompt="テストプロンプト",
            )


@pytest.mark.asyncio
async def test_retry_on_transient_error(gemini_client):
    """一時的エラーのリトライ動作

    前提条件: 最初の2回はクォータ超過エラー、3回目は成功
    検証項目: リトライ後に正常なレスポンスが返されること
    """
    # モックレスポンスの準備
    mock_response = _build_response_with_text("リトライ後の成功レスポンス")

    # GenerativeModelをモック（最初の2回はエラー、3回目は成功）
    with patch(
        "app.infrastructure.ai.gemini_client.GenerativeModel"
    ) as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(
            side_effect=[
                google_exceptions.ResourceExhausted("Quota exceeded"),
                google_exceptions.ResourceExhausted("Quota exceeded"),
                mock_response,
            ]
        )
        mock_model_class.return_value = mock_model

        # リトライ処理を高速化するためにバックオフをモック
        with patch.object(gemini_client, "_exponential_backoff", new=AsyncMock()):
            # テキスト生成を実行（リトライあり）
            result = await gemini_client.generate_content(
                prompt="テストプロンプト",
                max_retries=3,
            )

            # 検証
            assert result == "リトライ後の成功レスポンス"
            assert mock_model.generate_content_async.call_count == 3


@pytest.mark.asyncio
async def test_max_retries_exceeded(gemini_client):
    """最大リトライ回数超過

    前提条件: すべてのリトライでクォータ超過エラーが発生
    検証項目: AIServiceQuotaExceededError例外が発生すること
    """
    # GenerativeModelをモック（常にエラーを返す）
    with patch(
        "app.infrastructure.ai.gemini_client.GenerativeModel"
    ) as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(
            side_effect=google_exceptions.ResourceExhausted("Quota exceeded")
        )
        mock_model_class.return_value = mock_model

        # リトライ処理を高速化するためにバックオフをモック
        with patch.object(gemini_client, "_exponential_backoff", new=AsyncMock()):
            # エラーが発生することを検証
            with pytest.raises(AIServiceQuotaExceededError):
                await gemini_client.generate_content(
                    prompt="テストプロンプト",
                    max_retries=3,
                )

            # 最大リトライ回数分呼び出されたことを検証
            assert mock_model.generate_content_async.call_count == 3


@pytest.mark.asyncio
async def test_connection_error(gemini_client):
    """接続エラー

    前提条件: GenerativeModelがタイムアウトエラーを返す
    検証項目: AIServiceConnectionError例外が発生すること
    """
    # GenerativeModelをモック（タイムアウトエラーを返す）
    with patch(
        "app.infrastructure.ai.gemini_client.GenerativeModel"
    ) as mock_model_class:
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(
            side_effect=google_exceptions.DeadlineExceeded("Timeout")
        )
        mock_model_class.return_value = mock_model

        # リトライ処理を高速化するためにバックオフをモック
        with patch.object(gemini_client, "_exponential_backoff", new=AsyncMock()):
            # エラーが発生することを検証
            with pytest.raises(AIServiceConnectionError):
                await gemini_client.generate_content(
                    prompt="テストプロンプト",
                    max_retries=3,
                )
