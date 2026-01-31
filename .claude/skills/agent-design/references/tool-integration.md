# ツール統合のベストプラクティス

## はじめに

AI Agentの能力を拡張する上で、外部ツールとの統合は不可欠である。このドキュメントでは、ツールの選択、設計、最適化、エラーハンドリングのベストプラクティスを解説する。

## ツールの選択基準

### 1. 必要性の評価

ツールを追加する前に、本当に必要かを検証する。

**判断基準:**
- LLMの知識だけでは解決できないタスクか？
- リアルタイムデータが必要か？
- 外部システムとの連携が必要か？
- 計算処理や複雑なロジックが必要か？

**例:**
```python
# 不要なツール
def get_current_year():
    """現在の年を取得（LLMの知識で十分）"""
    pass

# 必要なツール
def get_stock_price(symbol):
    """リアルタイムの株価を取得（外部データが必要）"""
    pass
```

### 2. ツールの粒度

ツールの粒度は、タスクに応じて適切に設定する。

**細粒度ツール（推奨）:**
- 単一の明確な機能
- 再利用性が高い
- デバッグが容易

**粗粒度ツール（避ける）:**
- 複数の機能を含む
- 再利用性が低い
- デバッグが困難

```python
# 良い例: 細粒度
def search_web(query: str) -> List[str]:
    """Web検索を実行"""
    pass

def fetch_url(url: str) -> str:
    """URLのコンテンツを取得"""
    pass

# 悪い例: 粗粒度
def research_topic(topic: str) -> str:
    """トピックを調査（検索、取得、分析をすべて含む）"""
    pass
```

### 3. ツール数の最適化

提供するツール数は最小限に抑える。

**理由:**
- ツールの説明がプロンプトのトークン数を増やす
- ツール数が多いと選択精度が低下
- コストとレイテンシが増加

**推奨:**
- タスクごとに必要なツールのみ提供
- ツール数は5-10が適切
- 汎用的なツールより特化したツールを優先

## ツールの設計

### 1. 明確な説明

ツールの説明は、LLMが適切に使用できるよう明確にする。

```python
# 良い例: 明確な説明
{
    "name": "get_weather",
    "description": "指定された都市の現在の天気情報を取得します。都市名は日本語または英語で指定できます。",
    "parameters": {
        "city": {
            "type": "string",
            "description": "天気情報を取得する都市名（例: 東京、Tokyo）"
        }
    }
}

# 悪い例: 曖昧な説明
{
    "name": "get_weather",
    "description": "天気を取得",  # 不十分
    "parameters": {
        "city": {
            "type": "string",
            "description": "都市"  # 不十分
        }
    }
}
```

### 2. パラメータの型と制約

パラメータの型と制約を明確に定義する。

```python
{
    "name": "search_products",
    "description": "製品データベースから製品を検索します。",
    "parameters": {
        "query": {
            "type": "string",
            "description": "検索クエリ"
        },
        "category": {
            "type": "string",
            "enum": ["electronics", "clothing", "books", "food"],
            "description": "製品カテゴリ（省略可）"
        },
        "max_results": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "default": 10,
            "description": "返す結果の最大数（デフォルト: 10）"
        }
    },
    "required": ["query"]
}
```

### 3. エラーの明確な報告

ツールは、エラーを明確に報告する。

```python
def get_user_info(user_id: str) -> Dict:
    """ユーザー情報を取得"""
    try:
        user = database.get_user(user_id)
        if user is None:
            return {
                "success": False,
                "error": f"ユーザーID '{user_id}' が見つかりません。",
                "error_type": "NOT_FOUND"
            }
        return {
            "success": True,
            "data": user
        }
    except DatabaseConnectionError as e:
        return {
            "success": False,
            "error": "データベースに接続できません。後でもう一度お試しください。",
            "error_type": "CONNECTION_ERROR"
        }
```

## ツール使用の最適化

### 1. ツール呼び出しの順序

ツール呼び出しの順序を最適化し、不要な呼び出しを避ける。

#### Before（非効率な順序）

