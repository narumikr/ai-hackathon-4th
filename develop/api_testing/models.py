"""
データモデル定義

このモジュールは、API Testing Toolで使用するデータモデルを定義します。
"""

from dataclasses import dataclass


@dataclass
class EndpointDefinition:
    """
    APIエンドポイントのメタデータを保持するデータクラス

    Attributes:
        name: エンドポイントの表示名
        method: HTTPメソッド（GET, POST, PUT, DELETE）
        path: エンドポイントパス（例: /api/v1/travel-plans/{plan_id}）
        path_params: パスパラメータ名のリスト（例: ["plan_id"]）
        query_params: クエリパラメータ名のリスト（例: ["user_id"]）
        has_body: リクエストボディの有無
        body_type: リクエストボディのタイプ（"json" or "multipart"）
        description: エンドポイントの説明
    """

    name: str
    method: str
    path: str
    path_params: list[str]
    query_params: list[str]
    has_body: bool
    body_type: str
    description: str


@dataclass
class APIResponse:
    """
    APIレスポンスを保持するデータクラス

    Attributes:
        status_code: HTTPステータスコード
        headers: レスポンスヘッダーの辞書
        body: レスポンスボディの文字列
        is_json: レスポンスがJSON形式かどうか
        json_data: パース済みのJSONデータ（JSONでない場合はNone）
        error: エラーメッセージ（エラーがない場合はNone）
    """

    status_code: int
    headers: dict[str, str]
    body: str
    is_json: bool
    json_data: dict | list | None
    error: str | None
