"""AI APIレスポンス用のPydantic基底スキーマ"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class GeminiResponseSchema(BaseModel):
    """Gemini APIのレスポンス用基底スキーマ

    すべてのGemini構造化出力スキーマはこのクラスを継承する。
    Pydanticの設定により、未知のフィールドを禁止し、文字列の前後空白を自動除去する。
    """

    model_config = ConfigDict(
        extra="forbid",  # 未定義フィールドを禁止
        str_strip_whitespace=True,  # 文字列の前後空白を自動除去
        validate_assignment=True,  # 代入時にもバリデーション実行
    )

    @classmethod
    def to_json_schema(cls) -> dict[str, Any]:
        """Pydanticモデルから JSON Schemaを生成する

        Returns:
            dict[str, Any]: Gemini APIに渡すJSON Schema
        """
        return cls.model_json_schema(mode="serialization")