```python
# 悪い例: 不要なツール呼び出し
def get_product_details(product_name):
    # すべての製品を取得（コストが高い）
    all_products = list_all_products()

    # 該当する製品を検索
    product = find_product(all_products, product_name)

    if product:
        # 詳細を取得
        details = get_product_details_by_id(product.id)
        return details
    else:
        return None
```

#### After（効率的な順序）

```python
# 良い例: 直接検索
def get_product_details(product_name):
    # 製品名で直接検索（効率的）
    product = search_product_by_name(product_name)

    if product:
        return product
    else:
        return None
```

### 2. ツール呼び出しのバッチ化

複数の類似したツール呼び出しをバッチ化する。

#### Before（個別呼び出し）

```python
# 非効率: 個別にツールを呼び出し
def get_multiple_users(user_ids):
    users = []
    for user_id in user_ids:  # 10個のユーザーID
        user = get_user(user_id)  # 10回のツール呼び出し
        users.append(user)
    return users
```

#### After（バッチ呼び出し）

```python
# 効率的: バッチでツールを呼び出し
def get_multiple_users(user_ids):
    users = get_users_batch(user_ids)  # 1回のツール呼び出し
    return users
```

### 3. キャッシュの活用

同じツール呼び出しの結果をキャッシュする。

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_exchange_rate(from_currency, to_currency):
    """為替レートを取得（キャッシュ付き）"""
    # 外部APIを呼び出し
    rate = fetch_exchange_rate_from_api(from_currency, to_currency)
    return rate

# 同じパラメータでの呼び出しはキャッシュから返される
rate1 = get_exchange_rate("USD", "JPY")  # API呼び出し
rate2 = get_exchange_rate("USD", "JPY")  # キャッシュから返す
```

### 4. タイムアウトの設定

ツール呼び出しにタイムアウトを設定する。

```python
import requests

def fetch_url(url: str, timeout: int = 10) -> str:
    """URLのコンテンツを取得（タイムアウト付き）"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.Timeout:
        return {
            "success": False,
            "error": f"タイムアウト: {timeout}秒以内に応答がありませんでした。"
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"リクエストエラー: {str(e)}"
        }
```

## エラーハンドリング

### 1. グレースフルデグラデーション

ツールが失敗しても、システム全体が停止しないようにする。

```python
def analyze_with_external_data(topic):
    # 外部データの取得を試みる
    external_data = fetch_external_data(topic)

    if external_data.get("success"):
        # 外部データがある場合は使用
        analysis = analyze_with_data(topic, external_data["data"])
    else:
        # 外部データがない場合は、LLMの知識のみで分析
        analysis = analyze_without_data(topic)
        # ユーザーに通知
        analysis["note"] = "外部データの取得に失敗しました。LLMの知識のみで分析しています。"

    return analysis
```

### 2. リトライ戦略

一時的なエラーに対してリトライを実装する。

```python
import time

def fetch_data_with_retry(url, max_retries=3, backoff_factor=2):
    """リトライ戦略付きのデータ取得"""
    for attempt in range(max_retries):
        try:
            data = fetch_url(url)
            return {"success": True, "data": data}
        except TemporaryError as e:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                time.sleep(wait_time)
                continue
            else:
                return {
                    "success": False,
                    "error": f"最大リトライ回数({max_retries})に達しました。"
                }
        except PermanentError as e:
            # 永続的なエラーはリトライしない
            return {"success": False, "error": str(e)}
```

### 3. フォールバック

ツールが失敗した場合の代替手段を用意する。

```python
def get_product_info(product_id):
    # プライマリデータソース
    info = fetch_from_primary_db(product_id)

    if info.get("success"):
        return info

    # フォールバック: セカンダリデータソース
    info = fetch_from_secondary_db(product_id)

    if info.get("success"):
        return info

    # フォールバック: キャッシュ
    info = fetch_from_cache(product_id)

    if info.get("success"):
        info["note"] = "キャッシュから取得しました。最新のデータではない可能性があります。"
        return info

    # すべて失敗
    return {
        "success": False,
        "error": "製品情報を取得できませんでした。"
    }
```

### 4. ユーザーへのエラー通知

エラーを適切にユーザーに伝える。

```python
def process_user_request(request):
    # ツールを使用
    result = call_external_api(request)

    if not result.get("success"):
        error_type = result.get("error_type")

        # エラータイプに応じたメッセージ
        if error_type == "RATE_LIMIT":
            message = "申し訳ございません。現在、リクエストが集中しています。しばらくしてから再度お試しください。"
        elif error_type == "NOT_FOUND":
            message = f"'{request}'に関する情報が見つかりませんでした。別のキーワードでお試しください。"
        elif error_type == "PERMISSION_DENIED":
            message = "この操作を実行する権限がありません。"
        else:
            message = "申し訳ございません。処理中にエラーが発生しました。後でもう一度お試しください。"

        return {"error": message}

    return result
```

## ツールチェーンの設計

### 1. シーケンシャルなツールチェーン

ツールを順序立てて呼び出す。

```python
def research_and_summarize(topic):
    # ステップ1: Web検索
    search_results = search_web(topic)

    if not search_results.get("success"):
        return handle_error(search_results)

    # ステップ2: 各URLのコンテンツを取得
    contents = []
    for url in search_results["urls"][:5]:  # 上位5件
        content = fetch_url(url)
        if content.get("success"):
            contents.append(content["data"])

    # ステップ3: コンテンツを要約
    summary_prompt = f"""
