"""GeminiClientのユニットテスト"""

from __future__ import annotations

import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.error import URLError

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


def test_prepare_tools_skips_validate_url_model_tool() -> None:
    """validate_url はモデルツールに渡さず、google_search のみ構成されること。"""
    gemini_client, _ = _build_client_and_async_client()

    prepared_tools = gemini_client._prepare_tools(["google_search", "validate_url"])  # noqa: SLF001

    assert len(prepared_tools) == 1
    assert prepared_tools[0].google_search is not None


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
    mock_response = _build_response_with_text("検索結果を含む生成テキスト https://example.com/source")
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    with patch.object(
        gemini_client,
        "_validate_url_with_http_check",
        new=AsyncMock(return_value={"url": "https://example.com/source", "verdict": "valid", "reason": "ok"}),
    ):
        result = await gemini_client.generate_content(
            prompt="最新の観光情報を教えて",
            tools=["google_search"],
            temperature=0.0,
        )

    assert result == "検索結果を含む生成テキスト https://example.com/source [検証: valid]"
    mock_async_client.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_with_search_resolves_validate_url_tool_call():
    """validate_urlツール呼び出しがある場合に検証結果を反映して再生成すること。"""
    first_response = MagicMock()
    first_response.text = ""
    function_call = MagicMock()
    function_call.name = "validate_url"
    function_call.args = {"urls": ["https://example.com/source"]}
    part = MagicMock()
    part.function_call = function_call
    content = MagicMock()
    content.parts = [part]
    candidate = MagicMock()
    candidate.content = content
    first_response.candidates = [candidate]

    second_response = _build_response_with_text("https://example.com/source を使用した抽出結果")

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(
        side_effect=[first_response, second_response]
    )

    with patch.object(
        gemini_client,
        "_validate_url_with_http_check",
        new=AsyncMock(return_value={"url": "https://example.com/source", "verdict": "valid", "reason": "ok"}),
    ):
        result = await gemini_client.generate_content(
            prompt="出典候補を抽出してください",
            tools=["google_search", "validate_url"],
            temperature=0.0,
        )

    assert result == "https://example.com/source [検証: valid] を使用した抽出結果"
    assert mock_async_client.models.generate_content.call_count == 2


@pytest.mark.asyncio
async def test_generate_with_search_retries_when_response_has_no_urls():
    """URLが含まれない回答は再試行し、検証済みURL付き回答へ改善すること。"""
    first_response = _build_response_with_text("スポットの歴史情報です。")
    second_response = _build_response_with_text("https://example.com/source を使用した抽出結果")

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(
        side_effect=[first_response, second_response]
    )

    with patch.object(
        gemini_client,
        "_validate_url_with_http_check",
        new=AsyncMock(return_value={"url": "https://example.com/source", "verdict": "valid", "reason": "ok"}),
    ):
        result = await gemini_client.generate_content(
            prompt="出典候補を抽出してください",
            tools=["google_search"],
            temperature=0.0,
            max_retries=2,
        )

    assert result == "https://example.com/source [検証: valid] を使用した抽出結果"
    assert mock_async_client.models.generate_content.call_count == 2


@pytest.mark.asyncio
async def test_generate_with_search_returns_text_when_max_retries_reached_with_no_urls():
    """URLなしで最大試行に達した場合でもテキストを返すこと。"""
    response = _build_response_with_text("スポットの歴史情報です。")
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=response)

    result = await gemini_client.generate_content(
        prompt="出典候補を抽出してください",
        tools=["google_search"],
        temperature=0.0,
        max_retries=1,
    )

    assert result == "スポットの歴史情報です。"
    assert mock_async_client.models.generate_content.call_count == 1


@pytest.mark.asyncio
async def test_generate_with_search_passes_spot_context_to_url_validation():
    """スポット見出し付き本文ではURL検証にspot_nameとclaimが渡ること。"""
    response = _build_response_with_text(
        """
## スポット別の事実
### ひめゆりの塔
- 学徒隊の慰霊碑として建立された [出典: https://www.nippon.com/ja/guide-to-japan/gu900191/]
"""
    )
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=response)

    validate_mock = AsyncMock(
        return_value={
            "url": "https://www.nippon.com/ja/guide-to-japan/gu900191/",
            "verdict": "invalid",
            "reason": "relevance_mismatch",
            "spot_name": "ひめゆりの塔",
        }
    )
    with patch.object(gemini_client, "_validate_url_with_http_check", new=validate_mock):
        result = await gemini_client.generate_content(
            prompt="出典候補を抽出してください",
            tools=["google_search"],
            temperature=0.0,
            max_retries=1,
        )

    assert "[無効URL除去]" in result
    assert "https://www.nippon.com/ja/guide-to-japan/gu900191/" not in result
    assert validate_mock.await_count == 1
    call_kwargs = validate_mock.await_args_list[0].kwargs
    assert call_kwargs["spot_name"] == "ひめゆりの塔"
    assert "学徒隊の慰霊碑として建立された" in (call_kwargs["claim"] or "")


