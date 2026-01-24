"""
API Testing Tool - メインアプリケーション

Historical Travel Agent APIの開発・デバッグを支援するStreamlitベースのAPI検証ツール。
開発者がブラウザ上でAPIエンドポイントを選択し、パラメータを入力してリクエストを実行し、
レスポンスを確認できるインタラクティブなツールです。

使用方法:
    streamlit run app.py

環境変数:
    API_BASE_URL: バックエンドAPIのベースURL（デフォルト: http://localhost:8000）
"""

import streamlit as st

from api_client import APIClient
from endpoints import ENDPOINTS
from ui.settings import render_settings
from ui.endpoint_selector import render_endpoint_selector
from ui.request_builder import render_request_form
from ui.response_viewer import render_response


def main():
    """
    Streamlitアプリケーションのメインエントリーポイント

    アプリケーションフロー:
    1. ページ設定（タイトル、レイアウト）
    2. サイドバーに設定パネルとエンドポイント選択を配置
    3. メインエリアにリクエストフォームとレスポンス表示を配置
    4. 実行ボタンクリック時のリクエスト送信処理
    5. セッションステートの管理

    要件:
        - 1.1: エンドポイント選択機能
        - 4.1: リクエスト実行機能
    """
    # ページ設定
    st.set_page_config(
        page_title="API Testing Tool",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # タイトル
    st.title("🧪 API Testing Tool")
    st.markdown("Historical Travel Agent APIの開発・デバッグツール")
    st.divider()

    # セッションステートの初期化
    if "response" not in st.session_state:
        st.session_state.response = None

    # サイドバー: 設定パネル
    base_url = render_settings()

    st.sidebar.divider()

    # サイドバー: エンドポイント選択
    selected_endpoint = render_endpoint_selector(ENDPOINTS)

    # メインエリア
    if selected_endpoint is None:
        # エンドポイントが選択されていない場合
        st.info("👈 サイドバーからエンドポイントを選択してください")

        # 使用方法を表示
        st.markdown("### 使用方法")
        st.markdown("""
        1. **設定**: サイドバーでベースURLを設定します（デフォルト: http://localhost:8000）
        2. **エンドポイント選択**: サイドバーからテストしたいエンドポイントを選択します
        3. **パラメータ入力**: 必要なパラメータ（パスパラメータ、クエリパラメータ、リクエストボディ）を入力します
        4. **実行**: 「リクエストを実行」ボタンをクリックしてAPIリクエストを送信します
        5. **レスポンス確認**: ステータスコードとレスポンスボディを確認します
        """)

        # エンドポイント一覧を表示
        st.markdown("### 利用可能なエンドポイント")

        # カテゴリ別にエンドポイントを表示
        categories = {
            "旅行計画": [],
            "旅行ガイド": [],
            "振り返り": [],
            "スポット振り返り": [],
            "ヘルスチェック": [],
        }

        for endpoint in ENDPOINTS:
            if "/travel-plans" in endpoint.path:
                categories["旅行計画"].append(endpoint)
            elif "/travel-guides" in endpoint.path:
                categories["旅行ガイド"].append(endpoint)
            elif "/reflections" in endpoint.path:
                categories["振り返り"].append(endpoint)
            elif "/spot-reflections" in endpoint.path:
                categories["スポット振り返り"].append(endpoint)
            elif endpoint.path in ["/", "/health"]:
                categories["ヘルスチェック"].append(endpoint)

        for category, endpoints in categories.items():
            if endpoints:
                st.markdown(f"**{category}**")
                for endpoint in endpoints:
                    st.markdown(
                        f"- `{endpoint.method}` {endpoint.name}: {endpoint.description}"
                    )

    else:
        # エンドポイントが選択されている場合

        # リクエストフォームを表示
        request_data = render_request_form(selected_endpoint)

        # 実行ボタンがクリックされた場合
        if request_data["execute"]:
            # APIクライアントを初期化
            client = APIClient(base_url)

            # リクエストパラメータを準備
            path_params = request_data["path_params"]
            query_params = request_data["query_params"]
            json_body = request_data["body"]
            files = request_data["files"]
            form_data = request_data["form_data"]

            # バリデーション: 必須パラメータのチェック
            validation_errors = []

            # パスパラメータの検証
            for param in selected_endpoint.path_params:
                if not path_params.get(param):
                    validation_errors.append(f"パスパラメータ '{param}' は必須です")

            # multipart/form-dataの場合のバリデーション
            if selected_endpoint.body_type == "multipart":
                if form_data:
                    if not form_data.get("plan_id"):
                        validation_errors.append(
                            "フォームフィールド 'plan_id' は必須です"
                        )
                    if not form_data.get("spot_name"):
                        validation_errors.append(
                            "フォームフィールド 'spot_name' は必須です"
                        )
                if not files:
                    validation_errors.append(
                        "少なくとも1つの画像ファイルをアップロードしてください"
                    )

            # バリデーションエラーがある場合
            if validation_errors:
                st.error("入力エラー:")
                for error in validation_errors:
                    st.error(f"  • {error}")
            else:
                # リクエストを実行
                with st.spinner("リクエストを送信中..."):
                    # multipart/form-dataの場合
                    if selected_endpoint.body_type == "multipart" and files:
                        # ファイルをrequestsライブラリの形式に変換
                        files_list = [
                            ("files", (f.name, f.getvalue(), f.type)) for f in files
                        ]

                        # フォームデータとファイルを送信
                        response = client.execute_request(
                            method=selected_endpoint.method,
                            path=selected_endpoint.path,
                            path_params=path_params,
                            query_params=query_params,
                            json_body=None,  # multipartの場合はjson_bodyは使用しない
                            files=files_list,
                            data=form_data,
                        )
                    else:
                        # 通常のリクエスト（JSON）
                        response = client.execute_request(
                            method=selected_endpoint.method,
                            path=selected_endpoint.path,
                            path_params=path_params,
                            query_params=query_params,
                            json_body=json_body,
                            files=None,
                        )

                    # レスポンスをセッションステートに保存
                    st.session_state.response = response

        # レスポンスを表示
        if st.session_state.response is not None:
            st.divider()
            render_response(st.session_state.response)


if __name__ == "__main__":
    main()