以下のコンテンツを要約してください:

{contents}
"""
    summary = call_llm(summary_prompt)

    return summary
```

### 2. 条件付きツールチェーン

条件に応じてツールを呼び出す。

```python
def answer_question(question):
    # ステップ1: 質問を分析
    analysis = analyze_question(question)

    # ステップ2: 分析結果に基づいてツールを選択
    if analysis["requires_realtime_data"]:
        # リアルタイムデータが必要
        data = fetch_realtime_data(analysis["topic"])
    elif analysis["requires_calculation"]:
        # 計算が必要
        data = perform_calculation(analysis["expression"])
    elif analysis["requires_search"]:
        # 検索が必要
        data = search_web(analysis["query"])
    else:
        # LLMの知識のみで回答
        data = None

    # ステップ3: 回答生成
    answer = generate_answer(question, data)

    return answer
```

### 3. 並列ツールチェーン

複数のツールを並列実行する。

```python
import asyncio

async def comprehensive_research(topic):
    # 複数のソースから並列でデータを収集
    tasks = [
        search_academic_papers(topic),
        search_news_articles(topic),
        search_social_media(topic),
        search_government_data(topic)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 結果を統合
    valid_results = []
    for result in results:
        if isinstance(result, Exception):
            # エラーはログに記録し、スキップ
            logger.error(f"ツール呼び出しエラー: {result}")
        elif result.get("success"):
            valid_results.append(result["data"])

    # 統合レポート生成
    report = integrate_research_results(valid_results)

    return report
```

## Before/After例

### 例1: ツールの説明を改善

#### Before（曖昧な説明）

```python
tools = [
    {
        "name": "search",
        "description": "検索する",
        "parameters": {
            "q": {"type": "string"}
        }
    }
]

# 問題点:
# - 何を検索するのか不明
# - パラメータ名が不明瞭（"q"）
# - パラメータの説明がない
# - LLMが適切に使用できない
```

#### After（明確な説明）

```python
tools = [
    {
        "name": "search_web",
        "description": "Webを検索して関連する情報を取得します。最新の情報やリアルタイムデータが必要な場合に使用してください。",
        "parameters": {
            "query": {
                "type": "string",
                "description": "検索クエリ。キーワードまたは質問形式で指定できます。"
            },
            "max_results": {
                "type": "integer",
                "description": "返す検索結果の最大数（デフォルト: 10、最大: 100）",
                "default": 10,
                "minimum": 1,
                "maximum": 100
            }
        },
        "required": ["query"]
    }
]

# 改善ポイント:
# - ツールの目的が明確
# - パラメータ名が分かりやすい
# - パラメータの説明が詳細
# - 制約が明示されている
```

### 例2: エラーハンドリングを改善

#### Before（不十分なエラーハンドリング）

```python
def get_stock_price(symbol):
    # エラーハンドリングなし
    data = fetch_from_api(symbol)
    return data["price"]

# 問題点:
# - APIエラー時にクラッシュ
# - データがない場合の処理なし
# - ユーザーへのエラー通知なし
```

#### After（適切なエラーハンドリング）

```python
def get_stock_price(symbol):
    try:
        data = fetch_from_api(symbol, timeout=5)

        if not data.get("success"):
            return {
                "success": False,
                "error": f"株価情報を取得できませんでした: {data.get('error')}",
                "symbol": symbol
            }

        if "price" not in data:
            return {
                "success": False,
                "error": f"株価データが不完全です（シンボル: {symbol}）",
                "symbol": symbol
            }

        return {
            "success": True,
            "symbol": symbol,
            "price": data["price"],
            "currency": data.get("currency", "USD"),
            "timestamp": data.get("timestamp")
        }

    except TimeoutError:
        return {
            "success": False,
            "error": "APIのタイムアウト: 応答がありませんでした。",
            "symbol": symbol
        }
    except Exception as e:
        logger.error(f"株価取得エラー: {e}")
        return {
            "success": False,
            "error": "予期しないエラーが発生しました。",
            "symbol": symbol
        }

# 改善ポイント:
# - すべてのエラーケースを処理
# - 一貫した戻り値の形式
# - ユーザーに分かりやすいエラーメッセージ
# - ログ記録
```

### 例3: ツール数を最適化

#### Before（過剰なツール）

```python
# すべてのタスクにすべてのツールを提供
tools = [
    "search_web",
    "fetch_url",
    "get_weather",
    "get_stock_price",
    "calculate",
    "translate",
    "send_email",
    "create_calendar_event",
    "get_news",
    "search_database",
    "run_code",
    "generate_image"
]  # 12個のツール

# 問題点:
# - ツールの説明がプロンプトを肥大化
# - ツール選択の精度が低下
# - コストとレイテンシが増加
```

#### After（タスクに応じたツール）

```python
# タスクに応じて必要なツールのみ提供

# 質問応答タスク
qa_tools = ["search_web", "fetch_url", "calculate"]

# 天気予報タスク
weather_tools = ["get_weather"]

# 株価照会タスク
stock_tools = ["get_stock_price", "calculate"]

# タスクに応じてツールを選択
def get_tools_for_task(task_type):
    tool_map = {
        "qa": qa_tools,
        "weather": weather_tools,
        "stock": stock_tools
    }
    return tool_map.get(task_type, [])

# 改善ポイント:
# - ツール数を最小化（3個以下）
# - タスクに特化したツールセット
# - プロンプトのトークン数削減
# - ツール選択の精度向上
```

## まとめ

### ツール統合のベストプラクティス

1. **必要性の評価**: 本当に必要なツールのみ追加
2. **明確な設計**: ツールの説明とパラメータを明確に定義
3. **最適化**: ツール呼び出しの順序、バッチ化、キャッシュを活用
4. **エラーハンドリング**: グレースフルデグラデーション、リトライ、フォールバック
5. **ツールチェーン**: シーケンシャル、条件付き、並列の適切な組み合わせ

### チェックリスト

**ツール設計**
- [ ] ツールの説明は明確か？
- [ ] パラメータの型と制約が定義されているか？
- [ ] エラーを明確に報告しているか？

**ツール使用**
- [ ] 必要なツールのみ提供しているか？
- [ ] ツール呼び出しの順序は最適か？
- [ ] バッチ化やキャッシュを活用しているか？
- [ ] タイムアウトを設定しているか？

**エラーハンドリング**
- [ ] グレースフルデグラデーションを実装しているか？
- [ ] リトライ戦略を定義しているか？
- [ ] フォールバックを用意しているか？
- [ ] ユーザーに分かりやすいエラーメッセージを提供しているか？

### 次のステップ

- 評価とテスト戦略: [evaluation-testing.md](evaluation-testing.md)
- アンチパターンの回避: [anti-patterns.md](anti-patterns.md)
- 本番運用のベストプラクティス: [production-best-practices.md](production-best-practices.md)