@pytest.mark.asyncio
async def test_generate_with_search_retry_uses_updated_feedback_prompt():
    """URL検証失敗時の再試行で、更新済みフィードバックプロンプトが送信されること。"""
    first_response = _build_response_with_text(
        "A [出典: https://valid.example.com] と B [出典: https://invalid.example.com]"
    )
    second_response = _build_response_with_text(
        "A [出典: https://valid.example.com] [検証: valid]"
    )

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(side_effect=[first_response, second_response])

    async def _validate(url: str, **_: object) -> dict[str, str]:
        if "://valid.example.com" in url:
            return {"url": url, "verdict": "valid", "reason": "ok"}
        return {"url": url, "verdict": "invalid", "reason": "network_error_URLError"}

    with patch.object(gemini_client, "_validate_url_with_http_check", new=AsyncMock(side_effect=_validate)):
        result = await gemini_client.generate_content(
            prompt="出典候補を抽出してください",
            tools=["google_search"],
            temperature=0.0,
            max_retries=2,
        )

    assert "https://valid.example.com" in result
    assert "[検証: valid]" in result
    assert mock_async_client.models.generate_content.call_count == 2
    second_call_contents = mock_async_client.models.generate_content.await_args_list[1].kwargs["contents"]
    assert "<url_validation_feedback>" in second_call_contents
    assert "https://valid.example.com" in second_call_contents
    assert "vertexaisearch.cloud.google.com" in second_call_contents
    assert "同義語・旧称・英語表記" in second_call_contents


@pytest.mark.asyncio
async def test_generate_with_search_returns_sanitized_text_when_max_retries_reached_with_invalid_urls():
    """invalid URLが残っていても最大試行到達時は除去済みテキストを返すこと。"""
    response = _build_response_with_text(
        "A [出典: https://valid.example.com] と B [出典: https://invalid.example.com]"
    )
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=response)

    async def _validate(url: str, **_: object) -> dict[str, str]:
        if "://valid.example.com" in url:
            return {"url": url, "verdict": "valid", "reason": "ok"}
        return {"url": url, "verdict": "invalid", "reason": "network_error_URLError"}

    with patch.object(gemini_client, "_validate_url_with_http_check", new=AsyncMock(side_effect=_validate)):
        result = await gemini_client.generate_content(
            prompt="出典候補を抽出してください",
            tools=["google_search"],
            temperature=0.0,
            max_retries=1,
        )

    assert "https://valid.example.com [検証: valid]" in result
    assert "https://invalid.example.com" not in result
    assert "[無効URL除去]" in result
    assert mock_async_client.models.generate_content.call_count == 1


@pytest.mark.asyncio
async def test_generate_with_search_reuses_cached_valid_urls_without_revalidation():
    """同一リクエスト内で一度validになったURLは再検証をスキップすること。"""
    first_response = _build_response_with_text(
        "A [出典: https://valid.example.com] と B [出典: https://invalid.example.com]"
    )
    second_response = _build_response_with_text(
        "A [出典: https://valid.example.com]"
    )

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(side_effect=[first_response, second_response])

    async def _validate(url: str, **_: object) -> dict[str, str]:
        if "://valid.example.com" in url:
            return {"url": url, "verdict": "valid", "reason": "ok"}
        return {"url": url, "verdict": "invalid", "reason": "network_error_URLError"}

    validate_mock = AsyncMock(side_effect=_validate)
    with patch.object(gemini_client, "_validate_url_with_http_check", new=validate_mock):
        result = await gemini_client.generate_content(
            prompt="出典候補を抽出してください",
            tools=["google_search"],
            temperature=0.0,
            max_retries=2,
        )

    assert "https://valid.example.com [検証: valid]" in result
    # 1回目で valid/invalid の2URLを検証し、2回目の valid はキャッシュで再検証しない。
    assert validate_mock.await_count == 2


