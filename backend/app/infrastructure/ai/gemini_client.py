"""Vertex AI Gemini APIクライアント実装"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import ssl
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

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
_MAX_VALIDATE_URL_TOOL_LOOPS = 3
_MIN_VALID_URLS_FOR_EARLY_ACCEPT = 5
_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_DIAGNOSTIC_SNAPSHOT_DIR = _BACKEND_ROOT / "logs" / "ai_failures"
_STEPA_BLOCKED_SOURCE_HOSTS = ("vertexaisearch.cloud.google.com",)


class GeminiClient:
    """Vertex AI Gemini APIクライアント

    テキスト生成、画像分析、構造化出力などの機能を提供する
    """

    def __init__(
        self,
        project_id: str,
        location: str = "global",
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

    def _normalize_max_retries(self, max_retries: int) -> int:
        """最大リトライ回数を運用ルールに合わせて正規化する。"""
        if max_retries <= 0:
            raise AIServiceInvalidRequestError("max_retries must be greater than 0.")
        if max_retries >= 10:
            return 5
        return max_retries

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
        timeout: int = 90,
        max_retries: int = 10,
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
        max_retries = self._normalize_max_retries(max_retries)
        request_id = f"stepa-{uuid4().hex[:12]}"
        self._logger.info(
            "StepA generation started: request_id=%s model=%s max_retries=%d tools=%s",
            request_id,
            model_name_override or self.model_name,
            max_retries,
            tools,
        )

        requested_tools = list(tools) if tools else []
        original_prompt = prompt
        previous_invalid_urls: tuple[str, ...] = ()
        cumulative_valid_urls: set[str] = set()
        retry_without_validate_url = False
        should_server_side_url_validation = "google_search" in requested_tools

        # リトライ付きで生成を実行
        for attempt in range(max_retries):
            attempt_tools = list(requested_tools)
            if retry_without_validate_url and "validate_url" in attempt_tools:
                attempt_tools = [
                    tool_name for tool_name in attempt_tools if tool_name != "validate_url"
                ]
                self._logger.info(
                    "StepA retry strategy activated: request_id=%s attempt=%d/%d removed_tool=validate_url remaining_tools=%s",
                    request_id,
                    attempt + 1,
                    max_retries,
                    attempt_tools,
                )

            model_tools = self._prepare_tools(attempt_tools) if attempt_tools else None
            generation_config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                tools=model_tools,
            )
            contents = self._prepare_contents(prompt, images)
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
                response, validate_url_call_count = await self._resolve_validate_url_tool_calls(
                    response=response,
                    tools=attempt_tools,
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
                if attempt_tools and "google_search" in attempt_tools:
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

                if should_server_side_url_validation:
                    try:
                        extracted_text = self._extract_text(
                            response,
                            request_id=request_id,
                            attempt=attempt + 1,
                            max_retries=max_retries,
                        )
                    except AIServiceInvalidRequestError as e:
                        if "Response text is empty." in str(e) and attempt < max_retries - 1:
                            self._logger.info(
                                "StepA empty text response detected before URL validation; retrying request_id=%s attempt=%d/%d",
                                request_id,
                                attempt + 1,
                                max_retries,
                            )
                            await asyncio.sleep(0.3 * (attempt + 1))
                            continue
                        raise

                    (
                        validated_text,
                        validation_summary,
                    ) = await self._validate_and_annotate_urls_in_text(
                        extracted_text,
                        trusted_valid_urls=cumulative_valid_urls,
                    )
                    for item in validation_summary.get("valid_details", []):
                        url = item.get("url")
                        if isinstance(url, str) and url:
                            cumulative_valid_urls.add(url)
                    cumulative_valid_count = len(cumulative_valid_urls)
                    self._logger.info(
                        "StepA server-side URL validation: request_id=%s attempt=%d/%d checked=%d valid=%d invalid=%d cumulative_valid=%d",
                        request_id,
                        attempt + 1,
                        max_retries,
                        validation_summary["checked"],
                        validation_summary["valid"],
                        validation_summary["invalid"],
                        cumulative_valid_count,
                    )
                    if validation_summary["checked"] == 0:
                        self._logger.warning(
                            "StepA server-side URL validation skipped: no URLs found in response. request_id=%s attempt=%d/%d",
                            request_id,
                            attempt + 1,
                            max_retries,
                        )
                        if attempt < max_retries - 1:
                            prompt = self._build_missing_url_feedback_prompt(
                                base_prompt=original_prompt,
                                previous_response_text=extracted_text,
                                feedback_round=attempt + 1,
                                reusable_valid_urls=tuple(sorted(cumulative_valid_urls)),
                            )
                            await asyncio.sleep(0.3 * (attempt + 1))
                            continue
                        self._logger.warning(
                            "StepA max retries reached with no URLs; proceeding with unvalidated text. request_id=%s attempt=%d/%d",
                            request_id,
                            attempt + 1,
                            max_retries,
                        )
                        return extracted_text

                    if validation_summary["invalid"] == 0:
                        return validated_text

                    if cumulative_valid_count >= _MIN_VALID_URLS_FOR_EARLY_ACCEPT:
                        self._logger.warning(
                            "StepA early accept activated: request_id=%s attempt=%d/%d valid=%d invalid=%d cumulative_valid=%d threshold=%d",
                            request_id,
                            attempt + 1,
                            max_retries,
                            validation_summary["valid"],
                            validation_summary["invalid"],
                            cumulative_valid_count,
                            _MIN_VALID_URLS_FOR_EARLY_ACCEPT,
                        )
                        return validated_text

                    if attempt < max_retries - 1:
                        current_invalid_urls = tuple(
                            sorted(
                                item.get("url")
                                for item in validation_summary.get("invalid_details", [])
                                if isinstance(item.get("url"), str) and item.get("url")
                            )
                        )
                        repeated_invalid_urls = (
                            bool(current_invalid_urls)
                            and current_invalid_urls == previous_invalid_urls
                        )
                        previous_invalid_urls = current_invalid_urls
                        prompt_summary = dict(validation_summary)
                        prompt_summary["valid_details"] = [
                            {"url": url} for url in sorted(cumulative_valid_urls)[:10]
                        ]
                        prompt_summary["valid"] = len(cumulative_valid_urls)
                        prompt = self._build_url_validation_feedback_prompt(
                            base_prompt=original_prompt,
                            previous_response_text=extracted_text,
                            validation_summary=prompt_summary,
                            feedback_round=attempt + 1,
                            repeated_invalid_urls=repeated_invalid_urls,
                        )
                        self._logger.warning(
                            "StepA server-side URL validation failed; retrying request_id=%s attempt=%d/%d invalid=%d",
                            request_id,
                            attempt + 1,
                            max_retries,
                            validation_summary["invalid"],
                        )
                        await asyncio.sleep(0.3 * (attempt + 1))
                        continue

                    self._logger.warning(
                        "StepA max retries reached with invalid URLs remaining; proceeding with sanitized text. request_id=%s attempt=%d/%d invalid=%d cumulative_valid=%d",
                        request_id,
                        attempt + 1,
                        max_retries,
                        validation_summary["invalid"],
                        cumulative_valid_count,
                    )
                    return validated_text

                response_diagnostics = self._build_response_text_diagnostics(response)
                predicted_reason_code = self._derive_empty_text_reason_code(response_diagnostics)
                self._logger.info(
                    "StepA response summary: request_id=%s attempt=%d/%d diagnostics=%s predicted_reason_code_if_empty=%s",
                    request_id,
                    attempt + 1,
                    max_retries,
                    response_diagnostics,
                    predicted_reason_code,
                )
                try:
                    return self._extract_text(
                        response,
                        request_id=request_id,
                        attempt=attempt + 1,
                        max_retries=max_retries,
                    )
                except AIServiceInvalidRequestError as e:
                    reason_code = self._extract_reason_code_from_error_message(str(e))
                    self._logger.warning(
                        "StepA text extraction failed: request_id=%s attempt=%d/%d model=%s tools=%s reason_code=%s error=%s diagnostics=%s",
                        request_id,
                        attempt + 1,
                        max_retries,
                        selected_model_name,
                        attempt_tools,
                        reason_code,
                        str(e),
                        response_diagnostics,
                    )
                    if "Response text is empty." in str(e) and attempt < max_retries - 1:
                        if reason_code == "EMPTY_TEXT_TOOL_CALL_ONLY":
                            retry_without_validate_url = True
                        self._logger.info(
                            "StepA empty text response detected; retrying request_id=%s attempt=%d/%d reason_code=%s",
                            request_id,
                            attempt + 1,
                            max_retries,
                            reason_code,
                        )
                        await asyncio.sleep(0.3 * (attempt + 1))
                        continue
                    raise

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
        timeout: int = 90,
        max_retries: int = 10,
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
        max_retries = self._normalize_max_retries(max_retries)

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

        parse_error_message: str | None = None
        parse_error_diagnostics: dict[str, Any] | None = None

        # リトライ付きで生成を実行
        for attempt in range(max_retries):
            compaction_ratio = self._calculate_structured_retry_compaction_ratio(attempt)
            retry_prompt = self._build_structured_retry_prompt(
                base_prompt=prompt,
                attempt=attempt,
                compaction_ratio=compaction_ratio,
                previous_error=parse_error_message,
                diagnostics=parse_error_diagnostics,
            )
            contents = self._prepare_contents(retry_prompt, images)
            try:
                response = await asyncio.wait_for(
                    self._client.models.generate_content(
                        model=self.model_name,
                        contents=contents,  # type: ignore[arg-type]
                        config=generation_config,
                    ),
                    timeout=timeout,
                )
                try:
                    return self._extract_structured_data(response)
                except AIServiceInvalidRequestError as e:
                    diagnostics = self._build_response_text_diagnostics(response)
                    repaired = await self._try_repair_structured_payload(
                        response=response,
                        response_schema=response_schema,
                        system_instruction=system_instruction,
                        timeout=timeout,
                    )
                    if repaired is not None:
                        self._logger.info(
                            "Structured response repaired successfully: attempt=%d/%d diagnostics=%s",
                            attempt + 1,
                            max_retries,
                            diagnostics,
                        )
                        return repaired

                    if attempt == max_retries - 1:
                        raise
                    parse_error_message = str(e)
                    parse_error_diagnostics = diagnostics
                    self._logger.warning(
                        "Structured response parsing failed: attempt=%d/%d; retrying. compaction_ratio=%d error=%s diagnostics=%s",
                        attempt + 1,
                        max_retries,
                        compaction_ratio,
                        str(e),
                        diagnostics,
                    )
                    await self._exponential_backoff(attempt)
                    continue

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

    def _calculate_structured_retry_compaction_ratio(self, attempt: int) -> int:
        """構造化出力リトライ時の目標文字量（前回比）を算出する。"""
        if attempt <= 0:
            return 100
        return max(40, 100 - attempt * 15)

    def _build_structured_retry_prompt(
        self,
        *,
        base_prompt: str,
        attempt: int,
        compaction_ratio: int,
        previous_error: str | None,
        diagnostics: dict[str, Any] | None,
    ) -> str:
        """構造化JSONの再試行時に、段階的な簡潔化指示を付与する。"""
        if attempt <= 0:
            return base_prompt

        finish_reasons = diagnostics.get("finish_reasons", []) if diagnostics else []
        max_tokens_hit = any("MAX_TOKENS" in str(value) for value in finish_reasons)

        failure_reason = (
            "前回は出力が長すぎてJSONが途中で切れました。"
            if max_tokens_hit
            else "前回はJSONが壊れていました。"
        )
        error_line = f"前回エラー: {previous_error}" if previous_error else "前回エラー: 不明。"

        return (
            f"{base_prompt}\n\n"
            "<retry_compaction_instructions>\n"
            f"再試行 {attempt} 回目。\n"
            f"{failure_reason}\n"
            f"{error_line}\n"
            f"目標文字量: 前回の{compaction_ratio}%程度まで削減する。\n"
            "必須スキーマを満たしたうえで、冗長な修飾や重複説明を削除する。\n"
            "配列要素数は、必須条件を満たす最小限を優先する。\n"
            "各文字列フィールドは短く簡潔にし、同じ事実の言い換えを繰り返さない。\n"
            "有効なJSONオブジェクトのみを返し、JSON以外の文は出力しない。\n"
            "</retry_compaction_instructions>"
        )

    def _prepare_tools(self, tool_names: list[str]) -> list[Any]:
        """ツールを準備する。validate_url は常に callable として渡す。"""
        tools: list[Any] = []
        for tool_name in tool_names:
            if tool_name == "google_search":
                tools.append(types.Tool(google_search=types.GoogleSearch()))
                continue
            if tool_name == "validate_url":
                # validate_url はモデルツールとしては渡さず、サーバ側で強制検証する
                continue
            raise AIServiceInvalidRequestError(f"Unsupported tool name: {tool_name}")

        self._logger.info(
            "StepA tool configuration: requested=%s prepared_types=%s server_side_validate_url=%s",
            tool_names,
            [type(tool).__name__ for tool in tools],
            "validate_url" in tool_names,
        )

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
    ) -> tuple[Any, int]:
        """validate_urlツール呼び出しがあれば実行結果を反映して再生成する。"""
        if not tools or "validate_url" not in tools:
            return response, 0

        current_response = response
        validation_round_texts: list[str] = []
        previous_call_signature: str | None = None
        validate_url_call_count = 0

        for round_index in range(_MAX_VALIDATE_URL_TOOL_LOOPS):
            function_calls = self._extract_named_function_calls(current_response, "validate_url")
            if not function_calls:
                return current_response, validate_url_call_count
            validate_url_call_count += len(function_calls)

            call_signature = self._build_validate_url_call_signature(function_calls)
            if previous_call_signature == call_signature:
                self._logger.warning(
                    "validate_url tool call signature repeated; forcing final text generation. round=%d/%d",
                    round_index + 1,
                    _MAX_VALIDATE_URL_TOOL_LOOPS,
                )
                finalized_response = await self._finalize_after_validate_url_resolution(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    images=images,
                    model_name_override=model_name_override,
                    timeout=timeout,
                    tools=tools,
                    validation_round_texts=validation_round_texts,
                    reason="repeated_signature",
                )
                return finalized_response, validate_url_call_count
            previous_call_signature = call_signature

            self._logger.info(
                "validate_url tool calls detected: round=%d/%d count=%d",
                round_index + 1,
                _MAX_VALIDATE_URL_TOOL_LOOPS,
                len(function_calls),
            )

            url_entries: list[dict[str, str | None]] = []
            for call_args in function_calls:
                urls = call_args.get("urls")
                if not isinstance(urls, list):
                    continue
                for item in urls:
                    if isinstance(item, str) and item.strip():
                        url_entries.append({"url": item.strip(), "spotName": None, "claim": None})
                        continue
                    if isinstance(item, dict):
                        raw_url = item.get("url")
                        if isinstance(raw_url, str) and raw_url.strip():
                            spot_name = item.get("spotName")
                            claim = item.get("claim")
                            url_entries.append(
                                {
                                    "url": raw_url.strip(),
                                    "spotName": spot_name.strip()
                                    if isinstance(spot_name, str) and spot_name.strip()
                                    else None,
                                    "claim": claim.strip()
                                    if isinstance(claim, str) and claim.strip()
                                    else None,
                                }
                            )

            unique_entries: list[dict[str, str | None]] = []
            seen_keys: set[str] = set()
            for entry in url_entries:
                dedupe_key = f"{entry['url']}|{entry['spotName'] or ''}|{entry['claim'] or ''}"
                if dedupe_key in seen_keys:
                    continue
                seen_keys.add(dedupe_key)
                unique_entries.append(entry)
                if len(unique_entries) >= 20:
                    break

            if not unique_entries:
                return current_response, validate_url_call_count

            validation_results = []
            validate_start = time.perf_counter()
            for entry in unique_entries:
                validation_results.append(
                    await self._validate_url_with_http_check(
                        entry["url"] or "",
                        spot_name=entry["spotName"],
                        claim=entry["claim"],
                    )
                )
            validate_sec = time.perf_counter() - validate_start

            valid_count = len(
                [item for item in validation_results if item.get("verdict") == "valid"]
            )
            invalid_count = len(validation_results) - valid_count
            validation_text = self._format_validate_url_results(validation_results)
            validation_round_texts.append(
                f'<round index="{round_index + 1}">\n{validation_text}\n</round>'
            )

            self._logger.info(
                "validate_url tool execution finished: round=%d/%d checked=%d valid=%d invalid=%d validate_sec=%.3f",
                round_index + 1,
                _MAX_VALIDATE_URL_TOOL_LOOPS,
                len(validation_results),
                valid_count,
                invalid_count,
                validate_sec,
            )

            augmented_prompt = (
                f"{prompt}\n\n"
                "<url_validation_results>\n"
                f"{'\n'.join(validation_round_texts)}\n"
                "</url_validation_results>\n\n"
                "上記で invalid と判定されたURLは出典として採用しないでください。"
                "出典が不足する場合は、追加で検索して validate_url を使って再検証してください。"
                "validate_url を呼ぶ際は、可能な限り {url, spotName, claim} 形式で指定してください。"
            )

            followup_model_tools = self._prepare_tools(tools)
            followup_config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                tools=followup_model_tools,
            )
            followup_contents = self._prepare_contents(augmented_prompt, images)

            followup_start = time.perf_counter()
            current_response = await asyncio.wait_for(
                self._client.models.generate_content(
                    model=model_name_override or self.model_name,
                    contents=followup_contents,  # type: ignore[arg-type]
                    config=followup_config,
                ),
                timeout=timeout,
            )
            self._logger.info(
                "validate_url followup generation finished: round=%d/%d followup_sec=%.3f",
                round_index + 1,
                _MAX_VALIDATE_URL_TOOL_LOOPS,
                time.perf_counter() - followup_start,
            )

        self._logger.warning(
            "validate_url resolution reached max rounds: max_rounds=%d",
            _MAX_VALIDATE_URL_TOOL_LOOPS,
        )
        finalized_response = await self._finalize_after_validate_url_resolution(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            images=images,
            model_name_override=model_name_override,
            timeout=timeout,
            tools=tools,
            validation_round_texts=validation_round_texts,
            reason="max_rounds_reached",
        )
        return finalized_response, validate_url_call_count

    def _build_validate_url_call_signature(self, function_calls: list[dict[str, Any]]) -> str:
        """validate_url呼び出し引数の重複判定用シグネチャを作成する。"""
        try:
            return json.dumps(function_calls, ensure_ascii=False, sort_keys=True)
        except TypeError:
            return repr(function_calls)

    async def _finalize_after_validate_url_resolution(
        self,
        *,
        prompt: str,
        system_instruction: str | None,
        temperature: float,
        max_output_tokens: int,
        images: list[str] | None,
        model_name_override: str | None,
        timeout: int,
        tools: list[str] | None,
        validation_round_texts: list[str],
        reason: str,
    ) -> Any:
        """validate_url解決後の最終本文生成を行う。"""
        final_tools = [tool_name for tool_name in (tools or []) if tool_name != "validate_url"]
        final_tools_for_log = final_tools if final_tools else None

        validation_text = "\n".join(validation_round_texts)
        final_prompt = (
            f"{prompt}\n\n"
            "<url_validation_results>\n"
            f"{validation_text}\n"
            "</url_validation_results>\n\n"
            "これは最終回答フェーズです。これ以上ツール呼び出しは行わず、本文テキストのみを返してください。"
            "可能な範囲で出典付きでまとめてください。"
        )

        final_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            tools=self._prepare_tools(final_tools) if final_tools else None,
        )
        final_contents = self._prepare_contents(final_prompt, images)

        finalize_start = time.perf_counter()
        finalized_response = await asyncio.wait_for(
            self._client.models.generate_content(
                model=model_name_override or self.model_name,
                contents=final_contents,  # type: ignore[arg-type]
                config=final_config,
            ),
            timeout=timeout,
        )
        self._logger.info(
            "validate_url finalization finished: reason=%s tools=%s elapsed_sec=%.3f",
            reason,
            final_tools_for_log,
            time.perf_counter() - finalize_start,
        )
        return finalized_response

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

    def _validate_url_tool_afc(self, urls: list[Any]) -> dict[str, Any]:
        """AFC向けvalidate_urlツール実装。"""
        start = time.perf_counter()
        if not isinstance(urls, list) or not urls:
            self._logger.warning(
                "validate_url AFC called with invalid args: urls_type=%s",
                type(urls).__name__,
            )
            return {
                "results": [],
                "summary": {"checked": 0, "valid": 0, "invalid": 0},
                "error": "urls must be a non-empty list.",
            }

        self._logger.info(
            "validate_url AFC invoked: raw_url_items=%d",
            len(urls),
        )

        entries: list[dict[str, str | None]] = []
        for item in urls:
            if isinstance(item, str) and item.strip():
                entries.append({"url": item.strip(), "spotName": None, "claim": None})
                continue
            if isinstance(item, dict):
                raw_url = item.get("url")
                if isinstance(raw_url, str) and raw_url.strip():
                    spot_name = item.get("spotName")
                    claim = item.get("claim")
                    entries.append(
                        {
                            "url": raw_url.strip(),
                            "spotName": spot_name.strip()
                            if isinstance(spot_name, str) and spot_name.strip()
                            else None,
                            "claim": claim.strip()
                            if isinstance(claim, str) and claim.strip()
                            else None,
                        }
                    )

        unique_entries: list[dict[str, str | None]] = []
        seen_keys: set[str] = set()
        for entry in entries:
            dedupe_key = f"{entry['url']}|{entry['spotName'] or ''}|{entry['claim'] or ''}"
            if dedupe_key in seen_keys:
                continue
            seen_keys.add(dedupe_key)
            unique_entries.append(entry)
            if len(unique_entries) >= 20:
                break

        results: list[dict[str, Any]] = []
        for entry in unique_entries:
            results.append(
                self._validate_url_with_http_check_sync(
                    entry["url"] or "",
                    spot_name=entry["spotName"],
                    claim=entry["claim"],
                )
            )

        valid_count = len([item for item in results if item.get("verdict") == "valid"])
        invalid_count = len(results) - valid_count
        self._logger.info(
            "validate_url AFC finished: parsed=%d checked=%d valid=%d invalid=%d elapsed_sec=%.3f",
            len(entries),
            len(results),
            valid_count,
            invalid_count,
            time.perf_counter() - start,
        )
        return {
            "results": results,
            "summary": {
                "checked": len(results),
                "valid": valid_count,
                "invalid": invalid_count,
            },
        }

    async def _validate_url_with_http_check(
        self,
        url: str,
        *,
        spot_name: str | None = None,
        claim: str | None = None,
    ) -> dict[str, Any]:
        """URL検証ツールの実処理。"""
        return await asyncio.to_thread(
            self._validate_url_with_http_check_sync,
            url,
            spot_name=spot_name,
            claim=claim,
        )

    def _validate_url_with_http_check_sync(
        self,
        url: str,
        *,
        spot_name: str | None = None,
        claim: str | None = None,
    ) -> dict[str, Any]:
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
                        "spot_name": spot_name,
                    }

                title_match = re.search(
                    r"<title[^>]*>(.*?)</title>", body, flags=re.IGNORECASE | re.DOTALL
                )
                title = title_match.group(1).strip() if title_match else ""
                plain_body = re.sub(r"<[^>]+>", " ", body)
                relevance = self._assess_source_relevance(
                    url=url,
                    final_url=final_url,
                    title=title,
                    body=plain_body,
                    spot_name=spot_name,
                    claim=claim,
                )
                if not relevance["is_relevant"]:
                    return {
                        "url": url,
                        "verdict": "invalid",
                        "reason": "relevance_mismatch",
                        "final_url": final_url,
                        "tls_valid": True,
                        "tls_error": None,
                        "spot_name": spot_name,
                        "claim": claim,
                        "relevance_score": relevance["score"],
                        "relevance_threshold": relevance["threshold"],
                    }

                return {
                    "url": url,
                    "verdict": "valid",
                    "reason": "ok",
                    "final_url": final_url,
                    "tls_valid": True,
                    "tls_error": None,
                    "spot_name": spot_name,
                    "claim": claim,
                    "relevance_score": relevance["score"],
                    "relevance_threshold": relevance["threshold"],
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

    def _assess_source_relevance(
        self,
        *,
        url: str,
        final_url: str,
        title: str,
        body: str,
        spot_name: str | None,
        claim: str | None,
    ) -> dict[str, Any]:
        """出典ページの関連性を簡易判定する。"""
        if not spot_name:
            return {"is_relevant": True, "score": 1.0, "threshold": 0.0}

        score = 0.0
        title_l = title.lower()
        body_l = body.lower()
        url_l = (url + " " + final_url).lower()

        if spot_name and spot_name in title:
            score += 0.5
        if spot_name and spot_name in body:
            score += 0.3
        if spot_name and spot_name.lower() in url_l:
            score += 0.2

        if claim:
            claim_keywords = [w for w in re.split(r"[\s、。・,/()（）]+", claim) if len(w) >= 2]
            hit_count = 0
            for keyword in claim_keywords[:8]:
                if keyword.lower() in title_l or keyword.lower() in body_l:
                    hit_count += 1
            if claim_keywords:
                score += min(0.3, 0.05 * hit_count)

        threshold = 0.35
        return {"is_relevant": score >= threshold, "score": round(score, 3), "threshold": threshold}

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
                "- url: {url} | verdict: {verdict} | reason: {reason} | spot: {spot_name} | relevance_score: {relevance_score} | tls_valid: {tls_valid} | tls_error: {tls_error}".format(
                    url=result.get("url"),
                    verdict=result.get("verdict"),
                    reason=result.get("reason"),
                    spot_name=result.get("spot_name"),
                    relevance_score=result.get("relevance_score"),
                    tls_valid=result.get("tls_valid"),
                    tls_error=result.get("tls_error"),
                )
            )
        return "\n".join(lines)

    def _extract_url_entries_with_context(self, text: str) -> list[dict[str, str | None]]:
        """StepA本文からURLとスポット文脈を抽出する。"""
        entries: list[dict[str, str | None]] = []
        seen_keys: set[str] = set()
        in_spot_section = False
        current_spot: str | None = None

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if re.match(r"^##\s+", line):
                in_spot_section = "スポット別の事実" in line
                if not in_spot_section:
                    current_spot = None

            if in_spot_section and re.match(r"^###\s+", line):
                heading_text = line[3:].strip()
                bracket_match = re.match(r"^\[(.+?)\]$", heading_text)
                if bracket_match:
                    heading_text = bracket_match.group(1).strip()
                current_spot = heading_text or None
                continue

            urls_in_line = re.findall(r"https?://[^\s)\]}>\"']+", line)
            if not urls_in_line:
                continue

            claim_text = re.sub(r"\[出典:[^\]]*\]", "", line)
            claim_text = re.sub(
                r"\[\s*検証\s*[:：]\s*valid\s*\]", "", claim_text, flags=re.IGNORECASE
            )
            claim_text = re.sub(r"https?://[^\s)\]}>\"']+", "", claim_text)
            claim_text = re.sub(r"^[-*]\s*", "", claim_text).strip()
            claim = claim_text if claim_text else None

            for raw_url in urls_in_line:
                url = raw_url.rstrip(".,;:!?。、）】＞")
                if not url:
                    continue
                dedupe_key = f"{url}|{current_spot or ''}|{claim or ''}"
                if dedupe_key in seen_keys:
                    continue
                seen_keys.add(dedupe_key)
                entries.append(
                    {
                        "url": url,
                        "spotName": current_spot,
                        "claim": claim,
                    }
                )

        return entries

    async def _validate_and_annotate_urls_in_text(
        self,
        text: str,
        *,
        trusted_valid_urls: set[str] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        url_entries = self._extract_url_entries_with_context(text)
        if not url_entries:
            return text, {"checked": 0, "valid": 0, "invalid": 0, "invalid_details": []}

        results = []
        trusted = trusted_valid_urls or set()
        for entry in url_entries[:20]:
            url = entry["url"] or ""
            if url in trusted:
                results.append(
                    {
                        "url": url,
                        "verdict": "valid",
                        "reason": "cached_valid",
                        "spot_name": entry.get("spotName"),
                        "claim": entry.get("claim"),
                    }
                )
                continue
            results.append(
                await self._validate_url_with_http_check(
                    url,
                    spot_name=entry.get("spotName"),
                    claim=entry.get("claim"),
                )
            )

        valid_urls = {r.get("url") for r in results if r.get("verdict") == "valid"}
        invalid_results = [r for r in results if r.get("verdict") != "valid"]
        valid_results = [r for r in results if r.get("verdict") == "valid"]

        annotated_text = text
        for result in results:
            url = result.get("url")
            if not isinstance(url, str):
                continue
            if result.get("verdict") == "valid":
                annotated_text = re.sub(
                    rf"{re.escape(url)}(?!\s*\[検証:\s*valid\])",
                    f"{url} [検証: valid]",
                    annotated_text,
                )
                continue
            # invalidなURLはStepBへ渡さないよう本文から除去する
            annotated_text = re.sub(
                re.escape(url),
                "[無効URL除去]",
                annotated_text,
            )

        summary = {
            "checked": len(results),
            "valid": len(valid_urls),
            "invalid": len(invalid_results),
            "invalid_details": [
                {
                    "url": item.get("url"),
                    "reason": item.get("reason"),
                }
                for item in invalid_results[:10]
            ],
            "valid_details": [
                {
                    "url": item.get("url"),
                }
                for item in valid_results[:10]
                if isinstance(item.get("url"), str) and item.get("url")
            ],
        }
        return annotated_text, summary

    def _build_url_validation_feedback_prompt(
        self,
        *,
        base_prompt: str,
        previous_response_text: str,
        validation_summary: dict[str, Any],
        feedback_round: int,
        repeated_invalid_urls: bool = False,
    ) -> str:
        invalid_lines = []
        for item in validation_summary.get("invalid_details", []):
            invalid_lines.append(f"- {item.get('url')} (reason={item.get('reason')})")
        invalid_text = "\n".join(invalid_lines) if invalid_lines else "- なし"
        valid_lines = []
        for item in validation_summary.get("valid_details", []):
            valid_lines.append(f"- {item.get('url')}")
        valid_text = "\n".join(valid_lines) if valid_lines else "- なし"

        expansion_instruction = self._build_stepa_search_expansion_instruction(
            feedback_round=feedback_round,
            repeated_invalid_urls=repeated_invalid_urls,
        )
        blocked_hosts_text = "\n".join(f"- {host}" for host in _STEPA_BLOCKED_SOURCE_HOSTS)

        return (
            f"{base_prompt}\n\n"
            "<url_validation_feedback>\n"
            "前回の回答には検証に失敗したURLが含まれています。以下のURLは出典として使わないでください。\n"
            f"{invalid_text}\n"
            "以下のURLは検証済みです。まず再利用し、不足分のみ新規URLを追加してください。\n"
            f"{valid_text}\n"
            "以下のホストは有効期限付きリダイレクトを返しやすいため、出典URLとして禁止します。\n"
            f"{blocked_hosts_text}\n"
            f"{expansion_instruction}"
            "有効な https:// URL のみで再検索し、各URLに [検証: valid] を付けて再出力してください。\n"
            "前回回答:\n"
            f"{previous_response_text}\n"
            "</url_validation_feedback>"
        )

    def _build_missing_url_feedback_prompt(
        self,
        *,
        base_prompt: str,
        previous_response_text: str,
        feedback_round: int,
        reusable_valid_urls: tuple[str, ...] = (),
    ) -> str:
        """URL未提示時の再抽出指示プロンプトを作成する。"""
        expansion_instruction = self._build_stepa_search_expansion_instruction(
            feedback_round=feedback_round,
            repeated_invalid_urls=False,
        )
        blocked_hosts_text = "\n".join(f"- {host}" for host in _STEPA_BLOCKED_SOURCE_HOSTS)
        reusable_urls_text = "\n".join([f"- {url}" for url in reusable_valid_urls[:10]])
        if not reusable_urls_text:
            reusable_urls_text = "- なし"
        strict_instruction = ""
        if feedback_round >= 2:
            strict_instruction = "前回までURLが提示されていません。各スポットについて最低1件の https:// URL を必須で含めてください。\n"

        return (
            f"{base_prompt}\n\n"
            "<url_required_feedback>\n"
            "前回の回答にはURL出典が含まれていませんでした。"
            "事実ごとに有効な https:// URL を必ず付与してください。\n"
            f"{strict_instruction}"
            "これまでに検証済みのURL（再利用推奨）:\n"
            f"{reusable_urls_text}\n"
            "以下のホストは出典URLとして使用禁止です。\n"
            f"{blocked_hosts_text}\n"
            f"{expansion_instruction}"
            "前回回答:\n"
            f"{previous_response_text}\n"
            "</url_required_feedback>"
        )

    def _build_stepa_search_expansion_instruction(
        self,
        *,
        feedback_round: int,
        repeated_invalid_urls: bool,
    ) -> str:
        """StepA再試行向けの検索拡張指示を構築する。"""
        instructions: list[str] = []
        if feedback_round <= 1:
            instructions.append(
                "検索クエリは同義語・旧称・英語表記を追加し、観点を変えて再検索してください。\n"
            )
        elif feedback_round == 2:
            instructions.append(
                "検索クエリに年代・自治体名・施設種別を追加し、前回未使用ドメインを優先してください。\n"
            )
        else:
            instructions.append(
                "3回目以降の再試行です。観光ポータルより公式機関ドメイン（自治体・博物館・文化財）を優先してください。\n"
            )
            instructions.append(
                "同一URLの再提示は禁止し、各スポットで最低1件は別ドメインの新規URLを提示してください。\n"
            )

        if repeated_invalid_urls:
            instructions.append(
                "前回と同じ無効URLが再提示されました。同一URLの再利用は禁止し、別ドメインへ切り替えてください。\n"
            )

        return "".join(instructions)

    def _extract_text(
        self,
        response: Any,
        *,
        request_id: str | None = None,
        attempt: int | None = None,
        max_retries: int | None = None,
    ) -> str:
        """レスポンスからテキストを取り出す

        Args:
            response: Gemini APIからのレスポンスオブジェクト
            request_id: 診断用リクエストID
            attempt: 現在の試行回数
            max_retries: 最大試行回数

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
                "Gemini response.text is empty; falling back to candidates.parts.text. request_id=%s attempt=%s/%s diagnostics=%s",
                request_id,
                attempt,
                max_retries,
                diagnostics,
            )
            return candidate_text

        reason_code = self._derive_empty_text_reason_code(diagnostics)
        snapshot_path = self._save_failure_snapshot(
            response=response,
            diagnostics=diagnostics,
            reason_code=reason_code,
            request_id=request_id,
            attempt=attempt,
            max_retries=max_retries,
        )
        self._logger.error(
            "Gemini response text is empty and no fallback text found. request_id=%s attempt=%s/%s reason_code=%s diagnostics=%s snapshot=%s",
            request_id,
            attempt,
            max_retries,
            reason_code,
            diagnostics,
            snapshot_path,
        )
        raise AIServiceInvalidRequestError(f"Response text is empty. reason_code={reason_code}")

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

    def _derive_empty_text_reason_code(self, diagnostics: dict[str, Any]) -> str:
        """空テキスト応答の理由コードを推定する。"""
        block_reason = diagnostics.get("prompt_feedback_block_reason")
        if block_reason:
            return "EMPTY_TEXT_SAFETY_BLOCK"

        finish_reasons = [str(value) for value in diagnostics.get("finish_reasons", [])]
        if any("UNEXPECTED_TOOL_CALL" in value for value in finish_reasons):
            return "EMPTY_TEXT_UNEXPECTED_TOOL_CALL"
        if any("SAFETY" in value for value in finish_reasons):
            return "EMPTY_TEXT_SAFETY_BLOCK"

        candidate_count = int(diagnostics.get("candidate_count", 0) or 0)
        text_part_count = int(diagnostics.get("text_part_count", 0) or 0)
        function_call_part_count = int(diagnostics.get("function_call_part_count", 0) or 0)
        other_part_count = int(diagnostics.get("other_part_count", 0) or 0)

        if candidate_count == 0:
            return "EMPTY_TEXT_NO_CANDIDATE"
        if text_part_count == 0 and function_call_part_count > 0:
            return "EMPTY_TEXT_TOOL_CALL_ONLY"
        if text_part_count == 0 and other_part_count > 0:
            return "EMPTY_TEXT_NON_TEXT_PARTS_ONLY"
        return "EMPTY_TEXT_UNKNOWN"

    def _extract_reason_code_from_error_message(self, message: str) -> str | None:
        """例外メッセージから理由コードを抽出する。"""
        match = re.search(r"reason_code=([A-Z0-9_]+)", message)
        if match:
            return match.group(1)
        return None

    def _build_failure_snapshot_payload(self, response: Any) -> dict[str, Any]:
        """失敗分析用の最小スナップショットを構築する。"""
        candidates_payload: list[dict[str, Any]] = []
        candidates = getattr(response, "candidates", None)
        if candidates:
            for candidate in candidates[:5]:
                content = getattr(candidate, "content", None)
                parts = getattr(content, "parts", None) or []
                part_payloads: list[dict[str, Any]] = []
                for part in parts[:10]:
                    function_call = getattr(part, "function_call", None)
                    function_name = getattr(function_call, "name", None)
                    part_payloads.append(
                        {
                            "has_text": isinstance(getattr(part, "text", None), str),
                            "function_name": function_name,
                        }
                    )
                candidates_payload.append(
                    {
                        "finish_reason": str(getattr(candidate, "finish_reason", None)),
                        "parts": part_payloads,
                    }
                )

        prompt_feedback = getattr(response, "prompt_feedback", None)
        block_reason = (
            getattr(prompt_feedback, "block_reason", None) if prompt_feedback is not None else None
        )

        return {
            "response_text_length": len(response.text)
            if isinstance(getattr(response, "text", None), str)
            else None,
            "candidate_count": len(candidates) if candidates else 0,
            "candidates": candidates_payload,
            "prompt_feedback_block_reason": str(block_reason) if block_reason is not None else None,
        }

    def _save_failure_snapshot(
        self,
        *,
        response: Any,
        diagnostics: dict[str, Any],
        reason_code: str,
        request_id: str | None,
        attempt: int | None,
        max_retries: int | None,
    ) -> str | None:
        """失敗時の診断情報をJSONファイルへ保存する。"""
        safe_request_id = request_id or f"unknown-{uuid4().hex[:8]}"
        timestamp_ms = int(time.time() * 1000)
        snapshot_path = _DIAGNOSTIC_SNAPSHOT_DIR / f"{safe_request_id}-{timestamp_ms}.json"

        payload = {
            "request_id": request_id,
            "attempt": attempt,
            "max_retries": max_retries,
            "reason_code": reason_code,
            "timestamp_ms": timestamp_ms,
            "diagnostics": diagnostics,
            "response": self._build_failure_snapshot_payload(response),
        }

        try:
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            snapshot_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return str(snapshot_path)
        except OSError as exc:
            self._logger.warning(
                "Failed to persist AI failure snapshot: path=%s error=%s", snapshot_path, exc
            )
            return None

    def _build_response_text_diagnostics(self, response: Any) -> dict[str, Any]:
        """text抽出失敗時の診断情報を構築する。"""
        text = getattr(response, "text", None)
        text_length = len(text) if isinstance(text, str) else None

        candidate_count = 0
        candidate_text_lengths: list[int] = []
        finish_reasons: list[str] = []
        text_part_count = 0
        function_call_part_count = 0
        other_part_count = 0
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
                    function_call = getattr(part, "function_call", None)
                    if isinstance(part_text, str):
                        text_part_count += 1
                        candidate_text_lengths.append(len(part_text))
                        continue
                    if function_call is not None:
                        function_call_part_count += 1
                        continue
                    other_part_count += 1

        prompt_feedback = getattr(response, "prompt_feedback", None)
        block_reason = None
        if prompt_feedback is not None:
            block_reason = getattr(prompt_feedback, "block_reason", None)

        return {
            "text_length": text_length,
            "candidate_count": candidate_count,
            "candidate_text_lengths": candidate_text_lengths[:10],
            "finish_reasons": finish_reasons[:10],
            "has_prompt_feedback": prompt_feedback is not None,
            "prompt_feedback_block_reason": str(block_reason) if block_reason is not None else None,
            "text_part_count": text_part_count,
            "function_call_part_count": function_call_part_count,
            "other_part_count": other_part_count,
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

    async def _try_repair_structured_payload(
        self,
        *,
        response: Any,
        response_schema: type[T],
        system_instruction: str | None,
        timeout: int,
    ) -> dict[str, Any] | None:
        """壊れた構造化JSONを再生成して回復を試みる。"""
        raw_payload = self._extract_raw_structured_payload(response)
        if not raw_payload:
            return None

        repair_prompt = (
            "以下は壊れている可能性のあるJSONです。"
            "スキーマに厳密に準拠した有効なJSONオブジェクトのみを返してください。"
            "説明文は不要です。\n"
            f"<broken_json>{raw_payload}</broken_json>"
        )

        json_schema = response_schema.model_json_schema(mode="serialization")
        repair_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.0,
            max_output_tokens=4096,
            response_mime_type="application/json",
            response_json_schema=json_schema,
        )

        try:
            repair_response = await asyncio.wait_for(
                self._client.models.generate_content(
                    model=self.model_name,
                    contents=repair_prompt,
                    config=repair_config,
                ),
                timeout=timeout,
            )
            return self._extract_structured_data(repair_response)
        except Exception as exc:
            self._logger.warning(
                "Structured response repair failed: error=%s",
                str(exc),
            )
            return None

    def _extract_raw_structured_payload(self, response: Any) -> str | None:
        """構造化レスポンス候補の生テキストを抽出する。"""
        text = getattr(response, "text", None)
        if isinstance(text, str) and text.strip():
            return text.strip()

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
                    return part_text.strip()
        return None

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
