"""GeminiClientのユニットテスト"""

from __future__ import annotations

import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.api_core import exceptions as google_exceptions
from pydantic import Field

from app.infrastructure.ai.exceptions import (
    AIServiceConnectionError,
    AIServiceInvalidRequestError,
    AIServiceQuotaExceededError,
)
from app.infrastructure.ai.gemini_client import GeminiClient
from app.infrastructure.ai.schemas.base import GeminiResponseSchema


class SimpleTestSchema(GeminiResponseSchema):
    """テスト用のシンプルなスキーマ"""

    name: str = Field(description="名前")
    type: str = Field(description="タイプ")


class SpotTestSchema(GeminiResponseSchema):
    """テスト用の観光スポットスキーマ"""

    spot: str = Field(description="スポット名")
    confidence: float = Field(description="信頼度")


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
async def test_generate_with_search_logs_diagnostics_when_grounding_present(caplog: pytest.LogCaptureFixture):
    """Google Search利用時に診断ログが出力されること."""
    query = "中尊寺 公式サイト"

    part = MagicMock()
    function_call = MagicMock()
    function_call.name = "google_search"
    part.function_call = function_call

    content = MagicMock()
    content.parts = [part]

    web = MagicMock()
    web.uri = "https://www.chusonji.or.jp/"
    chunk = MagicMock()
    chunk.web = web

    grounding_metadata = MagicMock()
    grounding_metadata.grounding_chunks = [chunk]
    grounding_metadata.web_search_queries = [query]

    candidate = MagicMock()
    candidate.content = content
    candidate.grounding_metadata = grounding_metadata

    mock_response = MagicMock()
    mock_response.text = "検索結果を含む生成テキスト"
    mock_response.candidates = [candidate]

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    with caplog.at_level(logging.INFO):
        await gemini_client.generate_content(
            prompt="中尊寺の歴史を調べて",
            tools=["google_search"],
        )

    assert "Google Search tool diagnostics" in caplog.text
    assert "grounding_chunk_count" in caplog.text


@pytest.mark.asyncio
async def test_generate_with_search_warns_when_no_evidence(caplog: pytest.LogCaptureFixture):
    """Google Searchを要求しても証跡がない場合にWarningが出力されること."""
    mock_response = MagicMock()
    mock_response.text = "検索結果を含む生成テキスト"
    mock_response.candidates = []

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    with caplog.at_level(logging.WARNING):
        await gemini_client.generate_content(
            prompt="中尊寺の歴史を調べて",
            tools=["google_search"],
        )

    assert "no grounding/function-call evidence was found" in caplog.text


@pytest.mark.asyncio
async def test_generate_text_fallback_to_candidates_when_response_text_is_empty():
    """response.textが空でもcandidates.parts.textから復元できること."""
    part = MagicMock()
    part.text = "候補テキスト"
    content = MagicMock()
    content.parts = [part]
    candidate = MagicMock()
    candidate.content = content

    mock_response = MagicMock()
    mock_response.text = ""
    mock_response.candidates = [candidate]

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    result = await gemini_client.generate_content(prompt="テストプロンプト")

    assert result == "候補テキスト"
    mock_async_client.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_text_raises_when_response_text_and_candidates_are_empty():
    """response.textとcandidatesの双方が空の場合は例外を送出すること."""
    mock_response = MagicMock()
    mock_response.text = ""
    mock_response.candidates = []

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    with pytest.raises(AIServiceInvalidRequestError, match="Response text is empty"):
        await gemini_client.generate_content(prompt="テストプロンプト")


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

    result = await gemini_client.generate_content_with_schema(
        prompt="富士山の情報を返してください",
        response_schema=SimpleTestSchema,
        temperature=0.0,
    )

    assert result == expected_data
    mock_async_client.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_structured_data_success_with_parsed_and_empty_text():
    """response.textが空でもresponse.parsedから構造化データを取得できること."""
    expected_data = {"name": "富士山", "type": "自然"}
    mock_response = MagicMock()
    mock_response.text = ""
    mock_response.parsed = expected_data

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    result = await gemini_client.generate_content_with_schema(
        prompt="富士山の情報を返してください",
        response_schema=SimpleTestSchema,
        temperature=0.0,
    )

    assert result == expected_data
    mock_async_client.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_structured_data_success_with_candidates_text():
    """response.textが空でもcandidates.parts.textのJSONを復元できること."""
    expected_data = {"name": "富士山", "type": "自然"}
    part = MagicMock()
    part.text = json.dumps(expected_data)
    content = MagicMock()
    content.parts = [part]
    candidate = MagicMock()
    candidate.content = content

    mock_response = MagicMock()
    mock_response.text = ""
    mock_response.parsed = None
    mock_response.candidates = [candidate]

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    result = await gemini_client.generate_content_with_schema(
        prompt="富士山の情報を返してください",
        response_schema=SimpleTestSchema,
        temperature=0.0,
    )

    assert result == expected_data
    mock_async_client.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_structured_data_fallback_from_invalid_text_to_candidates():
    """response.textのJSONが壊れていてもcandidates.parts.textから復元できること."""
    expected_data = {"name": "富士山", "type": "自然"}
    part = MagicMock()
    part.text = json.dumps(expected_data)
    content = MagicMock()
    content.parts = [part]
    candidate = MagicMock()
    candidate.content = content

    mock_response = MagicMock()
    mock_response.text = '{"name":"富士山","type":"自然'
    mock_response.parsed = None
    mock_response.candidates = [candidate]

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    result = await gemini_client.generate_content_with_schema(
        prompt="富士山の情報を返してください",
        response_schema=SimpleTestSchema,
        temperature=0.0,
    )

    assert result == expected_data
    mock_async_client.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_structured_data_invalid_json_raises_invalid_request_error():
    """構造化JSONが壊れている場合はAIServiceInvalidRequestErrorを送出すること."""
    mock_response = MagicMock()
    mock_response.text = '{"name":"富士山","type":"自然'
    mock_response.parsed = None
    mock_response.candidates = None

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    with pytest.raises(AIServiceInvalidRequestError, match="Structured response JSON is invalid"):
        await gemini_client.generate_content_with_schema(
            prompt="富士山の情報を返してください",
            response_schema=SimpleTestSchema,
            temperature=0.0,
        )


@pytest.mark.asyncio
async def test_generate_structured_data_with_images_success():
    """画像付きJSON構造化出力の成功ケース

    前提条件: 画像URIとJSONスキーマを指定してSDKが正常なレスポンスを返す
    検証項目: 画像付きの構造化データが返され、contentsが配列になること
    """
    expected_data = {"spot": "清水寺", "confidence": 0.95}
    mock_response = _build_response_with_text(json.dumps(expected_data))
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    result = await gemini_client.generate_content_with_schema(
        prompt="画像の観光スポットを特定してください",
        response_schema=SpotTestSchema,
        images=["gs://bucket/kyoto.jpg"],
        temperature=0.0,
    )

    assert result == expected_data
    mock_async_client.models.generate_content.assert_called_once()
    contents = mock_async_client.models.generate_content.call_args.kwargs["contents"]
    assert isinstance(contents, list)
    assert len(contents) == 2


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
