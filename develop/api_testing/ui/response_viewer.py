"""
レスポンス表示UIコンポーネント

このモジュールは、APIレスポンスを表示するUIコンポーネントを提供します。
"""

import streamlit as st
from models import APIResponse


def render_response(response: APIResponse):
    """
    APIレスポンスを表示する

    HTTPステータスコードを色分けして表示し、レスポンスボディを
    適切な形式（JSON整形表示またはテキスト表示）で表示します。

    Args:
        response: APIResponseオブジェクト

    要件:
        - 5.1: HTTPステータスコードを表示する
        - 5.2: レスポンスボディをJSON形式で整形して表示する
        - 5.3: レスポンスボディがJSONでない場合はテキストとして表示する
    """
    st.subheader("レスポンス")

    # HTTPステータスコードの色分け表示
    status_code = response.status_code

    # ステータスコードの色分け: 2xx=緑、4xx=黄、5xx=赤
    if 200 <= status_code < 300:
        # 成功（2xx）: 緑色
        st.success(f"**ステータスコード:** {status_code}")
    elif 400 <= status_code < 500:
        # クライアントエラー（4xx）: 黄色（警告）
        st.warning(f"**ステータスコード:** {status_code}")
    elif 500 <= status_code < 600:
        # サーバーエラー（5xx）: 赤色（エラー）
        st.error(f"**ステータスコード:** {status_code}")
    else:
        # その他のステータスコード: 通常表示
        st.info(f"**ステータスコード:** {status_code}")

    # エラーメッセージの表示
    if response.error:
        st.error(f"**エラー:** {response.error}")
        return

    # レスポンスボディの表示
    st.markdown("---")
    st.markdown("**レスポンスボディ:**")

    if response.is_json and response.json_data is not None:
        # JSONレスポンスの整形表示
        st.json(response.json_data)
    elif response.body:
        # テキストレスポンスの表示
        st.code(response.body, language="text")
    else:
        # レスポンスボディが空の場合
        st.info("レスポンスボディは空です")

    # レスポンスヘッダーの表示（折りたたみ可能）
    with st.expander("レスポンスヘッダーを表示"):
        if response.headers:
            for key, value in response.headers.items():
                st.text(f"{key}: {value}")
        else:
            st.info("レスポンスヘッダーがありません")
