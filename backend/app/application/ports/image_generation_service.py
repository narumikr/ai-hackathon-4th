"""画像生成サービスのポートインターフェース"""

from __future__ import annotations

from abc import ABC, abstractmethod


class IImageGenerationService(ABC):
    """画像生成サービスのインターフェース

    スポット画像生成に必要なメソッドを定義する
    IAIServiceから分離し、インターフェース分離原則(ISP)に準拠する
    """

    @abstractmethod
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
        pass

    @abstractmethod
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
            既存のGeminiClientとは異なる実装が必要です。

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
        pass
