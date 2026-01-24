"""
APIクライアント実装

このモジュールは、HTTPリクエストを実行し、レスポンスを処理するAPIClientクラスを提供します。
"""

import json

import requests

from models import APIResponse


class APIClient:
    """
    HTTPリクエストを実行し、レスポンスを返すクライアントクラス

    Attributes:
        base_url: APIのベースURL（例: http://localhost:8000）
        session: HTTPセッションオブジェクト
    """

    def __init__(self, base_url: str):
        """
        APIClientを初期化する

        Args:
            base_url: APIのベースURL
        """
        self.base_url = base_url.rstrip("/")  # 末尾のスラッシュを削除
        self.session = requests.Session()

    def execute_request(
        self,
        method: str,
        path: str,
        path_params: dict[str, str] | None = None,
        query_params: dict[str, str] | None = None,
        json_body: dict | None = None,
        files: list | None = None,
        data: dict | None = None,
    ) -> APIResponse:
        """
        APIリクエストを実行する

        Args:
            method: HTTPメソッド（GET, POST, PUT, DELETE）
            path: エンドポイントパス（パスパラメータはプレースホルダー形式）
            path_params: パスパラメータの辞書（例: {"plan_id": "123"}）
            query_params: クエリパラメータの辞書（例: {"user_id": "user123"}）
            json_body: JSONリクエストボディ
            files: ファイルアップロード用のリスト（例: [("files", ("name", bytes, "type"))]）
            data: フォームデータの辞書（multipart/form-data用）

        Returns:
            APIResponse: レスポンスオブジェクト
        """
        # パスパラメータを置換してURLを構築
        url = build_url(self.base_url, path, path_params or {})

        # クエリパラメータをフィルタリング（空文字列を除外）
        params = {k: v for k, v in (query_params or {}).items() if v}

        # リクエストを実行
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params if params else None,
                json=json_body,
                files=files,
                data=data,
                timeout=30,  # 30秒のタイムアウト
            )

            # レスポンスをパース
            return parse_response(response)

        except requests.exceptions.ConnectionError as e:
            # 接続エラー（サーバーに接続できない）
            return APIResponse(
                status_code=0,
                headers={},
                body="",
                is_json=False,
                json_data=None,
                error=f"接続エラー: サーバーに接続できません。ベースURLが正しいか、サーバーが起動しているか確認してください。詳細: {str(e)}",
            )
        except requests.exceptions.Timeout as e:
            # タイムアウトエラー
            return APIResponse(
                status_code=0,
                headers={},
                body="",
                is_json=False,
                json_data=None,
                error=f"タイムアウト: リクエストが30秒以内に完了しませんでした。詳細: {str(e)}",
            )
        except requests.exceptions.HTTPError as e:
            # HTTPエラー（4xx、5xxなど）
            return APIResponse(
                status_code=0,
                headers={},
                body="",
                is_json=False,
                json_data=None,
                error=f"HTTPエラー: {str(e)}",
            )
        except requests.exceptions.RequestException as e:
            # その他のリクエスト関連エラー
            return APIResponse(
                status_code=0,
                headers={},
                body="",
                is_json=False,
                json_data=None,
                error=f"リクエストエラー: {str(e)}",
            )
        except Exception as e:
            # 予期しないエラー
            return APIResponse(
                status_code=0,
                headers={},
                body="",
                is_json=False,
                json_data=None,
                error=f"予期しないエラー: {str(e)}",
            )


def build_url(base_url: str, path: str, path_params: dict[str, str]) -> str:
    """
    パスパラメータをURLに埋め込む

    Args:
        base_url: ベースURL（例: http://localhost:8000）
        path: エンドポイントパス（例: /api/v1/travel-plans/{plan_id}）
        path_params: パスパラメータの辞書（例: {"plan_id": "123"}）

    Returns:
        完全なURL（例: http://localhost:8000/api/v1/travel-plans/123）

    Examples:
        >>> build_url("http://localhost:8000", "/api/v1/travel-plans/{plan_id}", {"plan_id": "123"})
        'http://localhost:8000/api/v1/travel-plans/123'

        >>> build_url("http://localhost:8000", "/health", {})
        'http://localhost:8000/health'
    """
    # パスパラメータを置換
    url_path = path
    for key, value in path_params.items():
        url_path = url_path.replace(f"{{{key}}}", value)

    # ベースURLとパスを結合
    return f"{base_url}{url_path}"


def parse_response(response: requests.Response) -> APIResponse:
    """
    HTTPレスポンスをAPIResponseオブジェクトに変換する

    Args:
        response: requestsライブラリのResponseオブジェクト

    Returns:
        APIResponse: パース済みのレスポンスオブジェクト

    Examples:
        レスポンスがJSON形式の場合、is_jsonがTrueになり、json_dataにパース済みデータが格納される。
        レスポンスがJSON形式でない場合、is_jsonがFalseになり、bodyにテキストが格納される。
        JSONパースに失敗した場合、errorフィールドにエラーメッセージが格納される。
    """
    is_json = False
    json_data = None
    error = None

    # Content-Typeヘッダーをチェック
    content_type = response.headers.get("Content-Type", "")

    # JSONレスポンスの場合はパースを試みる
    if "application/json" in content_type:
        try:
            json_data = response.json()
            is_json = True
        except json.JSONDecodeError as e:
            # JSONパースに失敗した場合はエラーメッセージを設定
            error = f"JSONパースエラー: Content-Typeはapplication/jsonですが、レスポンスボディが有効なJSONではありません。詳細: {str(e)}"

    return APIResponse(
        status_code=response.status_code,
        headers=dict(response.headers),
        body=response.text,
        is_json=is_json,
        json_data=json_data,
        error=error,
    )
