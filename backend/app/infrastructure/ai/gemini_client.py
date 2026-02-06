"""Vertex AI Gemini APIクライアント実装"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import TYPE_CHECKING, Any, TypeVar

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
            try:
                response = await asyncio.wait_for(
                    self._client.models.generate_content(
                        model=self.model_name,
                        contents=contents,  # type: ignore[arg-type]
                        config=generation_config,
                    ),
                    timeout=timeout,
                )
                return self._extract_text(response)

            except TimeoutError as e:
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Request timeout: {e}") from e
                await self._exponential_backoff(attempt)

            except google_exceptions.ResourceExhausted as e:
                # クォータ超過エラー（429）
                if attempt == max_retries - 1:
                    raise AIServiceQuotaExceededError(f"API quota exceeded: {e}") from e
                # 指数バックオフでリトライ
                await self._exponential_backoff(attempt)

            except google_exceptions.DeadlineExceeded as e:
                # タイムアウトエラー
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Request timeout: {e}") from e
                await self._exponential_backoff(attempt)

            except google_exceptions.ServiceUnavailable as e:
                # サービス利用不可エラー（500系）
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Service unavailable: {e}") from e
                await self._exponential_backoff(attempt)

            except google_exceptions.InvalidArgument as e:
                # 不正な引数エラー（400）- リトライしない
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
                # その他のGoogleAPIエラー
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
                # JSONをパースして返す
                extracted_text = self._extract_text(response)
                try:
                    return json.loads(extracted_text)
                except (json.JSONDecodeError, ValueError) as e:
                    if attempt == max_retries - 1:
                        raise AIServiceInvalidRequestError(f"Invalid JSON response: {e}") from e
                    self._logger.warning(
                        "Invalid JSON response from Gemini. retry=%s/%s, length=%s, head=%r, tail=%r",
                        attempt + 1,
                        max_retries,
                        len(extracted_text),
                        extracted_text[:200],
                        extracted_text[-200:],
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

    def _extract_text(self, response: Any) -> str:
        """レスポンスからテキストを取り出す

        Args:
            response: Gemini APIからのレスポンスオブジェクト

        Returns:
            str: 抽出されたテキスト

        Raises:
            AIServiceInvalidRequestError: text属性が存在しない、または空の場合
        """
        if not hasattr(response, "text"):
            raise AIServiceInvalidRequestError("Response does not contain a text attribute.")
        text = response.text
        if text is None or (isinstance(text, str) and not text.strip()):
            raise AIServiceInvalidRequestError("Response text is empty.")
        return text

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
