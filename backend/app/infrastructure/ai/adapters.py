"""AIサービスのアダプタ実装"""

from typing import Any

from app.application.ports.ai_service import IAIService
from app.infrastructure.ai.gemini_client import GeminiClient


class GeminiAIService(IAIService):
    """Gemini AIサービスアダプタ

    IAIServiceインターフェースを実装し、
    GeminiClientを使用してAI機能を提供する
    """

    def __init__(
        self,
        gemini_client: GeminiClient,
        *,
        default_temperature: float = 0.7,
        default_max_output_tokens: int = 8192,
        default_timeout_seconds: int = 60,
    ) -> None:
        """GeminiAIServiceを初期化する

        Args:
            gemini_client: GeminiClientインスタンス
            default_temperature: デフォルトの温度パラメータ
            default_max_output_tokens: デフォルトの最大出力トークン数
        """
        self.client = gemini_client
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
        response_schema: dict[str, Any],
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        """画像分析の構造化データを生成する

        Args:
            prompt: 画像に対する質問・指示
            image_uri: 画像のURI（GCS URIまたはHTTPS URL）
            response_schema: レスポンスのJSONスキーマ
            system_instruction: システム命令（オプション）
            temperature: 生成の多様性を制御するパラメータ（構造化出力時は0推奨、Noneの場合は0.0を使用）
            max_output_tokens: 最大出力トークン数（Noneの場合は設定値を使用）

        Returns:
            dict[str, Any]: スキーマに従った構造化データ
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
        response_schema: dict[str, Any],
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        """JSON構造化データを生成する

        Args:
            prompt: 生成プロンプト
            response_schema: レスポンスのJSONスキーマ
            system_instruction: システム命令（オプション）
            temperature: 生成の多様性を制御するパラメータ（構造化出力時は0推奨、Noneの場合は0.0を使用）
            max_output_tokens: 最大出力トークン数（Noneの場合は設定値を使用）

        Returns:
            dict[str, Any]: スキーマに従った構造化データ
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
        evaluation_schema: dict,
        evaluation_prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
    ) -> dict:
        """旅行ガイドの品質を評価する

        Args:
            guide_content: 評価対象の旅行ガイドデータ
            evaluation_schema: 評価結果のスキーマ
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