@pytest.mark.asyncio
async def test_generate_with_search_early_accept_when_enough_valid_urls():
    """valid URLが一定数に達した場合は再試行せずearly acceptすること。"""
    response_text = "\n".join(
        [
            "- [出典: https://valid1.example.com]",
            "- [出典: https://valid2.example.com]",
            "- [出典: https://valid3.example.com]",
            "- [出典: https://valid4.example.com]",
            "- [出典: https://valid5.example.com]",
            "- [出典: https://invalid.example.com]",
        ]
    )
    first_response = _build_response_with_text(response_text)

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=first_response)

    async def _validate(url: str, **_: object) -> dict[str, str]:
        if "://invalid.example.com" in url:
            return {"url": url, "verdict": "invalid", "reason": "network_error_URLError"}
        return {"url": url, "verdict": "valid", "reason": "ok"}

    with patch.object(gemini_client, "_validate_url_with_http_check", new=AsyncMock(side_effect=_validate)):
        result = await gemini_client.generate_content(
            prompt="出典候補を抽出してください",
            tools=["google_search"],
            temperature=0.0,
            max_retries=5,
        )

    assert mock_async_client.models.generate_content.call_count == 1
    assert "https://valid1.example.com [検証: valid]" in result
    assert "https://invalid.example.com" not in result
    assert "[無効URL除去]" in result


def test_validate_url_with_http_check_detects_certificate_expired() -> None:
    """validate_urlツールが証明書期限切れを識別できること。"""
    gemini_client, _ = _build_client_and_async_client()

    with patch("app.infrastructure.ai.gemini_client.urlopen", side_effect=URLError("certificate has expired")):
        result = gemini_client._validate_url_with_http_check_sync(  # noqa: SLF001
            "https://www.city.utsunomiya.tochigi.jp/kanko/kankou/spot/shizen/1007109.html"
        )

    assert result["verdict"] == "invalid"
    assert result["tls_valid"] is False
    assert result["tls_error"] == "certificate_expired"


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
    mock_response.text = "検索結果を含む生成テキスト https://www.chusonji.or.jp/"
    mock_response.candidates = [candidate]

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    with patch.object(
        gemini_client,
        "_validate_url_with_http_check",
        new=AsyncMock(return_value={"url": "https://www.chusonji.or.jp/", "verdict": "valid", "reason": "ok"}),
    ):
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
    mock_response.text = "検索結果を含む生成テキスト https://example.com/source"
    mock_response.candidates = []

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(return_value=mock_response)

    with patch.object(
        gemini_client,
        "_validate_url_with_http_check",
        new=AsyncMock(return_value={"url": "https://example.com/source", "verdict": "valid", "reason": "ok"}),
    ):
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
            max_retries=1,
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
async def test_max_retries_is_capped_to_five_when_ten_or_more_is_requested():
    """max_retriesが10以上の場合は5回に丸められること。"""
    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(
        side_effect=google_exceptions.ResourceExhausted("Quota exceeded")
    )

    with patch.object(gemini_client, "_exponential_backoff", new=AsyncMock()):
        with pytest.raises(AIServiceQuotaExceededError):
            await gemini_client.generate_content(
                prompt="テストプロンプト",
                max_retries=10,
            )

    assert mock_async_client.models.generate_content.call_count == 5


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


@pytest.mark.asyncio
async def test_generate_structured_data_retries_when_json_is_broken_then_succeeds():
    """構造化JSONが壊れて返っても再試行で復旧できること。"""
    invalid_response = MagicMock()
    invalid_response.text = '{"name":"富士山","type":"自然'
    invalid_response.parsed = None
    invalid_response.candidates = None

    expected_data = {"name": "富士山", "type": "自然"}
    valid_response = _build_response_with_text(json.dumps(expected_data))

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(
        side_effect=[invalid_response, valid_response]
    )

    with patch.object(gemini_client, "_exponential_backoff", new=AsyncMock()):
        result = await gemini_client.generate_content_with_schema(
            prompt="富士山の情報を返してください",
            response_schema=SimpleTestSchema,
            temperature=0.0,
            max_retries=2,
        )

    assert result == expected_data
    assert mock_async_client.models.generate_content.call_count == 2


