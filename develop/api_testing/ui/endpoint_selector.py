"""エンドポイント選択UI

サイドバーでエンドポイントを選択するコンポーネント。
"""

import streamlit as st
from models import EndpointDefinition


def render_endpoint_selector(
    endpoints: list[EndpointDefinition],
) -> EndpointDefinition | None:
    """
    エンドポイント選択UIを表示する

    エンドポイントをカテゴリ別にグループ化し、サイドバーに表示する。
    カテゴリ: 旅行計画、旅行ガイド、振り返り、スポット振り返り、ヘルスチェック

    Args:
        endpoints: エンドポイント定義のリスト

    Returns:
        EndpointDefinition | None: 選択されたエンドポイント定義、または None
    """
    # エンドポイントをカテゴリ別にグループ化
    categories = {
        "旅行計画": [],
        "旅行ガイド": [],
        "振り返り": [],
        "スポット振り返り": [],
        "ヘルスチェック": [],
    }

    # エンドポイントをカテゴリに分類
    for endpoint in endpoints:
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

    # サイドバーにエンドポイント選択UIを表示
    st.sidebar.header("📡 エンドポイント選択")

    # エンドポイントの選択肢を作成（カテゴリ別にグループ化して表示）
    all_options = []
    option_to_endpoint = {}
    
    for category, category_endpoints in categories.items():
        if not category_endpoints:
            continue
        
        # カテゴリ内のエンドポイントを選択肢に追加
        for endpoint in category_endpoints:
            # 表示用のラベルを作成（カテゴリ名を含める）
            label = f"[{category}] {endpoint.method} - {endpoint.name}"
            all_options.append(label)
            option_to_endpoint[label] = endpoint
    
    # セッションステートから現在の選択を取得
    current_selection = st.session_state.get("selected_endpoint_label", None)
    
    # 現在の選択のインデックスを取得
    index = 0
    if current_selection and current_selection in all_options:
        index = all_options.index(current_selection)
    
    # ラジオボタンで選択（全エンドポイントを1つのグループに）
    selected = st.sidebar.radio(
        label="エンドポイントを選択",
        options=all_options,
        index=index if current_selection else None,
        key="endpoint_selector",
        label_visibility="collapsed"
    )
    
    # 選択されたらセッションステートを更新
    if selected:
        st.session_state.selected_endpoint_label = selected
        return option_to_endpoint[selected]
    
    return None
