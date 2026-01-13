"""Vertex AI Gemini APIクライアント実装"""

import json
from typing import Any

import vertexai
from google.api_core import exceptions as google_exceptions
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)

try:
    from vertexai.preview import grounding  # type: ignore[import-not-found]
except ImportError:
    grounding = None  # type: ignore[assignment]

from app.infrastructure.ai.exceptions import (
    AIServiceConnectionError,
    AIServiceInvalidRequestError,
    AIServiceQuotaExceededError,
)


class GeminiClient:
    """Vertex AI Gemini APIクライアント

    Gemini 3 Flashモデルを使用したテキスト生成、画像分析、
    Function Calling、構造化出力などの機能を提供する
    """

    def __init__(
        self,
        project_id: str,
        location: str = "asia-northeast1",
        model_name: str = "gemini-3-flash",
    ) -> None:
        """GeminiClientを初期化する

        Args:
            project_id: Google CloudプロジェクトID
            location: Vertex AIのロケーション（デフォルト: asia-northeast1）
            model_name: 使用するモデル名（デフォルト: gemini-3-flash）
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        # Vertex AIの初期化
        vertexai.init(project=project_id, location=location)

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
        # モデルの初期化
        model = GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction,
        )

        # ツールの設定
        model_tools = self._prepare_tools(tools) if tools else None

        # GenerationConfigの作成
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        # コンテンツの準備
        contents = self._prepare_contents(prompt, images)

        # リトライ付きで生成を実行
        for attempt in range(max_retries):
            try:
                response = await model.generate_content_async(
                    contents=contents,  # type: ignore[arg-type]
                    tools=model_tools,
                    generation_config=generation_config,
                )
                return response.text

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
        response_schema: dict[str, Any],
        *,
        system_instruction: str | None = None,
        tools: list[str] | None = None,
        temperature: float = 0.0,
        max_output_tokens: int = 8192,
        timeout: int = 60,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """JSON構造化データを生成する

        Args:
            prompt: 生成プロンプト
            response_schema: レスポンスのJSONスキーマ
            system_instruction: システム命令（オプション）
            tools: 使用するツールのリスト（例: ["google_search"]）
            temperature: 生成の多様性を制御するパラメータ（構造化出力時は0推奨）
            max_output_tokens: 最大出力トークン数
            timeout: タイムアウト秒数
            max_retries: 最大リトライ回数

        Returns:
            dict[str, Any]: スキーマに従った構造化データ

        Raises:
            AIServiceConnectionError: 接続エラー
            AIServiceQuotaExceededError: クォータ超過エラー
            AIServiceInvalidRequestError: 不正リクエストエラー
        """
        # モデルの初期化
        model = GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction,
        )

        # ツールの設定
        model_tools = self._prepare_tools(tools) if tools else None

        # GenerationConfigの作成（JSON出力モード）
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json",
            response_schema=response_schema,
        )

        # リトライ付きで生成を実行
        for attempt in range(max_retries):
            try:
                response = await model.generate_content_async(
                    contents=prompt,
                    tools=model_tools,
                    generation_config=generation_config,
                )
                # JSONをパースして返す
                return json.loads(response.text)

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

            except (json.JSONDecodeError, ValueError) as e:
                # JSONパースエラー - リトライしない
                raise AIServiceInvalidRequestError(f"Invalid JSON response: {e}") from e

            except google_exceptions.GoogleAPIError as e:
                if attempt == max_retries - 1:
                    raise AIServiceConnectionError(f"Google API error: {e}") from e
                await self._exponential_backoff(attempt)

        raise AIServiceConnectionError("Max retries exceeded")

    def _prepare_tools(self, tool_names: list[str]) -> list[Tool]:
        """ツールを準備する

        Args:
            tool_names: ツール名のリスト

        Returns:
            list[Tool]: ツールオブジェクトのリスト
        """
        tools = []
        for tool_name in tool_names:
            if tool_name == "google_search":
                # Google Search統合
                if grounding is None:
                    raise AIServiceInvalidRequestError(
                        "Google Search tool is not available. Please check vertexai SDK version."
                    )
                tools.append(
                    Tool.from_google_search_retrieval(
                        grounding.GoogleSearchRetrieval()  # type: ignore[union-attr]
                    )
                )
            # 将来的に他のツール（google_maps, code_executionなど）を追加可能
        return tools

    def _prepare_contents(self, prompt: str, images: list[str] | None = None) -> list[Part] | str:
        """コンテンツを準備する

        Args:
            prompt: テキストプロンプト
            images: 画像URIのリスト（オプション）

        Returns:
            list[Part] | str: コンテンツ（画像がある場合はPartのリスト、ない場合は文字列）
        """
        if not images:
            return prompt

        # 画像がある場合はPartのリストとして構築
        parts = []
        for image_uri in images:
            parts.append(Part.from_uri(image_uri, mime_type="image/jpeg"))
        parts.append(Part.from_text(prompt))
        return parts

    async def _exponential_backoff(self, attempt: int) -> None:
        """指数バックオフを実行する

        Args:
            attempt: 現在の試行回数（0から開始）
        """
        import asyncio

        wait_time = min(2**attempt, 8)  # 最大8秒
        await asyncio.sleep(wait_time)