@pytest.mark.asyncio
async def test_generate_structured_data_retry_uses_compaction_prompt() -> None:
    """構造化JSON再試行時に段階的な簡潔化指示を追加すること。"""
    invalid_response = MagicMock()
    invalid_response.text = '{"name":"富士山","type":"自然'
    invalid_response.parsed = None
    invalid_part = MagicMock()
    invalid_part.text = invalid_response.text
    invalid_content = MagicMock()
    invalid_content.parts = [invalid_part]
    invalid_candidate = MagicMock()
    invalid_candidate.finish_reason = "FinishReason.MAX_TOKENS"
    invalid_candidate.content = invalid_content
    invalid_response.candidates = [invalid_candidate]

    invalid_repair_response = MagicMock()
    invalid_repair_response.text = '{"name":"富士山","type":"自然'
    invalid_repair_response.parsed = None
    invalid_repair_response.candidates = None

    expected_data = {"name": "富士山", "type": "自然"}
    valid_response = _build_response_with_text(json.dumps(expected_data))

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(
        side_effect=[invalid_response, invalid_repair_response, valid_response]
    )

    with patch.object(gemini_client, "_exponential_backoff", new=AsyncMock()):
        result = await gemini_client.generate_content_with_schema(
            prompt="富士山の情報を返してください",
            response_schema=SimpleTestSchema,
            temperature=0.0,
            max_retries=3,
        )

    assert result == expected_data
    assert mock_async_client.models.generate_content.call_count == 3
    first_call_contents = mock_async_client.models.generate_content.await_args_list[0].kwargs["contents"]
    second_call_contents = mock_async_client.models.generate_content.await_args_list[1].kwargs["contents"]
    third_call_contents = mock_async_client.models.generate_content.await_args_list[2].kwargs["contents"]
    assert "<retry_compaction_instructions>" not in first_call_contents
    assert "<broken_json>" in second_call_contents
    assert "<retry_compaction_instructions>" in third_call_contents
    assert "目標文字量: 前回の85%程度まで削減する。" in third_call_contents



def test_build_response_text_diagnostics_includes_block_reason_and_part_counts():
    """text抽出診断にblock_reasonとparts内訳が含まれること。"""
    gemini_client, _ = _build_client_and_async_client()

    text_part = MagicMock()
    text_part.text = "候補テキスト"
    text_part.function_call = None

    function_part = MagicMock()
    function_part.text = None
    function_part.function_call = MagicMock()

    other_part = MagicMock()
    other_part.text = None
    other_part.function_call = None

    content = MagicMock()
    content.parts = [text_part, function_part, other_part]

    candidate = MagicMock()
    candidate.finish_reason = "SAFETY"
    candidate.content = content

    prompt_feedback = MagicMock()
    prompt_feedback.block_reason = "SAFETY"

    response = MagicMock()
    response.text = ""
    response.candidates = [candidate]
    response.prompt_feedback = prompt_feedback

    diagnostics = gemini_client._build_response_text_diagnostics(response)  # noqa: SLF001

    assert diagnostics["candidate_count"] == 1
    assert diagnostics["finish_reasons"] == ["SAFETY"]
    assert diagnostics["prompt_feedback_block_reason"] == "SAFETY"
    assert diagnostics["text_part_count"] == 1
    assert diagnostics["function_call_part_count"] == 1
    assert diagnostics["other_part_count"] == 1


@pytest.mark.asyncio
async def test_generate_with_search_retries_when_response_text_is_empty_then_succeeds():
    """response textが空でも再試行で復旧できること。"""
    empty_response = MagicMock()
    empty_response.text = ""
    empty_response.candidates = []

    success_response = _build_response_with_text("再試行後の抽出結果 https://example.com/source")

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(
        side_effect=[empty_response, success_response]
    )

    with (
        patch("app.infrastructure.ai.gemini_client.asyncio.sleep", new=AsyncMock()),
        patch.object(
            gemini_client,
            "_validate_url_with_http_check",
            new=AsyncMock(return_value={"url": "https://example.com/source", "verdict": "valid", "reason": "ok"}),
        ),
    ):
        result = await gemini_client.generate_content(
            prompt="沖縄戦の史実を抽出してください",
            tools=["google_search"],
            max_retries=2,
        )

    assert result == "再試行後の抽出結果 https://example.com/source [検証: valid]"
    assert mock_async_client.models.generate_content.call_count == 2


