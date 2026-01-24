"""
リクエストフォームUI

このモジュールは、選択されたエンドポイントのリクエストフォームを表示し、
ユーザー入力を収集する機能を提供します。
"""

import json
from typing import Any

import streamlit as st

from models import EndpointDefinition
from endpoints import BODY_SAMPLES


def render_request_form(endpoint: EndpointDefinition) -> dict[str, Any]:
    """
    リクエストフォームを表示し、入力値を収集する

    Args:
        endpoint: エンドポイント定義

    Returns:
        入力値の辞書（path_params, query_params, body, files, form_data）
        {
            "path_params": dict[str, str],
            "query_params": dict[str, str],
            "body": dict | None,
            "files": list[UploadedFile] | None,
            "form_data": dict[str, str] | None
        }
    """
    # エンドポイント情報を表示
    st.header(f"{endpoint.name}")

    # メソッドとパスを表示
    col1, col2 = st.columns([1, 4])
    with col1:
        # HTTPメソッドをバッジ風に表示
        method_color = {"GET": "🟢", "POST": "🔵", "PUT": "🟡", "DELETE": "🔴"}.get(
            endpoint.method, "⚪"
        )
        st.markdown(f"### {method_color} {endpoint.method}")

    with col2:
        st.code(endpoint.path, language="")

    # 説明を表示
    st.markdown(f"*{endpoint.description}*")

    st.divider()

    # 入力値を格納する辞書
    result = {
        "path_params": {},
        "query_params": {},
        "body": None,
        "files": None,
        "form_data": None,
    }

    # パスパラメータの入力フィールド
    if endpoint.path_params:
        st.subheader("📍 パスパラメータ")
        for param in endpoint.path_params:
            value = st.text_input(
                f"{param}", key=f"path_{param}", help=f"パスパラメータ: {param}"
            )
            result["path_params"][param] = value
        st.divider()

    # クエリパラメータの入力フィールド
    if endpoint.query_params:
        st.subheader("🔍 クエリパラメータ")
        for param in endpoint.query_params:
            value = st.text_input(
                f"{param}", key=f"query_{param}", help=f"クエリパラメータ: {param}"
            )
            result["query_params"][param] = value
        st.divider()

    # リクエストボディの入力
    if endpoint.has_body:
        if endpoint.body_type == "json":
            # JSON形式のリクエストボディ
            st.subheader("📝 リクエストボディ (JSON)")

            # サンプルデータを取得
            sample_data = BODY_SAMPLES.get(endpoint.path, {})
            default_json = json.dumps(sample_data, indent=2, ensure_ascii=False)

            # サンプル表示ボタン
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("📋 サンプルを表示", key="show_sample"):
                    st.session_state[f"body_{endpoint.path}"] = default_json

            # JSONテキストエリア
            body_text = st.text_area(
                "JSON",
                value=st.session_state.get(f"body_{endpoint.path}", default_json),
                height=300,
                key=f"body_input_{endpoint.path}",
                help="JSON形式でリクエストボディを入力してください",
            )

            # JSONのバリデーション
            if body_text.strip():
                is_valid, parsed_json, error_msg = validate_json_body(body_text)
                if is_valid:
                    st.success("✅ 有効なJSON形式です")
                    result["body"] = parsed_json
                else:
                    st.error(f"❌ JSONパースエラー: {error_msg}")
                    result["body"] = None

            st.divider()

        elif endpoint.body_type == "multipart":
            # multipart/form-data形式のリクエストボディ
            st.subheader("📤 ファイルアップロード (multipart/form-data)")

            # フォームフィールドの入力
            st.markdown("**フォームフィールド**")
            plan_id = st.text_input("planId", key="form_plan_id", help="旅行計画ID")
            user_id = st.text_input("userId", key="form_user_id", help="ユーザーID")
            spot_id = st.text_input("spotId", key="form_spot_id", help="スポットID")
            spot_note = st.text_area(
                "spotNote (オプショナル)",
                key="form_spot_note",
                help="スポットへの感想・メモ",
                height=100,
            )

            result["form_data"] = {
                "planId": plan_id,
                "userId": user_id,
                "spotId": spot_id,
                "spotNote": spot_note,
            }

            st.markdown("---")

            # ファイルアップロード
            st.markdown("**画像ファイル**")
            uploaded_files = st.file_uploader(
                "画像を選択してください（複数選択可）",
                type=["jpg", "jpeg", "png", "gif"],
                accept_multiple_files=True,
                key="file_uploader",
                help="複数の画像ファイルをアップロードできます",
            )

            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)}個のファイルが選択されました")
                for file in uploaded_files:
                    st.text(f"  • {file.name} ({file.size} bytes)")
                result["files"] = uploaded_files

            st.divider()

    # 実行ボタン
    execute_button = st.button(
        "🚀 リクエストを実行",
        type="primary",
        use_container_width=True,
        key="execute_button",
    )

    # 実行ボタンがクリックされたかどうかをresultに含める
    result["execute"] = execute_button

    return result


def validate_json_body(body_text: str) -> tuple[bool, dict | None, str | None]:
    """
    JSON文字列をパースしてバリデーションする

    Args:
        body_text: JSON文字列

    Returns:
        (is_valid, parsed_json, error_message)
        - is_valid: JSONが有効かどうか
        - parsed_json: パース済みのJSONデータ（無効な場合はNone）
        - error_message: エラーメッセージ（有効な場合はNone）

    Examples:
        >>> validate_json_body('{"key": "value"}')
        (True, {'key': 'value'}, None)

        >>> validate_json_body('invalid json')
        (False, None, 'Expecting value: line 1 column 1 (char 0)')
    """
    try:
        parsed = json.loads(body_text)
        return True, parsed, None
    except json.JSONDecodeError as e:
        return False, None, str(e)
