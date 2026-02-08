"""Vertex AI Gemini APIクライアント実装"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import ssl
import time
from typing import TYPE_CHECKING, Any, TypeVar, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from google import genai
from google.api_core import exceptions as google_exceptions
from google.genai import errors as genai_errors
from google.genai import types

from app.infrastructure.ai.exceptions import (
    AIServiceConnectionError,
    AIServiceInvalidRequestError,
    AIServiceQuotaExceededError,
)

if TYPE_CHECKING:
    from app.infrastructure.ai.schemas.base import GeminiResponseSchema

T = TypeVar("T", bound="GeminiResponseSchema")
_URL_TOOL_TIMEOUT_SECONDS = 10


class GeminiClient:
    """Vertex AI Gemini APIクライアント

    テキスト生成、画像分析、構造化出力などの機能を提供する
    """

    def __init__(
        self,
        project_id: str,
        location: str = "asia-northeast1",
        model_name: str = "gemini-2.5-flash",
    ) -> None:
        """GeminiClientを初期化する

        Args:
            project_id: Google CloudプロジェクトID
            location: Vertex AIのロケーション（デフォルト: asia-northeast1）
            model_name: 使用するモデル名（デフォルト: gemini-2.5-flash）
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        # Vertex AI用のGoogle Gen AI SDKクライアント
        self._client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
            http_options=types.HttpOptions(api_version="v1"),
        ).aio
        self._logger = logging.getLogger(__name__)

    async def generate_content(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        tools: list[str] | None = None,
        temperature: float = 0.7,
        max_output_tokens: int = 8192,
        images: list[str] | None = None,
        model_name_override: str | None = None,
        timeout: int = 60,
        max_retries: int = 3,
    ) -> str:
        """基本的なコンテンツ生成を行う

        Args:
            prompt: 生成プロンプト
            system_instruction: システム命令（オプション）
            tools: 使用するツールのリスト（例: ["google_search"]）
            temperature: 生成の多様性を制御するパラメータ（0.0-2.0）
            max_output_tokens: 最大出力トークン数
            images: 画像URIのリスト（オプション）
            timeout: タイムアウト秒数
            max_retries: 最大リトライ回数

        Returns:
            str: 生成されたテキスト

        Raises:
            AIServiceConnectionError: 接続エラー
            AIServiceQuotaExceededError: クォータ超過エラー
            AIServiceInvalidRequestError: 不正リクエストエラー
        """
        # ツールの設定
        model_tools = self._prepare_tools(tools) if tools else None

        # GenerateContentConfigの作成
        generation_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            tools=model_tools,
        )

        # コンテンツの準備
        contents = self._prepare_contents(prompt, images)

        # リトライ付きで生成を実行
        for attempt in range(max_retries):
            attempt_start = time.perf_counter()
            try:
                first_call_start = time.perf_counter()
                selected_model_name = model_name_override or self.model_name
                response = await asyncio.wait_for(
                    self._client.models.generate_content(
                        model=selected_model_name,
                        contents=contents,  # type: ignore[arg-type]
                        config=generation_config,
                    ),
                    timeout=timeout,
                )
                first_call_sec = time.perf_counter() - first_call_start
                tool_resolution_start = time.perf_counter()
                response = await self._resolve_validate_url_tool_calls(
                    response=response,
                    tools=tools,
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    images=images,
                    model_name_override=model_name_override,
                    timeout=timeout,
                )
                tool_resolution_sec = time.perf_counter() - tool_resolution_start
                attempt_sec = time.perf_counter() - attempt_start
                self._logger.info(
                    "StepA timing: attempt=%d/%d first_call_sec=%.3f tool_resolution_sec=%.3f attempt_total_sec=%.3f",
                    attempt + 1,
                    max_retries,
                    first_call_sec,
                    tool_resolution_sec,
                    attempt_sec,
                )
                if tools and "google_search" in tools:
                    search_diagnostics = self._build_search_tool_diagnostics(response)
                    self._logger.info(
                        "Google Search tool diagnostics: %s",
                        search_diagnostics,
                    )
                    if (
                        search_diagnostics["grounded_candidate_count"] == 0
                        and search_diagnostics["google_search_function_call_count"] == 0
                    ):
                        self._logger.warning(
                            "Google Search was requested but no grounding/function-call evidence was found."
                        )
                return self._extract_text(response)

            except TimeoutError as e:
                self._logger.warning(
                    "StepA timeout: attempt=%d/%d elapsed_sec=%.3f",
                    attempt + 1,
                    max_retries,
                    time.perf_counter() - attempt_start,
                )
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Request timeout: {e}") from e
                await self._exponential_backoff(attempt)

            except google_exceptions.ResourceExhausted as e:
                # クォータ超過エラー（429）
                self._logger.warning(
                    "StepA quota exhausted: attempt=%d/%d elapsed_sec=%.3f",
                    attempt + 1,
                    max_retries,
                    time.perf_counter() - attempt_start,
                )
                if attempt == max_retries - 1:
                    raise AIServiceQuotaExceededError(f"API quota exceeded: {e}") from e
                # 指数バックオフでリトライ
                await self._exponential_backoff(attempt)

            except google_exceptions.DeadlineExceeded as e:
                # タイムアウトエラー
                self._logger.warning(
                    "StepA deadline exceeded: attempt=%d/%d elapsed_sec=%.3f",
                    attempt + 1,
                    max_retries,
                    time.perf_counter() - attempt_start,
                )
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Request timeout: {e}") from e
                await self._exponential_backoff(attempt)

            except google_exceptions.ServiceUnavailable as e:
                # サービス利用不可エラー（500系）
                self._logger.warning(
                    "StepA service unavailable: attempt=%d/%d elapsed_sec=%.3f",
                    attempt + 1,
                    max_retries,
                    time.perf_counter() - attempt_start,
                )
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Service unavailable: {e}") from e
                await self._exponential_backoff(attempt)

            except google_exceptions.InvalidArgument as e:
                # 不正な引数エラー（400）- リトライしない
                self._logger.warning(
                    "StepA invalid argument: attempt=%d/%d elapsed_sec=%.3f",
                    attempt + 1,
                    max_retries,
                    time.perf_counter() - attempt_start,
                )
                raise AIServiceInvalidRequestError(f"Invalid request: {e}") from e

            except genai_errors.ClientError as e:
                self._logger.warning(
                    "StepA client error: attempt=%d/%d elapsed_sec=%.3f code=%s status=%s",
                    attempt + 1,
                    max_retries,
                    time.perf_counter() - attempt_start,
                    getattr(e, "code", None),
                    getattr(e, "status", None),
                )
                if self._is_rate_limit_error(e):
                    if attempt == max_retries - 1:
                        raise AIServiceQuotaExceededError(f"API quota exceeded: {e}") from e
                    await self._exponential_backoff(attempt)
                    continue
                raise AIServiceInvalidRequestError(f"Invalid request: {e}") from e

            except genai_errors.ServerError as e:
                self._logger.warning(
                    "StepA server error: attempt=%d/%d elapsed_sec=%.3f",
                    attempt + 1,
                    max_retries,
                    time.perf_counter() - attempt_start,
                )
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Service unavailable: {e}") from e
                await self._exponential_backoff(attempt)

            except google_exceptions.GoogleAPIError as e:
                # その他のGoogleAPIエラー
                self._logger.warning(
                    "StepA google api error: attempt=%d/%d elapsed_sec=%.3f",
                    attempt + 1,
                    max_retries,
                    time.perf_counter() - attempt_start,
                )
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Google API error: {e}") from e
                await self._exponential_backoff(attempt)

        # ここには到達しないはずだが、念のため
        raise AIServiceConnectionError("Max retries exceeded")

    async def generate_content_with_schema(
        self,
        prompt: str,
        response_schema: type[T],
        *,
        system_instruction: str | None = None,
        tools: list[str] | None = None,
        temperature: float = 0.0,
        max_output_tokens: int = 8192,
        images: list[str] | None = None,
        timeout: int = 60,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """JSON構造化データを生成する

        Args:
            prompt: 生成プロンプト
            response_schema: PydanticスキーマクラスのType（GeminiResponseSchemaのサブクラス）
            system_instruction: システム命令（オプション）
            tools: 使用するツールのリスト（構造化出力では未対応）
            temperature: 生成の多様性を制御するパラメータ（構造化出力時は0推奨）
            max_output_tokens: 最大出力トークン数
            images: 画像URIのリスト（オプション）
            timeout: タイムアウト秒数
            max_retries: 最大リトライ回数

        Returns:
            dict[str, Any]: スキーマに従った構造化データ（dict形式）

        Raises:
            AIServiceConnectionError: 接続エラー
            AIServiceQuotaExceededError: クォータ超過エラー
            AIServiceInvalidRequestError: 不正リクエストエラー
        """
        if tools:
            raise AIServiceInvalidRequestError("Tools are not supported for structured output.")

        # PydanticモデルからJSON Schemaを生成
        json_schema = response_schema.model_json_schema(mode="serialization")

        # GenerateContentConfigの作成（JSON出力モード）
        generation_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json",
            response_json_schema=json_schema,
        )

        contents = self._prepare_contents(prompt, images)

        # リトライ付きで生成を実行
        for attempt in range(max_retries):
            try:
                response = await asyncio.wait_for(
                    self._client.models.generate_content(
                        model=self.model_name,
                        contents=contents,  # type: ignore[arg-type]
                        config=generation_config,
                    ),
                    timeout=timeout,
                )
                return self._extract_structured_data(response)

            except TimeoutError as e:
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Request timeout: {e}") from e
                await self._exponential_backoff(attempt)

            except google_exceptions.ResourceExhausted as e:
                if attempt == max_retries - 1:
                    raise AIServiceQuotaExceededError(f"API quota exceeded: {e}") from e
                await self._exponential_backoff(attempt)

            except google_exceptions.DeadlineExceeded as e:
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Request timeout: {e}") from e
                await self._exponential_backoff(attempt)

            except google_exceptions.ServiceUnavailable as e:
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Service unavailable: {e}") from e
                await self._exponential_backoff(attempt)

            except google_exceptions.InvalidArgument as e:
                raise AIServiceInvalidRequestError(f"Invalid request: {e}") from e

            except genai_errors.ClientError as e:
                if self._is_rate_limit_error(e):
                    if attempt == max_retries - 1:
                        raise AIServiceQuotaExceededError(f"API quota exceeded: {e}") from e
                    await self._exponential_backoff(attempt)
                    continue
                raise AIServiceInvalidRequestError(f"Invalid request: {e}") from e

            except genai_errors.ServerError as e:
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Service unavailable: {e}") from e
                await self._exponential_backoff(attempt)

            except google_exceptions.GoogleAPIError as e:
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Google API error: {e}") from e
                await self._exponential_backoff(attempt)

        raise AIServiceConnectionError("Max retries exceeded")

    def _prepare_tools(self, tool_names: list[str]) -> list[types.Tool]:
        """ツールを準備する

        Args:
            tool_names: ツール名のリスト

        Returns:
            list[types.Tool]: ツールオブジェクトのリスト
        """
        tools = []
        for tool_name in tool_names:
            if tool_name == "google_search":
                tools.append(types.Tool(google_search=types.GoogleSearch()))
                continue
            if tool_name == "validate_url":
                tools.append(
                    types.Tool(
                        function_declarations=[
                            types.FunctionDeclaration(
                                name="validate_url",
                                description=(
                                    "URLの到達性と有効性を検証します。"
                                    "404、ソフト404、期限付きリンク等を検出します。"
                                ),
                                parameters=cast(
                                    Any,
                                    {
                                        "type": "object",
                                        "properties": {
                                            "urls": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                                "description": "検証対象URLの配列",
                                            }
                                        },
                                        "required": ["urls"],
                                    },
                                ),
                            )
                        ]
                    )
                )
                continue
            raise AIServiceInvalidRequestError(f"Unsupported tool name: {tool_name}")
        return tools

    def _prepare_contents(
        self,
        prompt: str,
        images: list[str] | None = None,
    ) -> list[types.Part] | str:
        """コンテンツを準備する

        Args:
            prompt: テキストプロンプト
            images: 画像URIのリスト（オプション）

        Returns:
            list[types.Part] | str: コンテンツ（画像がある場合はPartのリスト、ない場合は文字列）
        """
        if not images:
            return prompt

        # 画像がある場合はPartのリストとして構築
        parts = []
        for image_uri in images:
            parts.append(types.Part.from_uri(file_uri=image_uri, mime_type="image/jpeg"))
        parts.append(types.Part.from_text(text=prompt))
        return parts

    async def _resolve_validate_url_tool_calls(
        self,
        *,
        response: Any,
        tools: list[str] | None,
        prompt: str,
        system_instruction: str | None,
        temperature: float,
        max_output_tokens: int,
        images: list[str] | None,
        model_name_override: str | None,
        timeout: int,
    ) -> Any:
        """validate_urlツール呼び出しがあれば実行結果を反映して再生成する。"""
        if not tools or "validate_url" not in tools:
            return response

        function_calls = self._extract_named_function_calls(response, "validate_url")
        if not function_calls:
            return response
        self._logger.info(
            "validate_url tool calls detected: count=%d",
            len(function_calls),
        )

        urls_to_validate: list[str] = []
        for call_args in function_calls:
            urls = call_args.get("urls")
            if not isinstance(urls, list):
                continue
            for url in urls:
                if isinstance(url, str) and url.strip():
                    urls_to_validate.append(url.strip())

        # ツール誤動作時の暴走防止
        unique_urls = list(dict.fromkeys(urls_to_validate))[:20]
        if not unique_urls:
            return response

        validation_results = []
        validate_start = time.perf_counter()
        for url in unique_urls:
            validation_results.append(await self._validate_url_with_http_check(url))
        validate_sec = time.perf_counter() - validate_start

        validation_text = self._format_validate_url_results(validation_results)
        self._logger.info(
            "validate_url tool execution finished: checked=%d valid=%d invalid=%d validate_sec=%.3f",
            len(validation_results),
            len([item for item in validation_results if item.get("verdict") == "valid"]),
            len([item for item in validation_results if item.get("verdict") != "valid"]),
            validate_sec,
        )
        augmented_prompt = (
            f"{prompt}\n\n"
            "<url_validation_results>\n"
            f"{validation_text}\n"
            "</url_validation_results>\n\n"
            "上記で invalid と判定されたURLは出典として採用しないでください。"
        )
        followup_tools = [tool for tool in tools if tool != "validate_url"]
        followup_model_tools = self._prepare_tools(followup_tools) if followup_tools else None
        followup_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            tools=followup_model_tools,
        )
        followup_contents = self._prepare_contents(augmented_prompt, images)
        second_call_start = time.perf_counter()
        followup_response = await asyncio.wait_for(
            self._client.models.generate_content(
                model=model_name_override or self.model_name,
                contents=followup_contents,  # type: ignore[arg-type]
                config=followup_config,
            ),
            timeout=timeout,
        )
        self._logger.info(
            "validate_url followup generation finished: second_call_sec=%.3f",
            time.perf_counter() - second_call_start,
        )
        return followup_response

    def _extract_named_function_calls(
        self, response: Any, function_name: str
    ) -> list[dict[str, Any]]:
        """レスポンスから指定名のFunction Call引数を抽出する。"""
        calls: list[dict[str, Any]] = []
        candidates = getattr(response, "candidates", None)
        if not candidates:
            return calls

        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None)
            if not parts:
                continue
            for part in parts:
                function_call = getattr(part, "function_call", None)
                if function_call is None:
                    continue
                name = getattr(function_call, "name", None)
                if name != function_name:
                    continue
                args = getattr(function_call, "args", None)
                if isinstance(args, dict):
                    calls.append(args)
                    continue
                if isinstance(args, str):
                    try:
                        parsed = json.loads(args)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(parsed, dict):
                        calls.append(parsed)
        return calls

    async def _validate_url_with_http_check(self, url: str) -> dict[str, Any]:
        """URL検証ツールの実処理。"""
        return await asyncio.to_thread(self._validate_url_with_http_check_sync, url)

    def _validate_url_with_http_check_sync(self, url: str) -> dict[str, Any]:
        """URL検証ツールの同期処理。"""
        parsed = urlparse(url)
        if parsed.scheme.lower() != "https":
            return {
                "url": url,
                "verdict": "invalid",
                "reason": "non_https",
                "tls_valid": False,
                "tls_error": "non_https_scheme",
            }
        if any(
            token in parsed.query.lower()
            for token in ("x-goog-expires", "x-amz-expires", "x-goog-signature", "token=")
        ):
            return {
                "url": url,
                "verdict": "invalid",
                "reason": "possibly_expiring",
                "tls_valid": None,
                "tls_error": None,
            }

        try:
            request = Request(
                url,
                headers={"User-Agent": "HistoricalTravelAgent/1.0 (validate_url tool)"},
                method="GET",
            )
            with urlopen(request, timeout=_URL_TOOL_TIMEOUT_SECONDS) as response:  # noqa: S310
                status_code = response.getcode()
                content_type = response.headers.get("Content-Type", "")
                final_url = response.geturl()
                body = response.read(65536).decode("utf-8", errors="ignore")
                if status_code < 200 or status_code >= 300:
                    return {
                        "url": url,
                        "verdict": "invalid",
                        "reason": f"http_status_{status_code}",
                        "final_url": final_url,
                        "tls_valid": True,
                        "tls_error": None,
                    }
                if "text/html" in content_type.lower() and self._is_soft_404_html(body, final_url):
                    return {
                        "url": url,
                        "verdict": "invalid",
                        "reason": "soft_404",
                        "final_url": final_url,
                        "tls_valid": True,
                        "tls_error": None,
                    }
                return {
                    "url": url,
                    "verdict": "valid",
                    "reason": "ok",
                    "final_url": final_url,
                    "tls_valid": True,
                    "tls_error": None,
                }
        except HTTPError as exc:
            return {
                "url": url,
                "verdict": "invalid",
                "reason": f"http_error_{exc.code}",
                "tls_valid": True,
                "tls_error": None,
            }
        except (URLError, TimeoutError, ValueError, ssl.SSLError) as exc:
            tls_error = self._extract_tls_error_code(exc)
            return {
                "url": url,
                "verdict": "invalid",
                "reason": f"network_error_{type(exc).__name__}",
                "tls_valid": False if tls_error else None,
                "tls_error": tls_error,
            }

    def _extract_tls_error_code(self, exc: BaseException) -> str | None:
        """例外からTLSエラー種別を抽出する。"""
        if isinstance(exc, ssl.SSLError):
            detail = str(exc).lower()
        elif isinstance(exc, URLError):
            detail = str(exc.reason).lower()
        else:
            detail = str(exc).lower()

        if "certificate has expired" in detail or "certificate expired" in detail:
            return "certificate_expired"
        if "certificate verify failed" in detail:
            return "certificate_verify_failed"
        if "self signed certificate" in detail:
            return "self_signed_certificate"
        if "hostname" in detail and "mismatch" in detail:
            return "hostname_mismatch"
        return None

    def _is_soft_404_html(self, html: str, final_url: str) -> bool:
        lowered = html.lower()
        final_url_lower = final_url.lower()
        if any(token in final_url_lower for token in ("/404", "404.html", "kanko404")):
            return True
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).lower() if title_match else ""
        return any(
            token in title or token in lowered
            for token in ("not found", "見つかりません", "お探しのページ", "統合しました")
        )

    def _format_validate_url_results(self, validation_results: list[dict[str, Any]]) -> str:
        lines = []
        for result in validation_results:
            lines.append(
                "- url: {url} | verdict: {verdict} | reason: {reason} | tls_valid: {tls_valid} | tls_error: {tls_error}".format(
                    url=result.get("url"),
                    verdict=result.get("verdict"),
                    reason=result.get("reason"),
                    tls_valid=result.get("tls_valid"),
                    tls_error=result.get("tls_error"),
                )
            )
        return "\n".join(lines)

    def _extract_text(self, response: Any) -> str:
        """レスポンスからテキストを取り出す

        Args:
            response: Gemini APIからのレスポンスオブジェクト

        Returns:
            str: 抽出されたテキスト

        Raises:
            AIServiceInvalidRequestError: text属性が存在しない、または空の場合
        """
        text = getattr(response, "text", None)
        if isinstance(text, str) and text.strip():
            return text

        candidate_text = self._extract_first_candidate_text(response)
        diagnostics = self._build_response_text_diagnostics(response)
        if candidate_text is not None:
            self._logger.warning(
                "Gemini response.text is empty; falling back to candidates.parts.text. diagnostics=%s",
                diagnostics,
            )
            return candidate_text

        self._logger.error(
            "Gemini response text is empty and no fallback text found. diagnostics=%s",
            diagnostics,
        )
        raise AIServiceInvalidRequestError("Response text is empty.")

    def _extract_first_candidate_text(self, response: Any) -> str | None:
        """レスポンス候補から最初の有効なtextを取得する。"""
        candidates = getattr(response, "candidates", None)
        if not candidates:
            return None

        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None)
            if not parts:
                continue
            for part in parts:
                part_text = getattr(part, "text", None)
                if isinstance(part_text, str) and part_text.strip():
                    return part_text
        return None

    def _build_response_text_diagnostics(self, response: Any) -> dict[str, Any]:
        """text抽出失敗時の診断情報を構築する。"""
        text = getattr(response, "text", None)
        text_length = len(text) if isinstance(text, str) else None

        candidate_count = 0
        candidate_text_lengths: list[int] = []
        finish_reasons: list[str] = []
        candidates = getattr(response, "candidates", None)
        if candidates:
            candidate_count = len(candidates)
            for candidate in candidates:
                finish_reason = getattr(candidate, "finish_reason", None)
                if finish_reason is not None:
                    finish_reasons.append(str(finish_reason))

                content = getattr(candidate, "content", None)
                parts = getattr(content, "parts", None)
                if not parts:
                    continue
                for part in parts:
                    part_text = getattr(part, "text", None)
                    if isinstance(part_text, str):
                        candidate_text_lengths.append(len(part_text))

        prompt_feedback = getattr(response, "prompt_feedback", None)
        return {
            "text_length": text_length,
            "candidate_count": candidate_count,
            "candidate_text_lengths": candidate_text_lengths[:10],
            "finish_reasons": finish_reasons[:10],
            "has_prompt_feedback": prompt_feedback is not None,
        }

    def _build_search_tool_diagnostics(self, response: Any) -> dict[str, Any]:
        """Google Searchツール利用の診断情報を構築する。"""

        def _field(obj: Any, key: str) -> Any:
            if obj is None:
                return None
            if isinstance(obj, dict):
                return obj.get(key)
            return getattr(obj, key, None)

        def _as_list(value: Any) -> list[Any]:
            if isinstance(value, (list, tuple)):
                return list(value)
            return []

        candidates = _as_list(_field(response, "candidates"))
        grounded_candidate_count = 0
        grounding_chunk_count = 0
        web_search_query_count = 0
        google_search_function_call_count = 0
        grounded_uris: list[str] = []

        for candidate in candidates:
            grounding_metadata = _field(candidate, "grounding_metadata")
            if grounding_metadata is not None:
                grounded_candidate_count += 1

                grounding_chunks = _as_list(_field(grounding_metadata, "grounding_chunks"))
                grounding_chunk_count += len(grounding_chunks)

                for chunk in grounding_chunks:
                    web = _field(chunk, "web")
                    uri = _field(web, "uri")
                    if isinstance(uri, str) and uri.strip():
                        grounded_uris.append(uri.strip())

                web_search_queries = _as_list(_field(grounding_metadata, "web_search_queries"))
                web_search_query_count += len(web_search_queries)

            content = _field(candidate, "content")
            parts = _as_list(_field(content, "parts"))
            for part in parts:
                function_call = _field(part, "function_call")
                name = _field(function_call, "name")
                if name == "google_search":
                    google_search_function_call_count += 1

        return {
            "candidate_count": len(candidates),
            "grounded_candidate_count": grounded_candidate_count,
            "grounding_chunk_count": grounding_chunk_count,
            "web_search_query_count": web_search_query_count,
            "google_search_function_call_count": google_search_function_call_count,
            "grounded_uri_samples": grounded_uris[:5],
        }

    def _extract_structured_data(self, response: Any) -> dict[str, Any]:
        """構造化レスポンスをdictとして抽出する.

        Structured outputでは response.text が空でも response.parsed が埋まることがあるため、
        parsed を優先し、次に text / candidates から復元する。
        """
        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, dict):
            return parsed
        if parsed is not None and hasattr(parsed, "model_dump"):
            dumped = parsed.model_dump()
            if isinstance(dumped, dict):
                return dumped

        parse_errors: list[str] = []

        # 互換性のため text を利用
        text = getattr(response, "text", None)
        if isinstance(text, str) and text.strip():
            try:
                return self._parse_json_object(text, source="response.text")
            except AIServiceInvalidRequestError as e:
                parse_errors.append(str(e))

        # textが空の場合、candidates.parts.text をフォールバックで走査
        candidates = getattr(response, "candidates", None)
        if candidates:
            for candidate in candidates:
                content = getattr(candidate, "content", None)
                parts = getattr(content, "parts", None)
                if not parts:
                    continue
                for part in parts:
                    part_text = getattr(part, "text", None)
                    if isinstance(part_text, str) and part_text.strip():
                        try:
                            return self._parse_json_object(
                                part_text,
                                source="response.candidates[].content.parts[].text",
                            )
                        except AIServiceInvalidRequestError as e:
                            parse_errors.append(str(e))

        if parse_errors:
            raise AIServiceInvalidRequestError("; ".join(parse_errors))
        raise AIServiceInvalidRequestError("Response structured payload is empty.")

    def _parse_json_object(self, payload: str, *, source: str) -> dict[str, Any]:
        """JSON文字列をdictへパースする."""
        try:
            loaded = json.loads(payload)
        except json.JSONDecodeError as e:
            raise AIServiceInvalidRequestError(
                f"Structured response JSON is invalid in {source}: {e.msg} (line {e.lineno}, column {e.colno})."
            ) from e

        if not isinstance(loaded, dict):
            raise AIServiceInvalidRequestError(
                f"Structured response JSON must be an object in {source}."
            )
        return loaded

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """レート制限やクォータ超過のエラーか判定する"""
        if not isinstance(error, genai_errors.APIError):
            return False
        return bool(error.code == 429 or error.status == "RESOURCE_EXHAUSTED")

    async def _exponential_backoff(self, attempt: int) -> None:
        """指数バックオフを実行する

        Args:
            attempt: 現在の試行回数（0から開始）
        """
        wait_time = min(2**attempt, 8)  # 最大8秒
        await asyncio.sleep(wait_time)