@pytest.mark.asyncio
async def test_generate_with_search_resolves_validate_url_tool_call_in_multiple_rounds():
    """validate_urlのtool callが複数ラウンド発生しても解決できること。"""
    first_response = MagicMock()
    first_response.text = ""
    first_call = MagicMock()
    first_call.name = "validate_url"
    first_call.args = {"urls": ["https://example.com/source1"]}
    first_part = MagicMock()
    first_part.function_call = first_call
    first_content = MagicMock()
    first_content.parts = [first_part]
    first_candidate = MagicMock()
    first_candidate.content = first_content
    first_response.candidates = [first_candidate]

    second_response = MagicMock()
    second_response.text = ""
    second_call = MagicMock()
    second_call.name = "validate_url"
    second_call.args = {"urls": ["https://example.com/source2"]}
    second_part = MagicMock()
    second_part.function_call = second_call
    second_content = MagicMock()
    second_content.parts = [second_part]
    second_candidate = MagicMock()
    second_candidate.content = second_content
    second_response.candidates = [second_candidate]

    final_response = _build_response_with_text("最終抽出結果 https://example.com/source2")

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(
        side_effect=[first_response, second_response, final_response]
    )

    async def _validate(url: str, **_: object) -> dict[str, str]:
        return {"url": url, "verdict": "valid", "reason": "ok"}

    with patch.object(
        gemini_client,
        "_validate_url_with_http_check",
        new=AsyncMock(side_effect=_validate),
    ):
        result = await gemini_client.generate_content(
            prompt="出典候補を抽出してください",
            tools=["google_search", "validate_url"],
            temperature=0.0,
        )

    assert result == "最終抽出結果 https://example.com/source2 [検証: valid]"
    assert mock_async_client.models.generate_content.call_count == 3



def test_validate_url_with_http_check_marks_relevance_mismatch() -> None:
    """spot_nameと無関係なページはrelevance_mismatchでinvalidになること。"""
    gemini_client, _ = _build_client_and_async_client()

    fake_response = MagicMock()
    fake_response.getcode.return_value = 200
    fake_response.headers.get.return_value = "text/html; charset=utf-8"
    fake_response.geturl.return_value = "https://example.com/unrelated"
    fake_response.read.return_value = (
        "<html><head><title>文化財データベース</title></head>"
        "<body>登録情報の一覧ページです。</body></html>"
    ).encode()

    context_manager = MagicMock()
    context_manager.__enter__.return_value = fake_response
    context_manager.__exit__.return_value = None

    with patch("app.infrastructure.ai.gemini_client.urlopen", return_value=context_manager):
        result = gemini_client._validate_url_with_http_check_sync(  # noqa: SLF001
            "https://example.com/unrelated",
            spot_name="高千穂峡",
            claim="柱状節理の渓谷",
        )

    assert result["verdict"] == "invalid"
    assert result["reason"] == "relevance_mismatch"


@pytest.mark.asyncio
async def test_generate_with_search_validate_url_accepts_structured_entries():
    """validate_urlの引数が {url, spotName, claim} 形式でも検証処理へ渡せること。"""
    first_response = MagicMock()
    first_response.text = ""
    function_call = MagicMock()
    function_call.name = "validate_url"
    function_call.args = {
        "urls": [
            {
                "url": "https://example.com/source",
                "spotName": "高千穂峡",
                "claim": "柱状節理の渓谷",
            }
        ]
    }
    part = MagicMock()
    part.function_call = function_call
    content = MagicMock()
    content.parts = [part]
    candidate = MagicMock()
    candidate.content = content
    first_response.candidates = [candidate]

    second_response = _build_response_with_text("https://example.com/source を使用した抽出結果")

    gemini_client, mock_async_client = _build_client_and_async_client()
    mock_async_client.models.generate_content = AsyncMock(
        side_effect=[first_response, second_response]
    )

    validate_mock = AsyncMock(return_value={"url": "https://example.com/source", "verdict": "valid", "reason": "ok"})
    with patch.object(gemini_client, "_validate_url_with_http_check", new=validate_mock):
        result = await gemini_client.generate_content(
            prompt="出典候補を抽出してください",
            tools=["google_search", "validate_url"],
            temperature=0.0,
        )

    assert result == "https://example.com/source [検証: valid] を使用した抽出結果"
    validate_mock.assert_awaited()
    call = validate_mock.await_args
    assert call.args[0] == "https://example.com/source"
