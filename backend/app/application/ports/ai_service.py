"""AIサービスのポートインターフェース"""

from abc import ABC, abstractmethod
from typing import Any


class IAIService(ABC):
    """AIサービスのインターフェース

    ドメイン層でのAIサービスインターフェース定義
    実装はインフラ層で提供される
    """

    @abstractmethod
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
            temperature: 生成の多様性を制御するパラメータ（0.0-2.0、Noneの場合は実装のデフォルト値を使用）
            max_output_tokens: 最大出力トークン数（Noneの場合は実装のデフォルト値を使用）

        Returns:
            str: 生成されたテキスト
        """
        pass

    @abstractmethod
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
            max_output_tokens: 最大出力トークン数（Noneの場合は実装のデフォルト値を使用）

        Returns:
            str: 生成されたテキスト（検索結果を含む）
        """
        pass

    @abstractmethod
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
            temperature: 生成の多様性を制御するパラメータ（0.0-2.0、Noneの場合は実装のデフォルト値を使用）
            max_output_tokens: 最大出力トークン数（Noneの場合は実装のデフォルト値を使用）

        Returns:
            str: 画像分析結果のテキスト
        """
        pass

    @abstractmethod
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
            max_output_tokens: 最大出力トークン数（Noneの場合は実装のデフォルト値を使用）

        Returns:
            dict[str, Any]: スキーマに従った構造化データ
        """
        pass
