"""AIサービスのアダプタ実装"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from app.application.ports.ai_service import IAIService
from app.application.ports.image_generation_service import IImageGenerationService
from app.infrastructure.ai.gemini_client import GeminiClient
from app.infrastructure.ai.image_generation_client import ImageGenerationClient

if TYPE_CHECKING:
    from app.infrastructure.ai.schemas.base import GeminiResponseSchema

T = TypeVar("T", bound="GeminiResponseSchema")


class GeminiAIService(IAIService, IImageGenerationService):
    """Gemini AIサービスアダプタ

    IAIServiceとIImageGenerationServiceの両インターフェースを実装し、
    GeminiClientとImageGenerationClientを使用してAI機能を提供する
    """

    def __init__(
        self,
        gemini_client: GeminiClient,
        image_generation_client: ImageGenerationClient,
        *,
        default_temperature: float = 0.7,
        default_max_output_tokens: int = 8192,
        default_timeout_seconds: int = 60,
    ) -> None:
        """GeminiAIServiceを初期化する

        Args:
            gemini_client: GeminiClientインスタンス（テキスト生成用）
            image_generation_client: ImageGenerationClientインスタンス（画像生成用）
            default_temperature: デフォルトの温度パラメータ
            default_max_output_tokens: デフォルトの最大出力トークン数
            default_timeout_seconds: デフォルトのタイムアウト秒数
        """
        self.client = gemini_client
        self.image_client = image_generation_client
        self.default_temperature = default_temperature
        self.default_max_output_tokens = default_max_output_tokens
        self.default_timeout_seconds = default_timeout_seconds

    async def generate_text(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        """基本的なテキスト生成を行う

        Args:
            prompt: 生成プロンプト
            system_instruction: システム命令（オプション）
            temperature: 生成の多様性を制御するパラメータ（0.0-2.0、Noneの場合は設定値を使用）
            max_output_tokens: 最大出力トークン数（Noneの場合は設定値を使用）

        Returns:
            str: 生成されたテキスト
        """
        return await self.client.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature if temperature is not None else self.default_temperature,
            max_output_tokens=max_output_tokens
            if max_output_tokens is not None
            else self.default_max_output_tokens,
            timeout=self.default_timeout_seconds,
        )

    async def generate_with_search(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        """Google Search統合でテキスト生成を行う

        Args:
            prompt: 生成プロンプト
            system_instruction: システム命令（オプション）
            temperature: 生成の多様性を制御するパラメータ（Function Calling時は0推奨、Noneの場合は0.0を使用）
            max_output_tokens: 最大出力トークン数（Noneの場合は設定値を使用）

        Returns:
            str: 生成されたテキスト（検索結果を含む）
        """
        return await self.client.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            tools=["google_search"],
            temperature=temperature if temperature is not None else 0.0,
            max_output_tokens=max_output_tokens
            if max_output_tokens is not None
            else self.default_max_output_tokens,
            timeout=self.default_timeout_seconds,
        )

    async def analyze_image(
        self,
        prompt: str,
        image_uri: str,
        *,
        system_instruction: str | None = None,
        tools: list[str] | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> str:
        """画像分析を行う

        Args:
            prompt: 画像に対する質問・指示
            image_uri: 画像のURI（GCS URIまたはHTTPS URL）
            system_instruction: システム命令（オプション）
            tools: 使用するツールのリスト（オプション）
            temperature: 生成の多様性を制御するパラメータ（0.0-2.0、Noneの場合は設定値を使用）
            max_output_tokens: 最大出力トークン数（Noneの場合は設定値を使用）

        Returns:
            str: 画像分析結果のテキスト
        """
        return await self.client.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            tools=tools,
            images=[image_uri],
            temperature=temperature if temperature is not None else self.default_temperature,
            max_output_tokens=max_output_tokens
            if max_output_tokens is not None
            else self.default_max_output_tokens,
            timeout=self.default_timeout_seconds,
        )

    async def analyze_image_structured(
        self,
        prompt: str,
        image_uri: str,
        response_schema: type[T],
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        """画像分析の構造化データを生成する

        Args:
            prompt: 画像に対する質問・指示
            image_uri: 画像のURI（GCS URIまたはHTTPS URL）
            response_schema: PydanticスキーマクラスのType（GeminiResponseSchemaのサブクラス）
            system_instruction: システム命令（オプション）
            temperature: 生成の多様性を制御するパラメータ（構造化出力時は0推奨、Noneの場合は0.0を使用）
            max_output_tokens: 最大出力トークン数（Noneの場合は設定値を使用）

        Returns:
            dict[str, Any]: スキーマに従った構造化データ（dict形式）
        """
        return await self.client.generate_content_with_schema(
            prompt=prompt,
            response_schema=response_schema,
            system_instruction=system_instruction,
            temperature=temperature if temperature is not None else 0.0,
            max_output_tokens=max_output_tokens
            if max_output_tokens is not None
            else self.default_max_output_tokens,
            images=[image_uri],
            timeout=self.default_timeout_seconds,
        )

    async def generate_structured_data(
        self,
        prompt: str,
        response_schema: type[T],
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        """JSON構造化データを生成する

        Args:
            prompt: 生成プロンプト
            response_schema: PydanticスキーマクラスのType（GeminiResponseSchemaのサブクラス）
            system_instruction: システム命令（オプション）
            temperature: 生成の多様性を制御するパラメータ（構造化出力時は0推奨、Noneの場合は0.0を使用）
            max_output_tokens: 最大出力トークン数（Noneの場合は設定値を使用）

        Returns:
            dict[str, Any]: スキーマに従った構造化データ（dict形式）
        """
        return await self.client.generate_content_with_schema(
            prompt=prompt,
            response_schema=response_schema,
            system_instruction=system_instruction,
            temperature=temperature if temperature is not None else 0.0,
            max_output_tokens=max_output_tokens
            if max_output_tokens is not None
            else self.default_max_output_tokens,
            timeout=self.default_timeout_seconds,
        )

    async def evaluate_travel_guide(
        self,
        guide_content: dict,
        evaluation_schema: type[T],
        evaluation_prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict:
        """旅行ガイドの品質を評価する

        Args:
            guide_content: 評価対象の旅行ガイドデータ
            evaluation_schema: PydanticスキーマクラスのType（GeminiResponseSchemaのサブクラス）
            evaluation_prompt: 評価プロンプト
            system_instruction: システム命令（オプション）
            temperature: 生成の多様性を制御するパラメータ（評価時は0推奨）
            max_output_tokens: 最大出力トークン数（オプション）

        Returns:
            dict: 評価結果
        """
        return await self.client.generate_content_with_schema(
            prompt=evaluation_prompt,
            response_schema=evaluation_schema,
            system_instruction=system_instruction,
            temperature=temperature if temperature is not None else 0.0,
            max_output_tokens=max_output_tokens
            if max_output_tokens is not None
            else self.default_max_output_tokens,
            timeout=self.default_timeout_seconds,
        )

    async def generate_image_prompt(
        self,
        spot_name: str,
        historical_background: str | None = None,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
    ) -> str:
        """スポット情報から画像生成プロンプトを生成する

        Args:
            spot_name: スポット名
            historical_background: 歴史的背景（オプション）
            system_instruction: システム命令（オプション）
            temperature: 生成の多様性を制御するパラメータ

        Returns:
            str: 画像生成用プロンプト
        """
        # プロンプトテンプレートを構築
        background = historical_background.strip() if historical_background else "なし"
        prompt = "\n".join(
            [
                "Vertex AI Image Generation API用の画像生成プロンプトを1文で作成してください。",
                f"スポット名: {spot_name}",
                f"歴史的背景: {background}",
                "要件: 日本語 / リアルで写真のようなスタイル / 80-140文字 / 説明文や前置きは不要。",
            ]
        )

        # Gemini APIを呼び出してプロンプトを生成
        return await self.client.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature if temperature is not None else self.default_temperature,
            # 画像プロンプト生成でMAX_TOKENS打ち切りが発生するため上限を引き上げる
            max_output_tokens=2048,
            timeout=self.default_timeout_seconds,
        )

    async def generate_image(
        self,
        prompt: str,
        *,
        aspect_ratio: str = "16:9",
        timeout: int = 60,
    ) -> bytes:
        """画像を生成する

        Note:
            このメソッドはVertex AI Image Generation APIを使用します。
            ImageGenerationClientを使用して画像を生成します。

        Args:
            prompt: 画像生成プロンプト
            aspect_ratio: アスペクト比（"16:9", "1:1", "9:16"など）
            timeout: タイムアウト秒数

        Returns:
            bytes: 生成された画像データ（JPEG形式）

        Raises:
            AIServiceConnectionError: 接続エラー
            AIServiceQuotaExceededError: クォータ超過エラー
            AIServiceInvalidRequestError: 不正リクエストエラー
        """
        return await self.image_client.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            timeout=timeout,
        )
