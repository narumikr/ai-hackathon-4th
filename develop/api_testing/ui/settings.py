"""設定パネルUI

ベースURL設定を表示するコンポーネント。
"""

import os
import streamlit as st


def render_settings() -> str:
    """
    設定パネルを表示し、ベースURLを取得する

    環境変数API_BASE_URLから読み込み、設定されていない場合は
    デフォルトのhttp://localhost:8000を使用する。
    サイドバーでベースURLを変更可能。

    Returns:
        str: ベースURL
    """
    # 環境変数からベースURLを読み込む（デフォルト: http://localhost:8000）
    default_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

    # サイドバーに設定セクションを表示
    st.sidebar.header("⚙️ 設定")

    # ベースURLの入力フィールド
    base_url = st.sidebar.text_input(
        "ベースURL",
        value=default_base_url,
        help="バックエンドAPIのベースURL（例: http://localhost:8000）",
    )

    # 現在のベースURLを表示
    st.sidebar.caption(f"現在のベースURL: `{base_url}`")

    return base_url
