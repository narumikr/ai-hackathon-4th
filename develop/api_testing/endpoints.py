"""
エンドポイント定義

このモジュールは、Historical Travel Agent APIのすべてのエンドポイント定義と
リクエストボディのサンプルデータを提供します。
"""

from models import EndpointDefinition


# すべてのAPIエンドポイントの定義リスト
ENDPOINTS = [
    # 旅行計画API
    EndpointDefinition(
        name="旅行計画作成",
        method="POST",
        path="/api/v1/travel-plans",
        path_params=[],
        query_params=[],
        has_body=True,
        body_type="json",
        description="旅行計画を作成する",
    ),
    EndpointDefinition(
        name="旅行計画一覧取得",
        method="GET",
        path="/api/v1/travel-plans",
        path_params=[],
        query_params=["user_id"],
        has_body=False,
        body_type="",
        description="ユーザーの旅行計画一覧を取得する",
    ),
    EndpointDefinition(
        name="旅行計画取得",
        method="GET",
        path="/api/v1/travel-plans/{plan_id}",
        path_params=["plan_id"],
        query_params=[],
        has_body=False,
        body_type="",
        description="旅行計画を取得する",
    ),
    EndpointDefinition(
        name="旅行計画更新",
        method="PUT",
        path="/api/v1/travel-plans/{plan_id}",
        path_params=["plan_id"],
        query_params=[],
        has_body=True,
        body_type="json",
        description="旅行計画を更新する",
    ),
    EndpointDefinition(
        name="旅行計画削除",
        method="DELETE",
        path="/api/v1/travel-plans/{plan_id}",
        path_params=["plan_id"],
        query_params=[],
        has_body=False,
        body_type="",
        description="旅行計画を削除する",
    ),
    # 旅行ガイドAPI
    EndpointDefinition(
        name="旅行ガイド生成",
        method="POST",
        path="/api/v1/travel-guides",
        path_params=[],
        query_params=[],
        has_body=True,
        body_type="json",
        description="旅行ガイド生成を開始する",
    ),
    # 振り返りAPI
    EndpointDefinition(
        name="振り返り生成",
        method="POST",
        path="/api/v1/reflections",
        path_params=[],
        query_params=[],
        has_body=True,
        body_type="json",
        description="振り返り生成を開始する",
    ),
    # スポット振り返りAPI
    EndpointDefinition(
        name="スポット写真登録",
        method="POST",
        path="/api/v1/spot-reflections",
        path_params=[],
        query_params=[],
        has_body=True,
        body_type="multipart",
        description="スポットの写真と感想を登録する",
    ),
    # ヘルスチェック
    EndpointDefinition(
        name="ルート",
        method="GET",
        path="/",
        path_params=[],
        query_params=[],
        has_body=False,
        body_type="",
        description="ルートエンドポイント",
    ),
    EndpointDefinition(
        name="ヘルスチェック",
        method="GET",
        path="/health",
        path_params=[],
        query_params=[],
        has_body=False,
        body_type="",
        description="ヘルスチェックエンドポイント",
    ),
]


# 各エンドポイントのリクエストボディのサンプルデータ
BODY_SAMPLES = {
    "/api/v1/travel-plans": {
        "userId": "user123",
        "title": "京都歴史巡り",
        "destination": "京都",
        "spots": [
            {
                "name": "金閣寺",
                "description": "金色に輝く寺院",
                "userNotes": "朝早く訪れるのがおすすめ",
            }
        ],
    },
    "/api/v1/travel-plans/{plan_id}": {
        "title": "奈良歴史巡り",
        "destination": "奈良",
        "spots": [
            {
                "name": "東大寺",
                "description": "大仏で有名な寺院",
                "userNotes": "鹿にせんべいをあげられる",
            }
        ],
        "status": "planning",
    },
    "/api/v1/travel-guides": {"planId": "plan123"},
    "/api/v1/reflections": {
        "planId": "plan123",
        "userId": "user123",
        "userNotes": "とても楽しい旅行でした",
    },
}
