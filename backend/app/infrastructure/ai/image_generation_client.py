"""Vertex AI Image Generation APIクライアント実装"""

from __future__ import annotations

import asyncio

from google import genai
from google.api_core import exceptions as google_exceptions
from google.genai import errors as genai_errors
from google.genai import types

from app.infrastructure.ai.exceptions import (
    AIServiceConnectionError,
    AIServiceInvalidRequestError,
    AIServiceQuotaExceededError,
)


class ImageGenerationClient:
    """Vertex AI Image Generation APIクライアント

    Vertex AI Image Generation APIを使用して画像を生成する
    """

    def __init__(
        self,
        project_id: str,
        location: str = "global",
        model_name: str = "gemini-2.5-flash-image",
    ) -> None:
        """ImageGenerationClientを初期化する

        Args:
            project_id: Google CloudプロジェクトID
            location: Vertex AIのロケーション（デフォルト: asia-northeast1）
            model_name: 使用するモデル名（デフォルト: gemini-2.5-flash-image）
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        # Vertex AI用のGoogle Gen AI SDKクライアント（非同期版）
        self._client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
        ).aio

    async def generate_image(
        self,
        prompt: str,
        *,
        aspect_ratio: str = "16:9",
        timeout: int = 60,
        max_retries: int = 3,
    ) -> bytes:
        """画像を生成する

        Args:
            prompt: 画像生成プロンプト
            aspect_ratio: アスペクト比（"16:9", "1:1", "9:16"など）
            timeout: タイムアウト秒数
            max_retries: 最大リトライ回数

        Returns:
            bytes: 生成された画像データ（JPEG形式）

        Raises:
            AIServiceConnectionError: 接続エラー
            AIServiceQuotaExceededError: クォータ超過エラー
            AIServiceInvalidRequestError: 不正リクエストエラー
        """
        # GenerateContentConfigの作成（画像生成用）
        generation_config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
            ),
        )

        # リトライ付きで生成を実行
        for attempt in range(max_retries):
            try:
                response = await asyncio.wait_for(
                    self._client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=generation_config,
                    ),
                    timeout=timeout,
                )

                # 画像データを抽出
                return self._extract_image_data(response)

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

    def _extract_image_data(self, response: types.GenerateContentResponse) -> bytes:
        """レスポンスから画像データを取り出す

        Args:
            response: Gemini APIからのレスポンスオブジェクト

        Returns:
            bytes: 抽出された画像データ

        Raises:
            AIServiceInvalidRequestError: 画像データが存在しない場合
        """
        # レスポンスから最初の候補を取得
        if not response.candidates or len(response.candidates) == 0:
            raise AIServiceInvalidRequestError("Response does not contain any candidates.")

        candidate = response.candidates[0]

        # 候補からパーツを取得
        if not candidate.content or not candidate.content.parts:
            raise AIServiceInvalidRequestError("Response does not contain any parts.")

        # 最初のパーツから画像データを取得
        for part in candidate.content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                if part.inline_data.data:
                    return part.inline_data.data

        raise AIServiceInvalidRequestError("Response does not contain image data.")

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """レート制限やクォータ超過のエラーか判定する

        Args:
            error: 判定対象のエラー

        Returns:
            bool: レート制限エラーの場合True
        """
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
