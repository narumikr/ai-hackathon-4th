# アンチパターンと回避方法

## はじめに

AI Agent設計において、よくある失敗パターン（アンチパターン）を理解することは、効果的なシステムを構築する上で重要である。このドキュメントでは、主要なアンチパターンとその回避方法を解説する。

## 1. アーキテクチャのミス

### アンチパターン1-1: 過度な複雑性

**問題**
シンプルなタスクに対して、不必要に複雑なマルチエージェントシステムを構築する。

**症状**
- 単純な質問にも10個以上のエージェント呼び出し
- デバッグに何時間もかかる
- コストとレイテンシが非常に高い
- 実測で効果が確認できない複雑性

**Before（過度な複雑性）**

```python
def answer_simple_question(question):
    # 不必要に複雑なワークフロー
    # ステップ1: メタ分析エージェント
    meta_analysis = meta_analyzer.analyze(question)

    # ステップ2: 複数の専門エージェントを並列実行
    expert_results = parallel_execute([
        linguistic_expert,
        semantic_expert,
        contextual_expert,
        pragmatic_expert
    ], meta_analysis)

    # ステップ3: 結果を統合
    integrated = integrator.integrate(expert_results)

    # ステップ4: 品質チェッカー
    quality_check = quality_checker.check(integrated)

    # ステップ5: 最適化エージェント
    if quality_check["score"] < 0.95:
        integrated = optimizer.optimize(integrated, quality_check)

    # ステップ6: 最終検証
    final_check = final_validator.validate(integrated)

    return integrated

# 問題点:
# - 「東京の天気は？」という質問にも上記の複雑なフローを実行
# - レイテンシ: 25秒、コスト: $0.80
# - 単一プロンプトと比較して精度は+2%のみ
```

**After（シンプリシティ優先）**

```python
def answer_simple_question(question):
    # シンプルな質問はシンプルに処理
    prompt = f"""
以下の質問に回答してください。

質問: {question}
"""
    answer = call_llm(prompt, tools=["search_web"])
    return answer

# 改善結果:
# - レイテンシ: 3秒（88%削減）
# - コスト: $0.02（97%削減）
# - 精度: 単純な質問では同等

# 複雑な質問のみ追加ステップを適用
def answer_complex_question(question):
    # まずシンプルに試す
    simple_answer = answer_simple_question(question)

    # 品質評価
    if needs_deeper_analysis(simple_answer):
        # 必要な場合のみ追加分析
        detailed_analysis = perform_detailed_analysis(question)
        return detailed_analysis

    return simple_answer
```

**回避方法**
- 常にシンプルなソリューションから始める
- 複雑性は実測で効果を確認してから追加
- 各ステップの必要性を検証
- 80/20ルール: 80%のケースはシンプルに、20%のみ複雑に

### アンチパターン1-2: 循環依存

**問題**
エージェント間で循環依存が発生し、無限ループやデッドロックを引き起こす。

**症状**
- エージェントAがエージェントBを呼び出し、BがAを呼び出す
- 処理が終了しない
- スタックオーバーフローエラー

**Before（循環依存）**

```python
def agent_a(task):
    # エージェントAの処理
    if requires_agent_b(task):
        return agent_b(task)  # BはAを呼び出す可能性
    return process_a(task)

def agent_b(task):
    # エージェントBの処理
    if requires_agent_a(task):
        return agent_a(task)  # AはBを呼び出す可能性
    return process_b(task)

# 問題点:
# - A → B → A → B → ... の無限ループ
# - 最大再帰深度エラー
```

**After（依存関係の明確化）**

```python
def orchestrator(task):
    # オーケストレーターが依存関係を管理
    plan = analyze_task(task)

    results = {}

    # エージェントを順序立てて実行（循環なし）
    if plan["needs_a"]:
        results["a"] = agent_a(task, context=results)

    if plan["needs_b"]:
        results["b"] = agent_b(task, context=results)

    # 結果を統合
    return integrate_results(results)

def agent_a(task, context):
    # エージェントAは他のエージェントを呼び出さない
    # 必要なコンテキストは引数で受け取る
    return process_a(task, context)

def agent_b(task, context):
    # エージェントBも他のエージェントを呼び出さない
    return process_b(task, context)
```

**回避方法**
- 依存関係を階層的に設計（一方向のみ）
- オーケストレーターパターンを使用
- 各エージェントは他のエージェントを直接呼び出さない
- 最大再帰深度を設定

## 2. エラー伝播の問題

### アンチパターン2-1: エラーの隠蔽

**問題**
エラーを適切に処理せず、エラー情報が失われる。

**症状**
- エラーが発生しても気づかない
- デバッグが極めて困難
- 不正確な出力が返される

**Before（エラーの隠蔽）**

```python
def process_with_tools(task):
    try:
        # ツールを使用
        result = call_tool("search", task)
        return result
    except Exception:
        # エラーを無視
        return "処理できませんでした"

# 問題点:
# - エラーの詳細が失われる
# - なぜ失敗したか不明
# - ログもない
```

**After（適切なエラーハンドリング）**

```python
import logging

logger = logging.getLogger(__name__)

def process_with_tools(task):
    try:
        result = call_tool("search", task)
        return {
            "success": True,
            "result": result
        }
    except ToolNotFoundError as e:
        logger.error(f"ツールが見つかりません: {e}")
        return {
            "success": False,
            "error": "指定されたツールは利用できません",
            "error_type": "TOOL_NOT_FOUND",
            "details": str(e)
        }
    except ToolTimeoutError as e:
        logger.error(f"ツールがタイムアウトしました: {e}")
        return {
            "success": False,
            "error": "処理がタイムアウトしました。後でもう一度お試しください",
            "error_type": "TIMEOUT",
            "details": str(e)
        }
    except Exception as e:
        logger.exception(f"予期しないエラー: {e}")
        return {
            "success": False,
            "error": "予期しないエラーが発生しました",
            "error_type": "UNKNOWN",
            "details": str(e)
        }
```

**回避方法**
- すべてのエラーをログに記録
- エラータイプを明確に分類
- ユーザーに分かりやすいメッセージを提供
- エラーの詳細を保持（デバッグ用）

### アンチパターン2-2: エラーの連鎖

**問題**
1つのエラーが次々と他のエラーを引き起こす。

**症状**
- 初期のエラーが後続のステップに伝播
- エラーメッセージが不明瞭
- 本当の原因が分からない

**Before（エラーの連鎖）**

```python
def multi_step_process(input_data):
    # ステップ1: データ検証（エラーチェックなし）
    validated = validate_data(input_data)

    # ステップ2: データ変換（validatedがNoneでもそのまま処理）
    transformed = transform_data(validated)

    # ステップ3: データ保存（transformedがNoneでもそのまま処理）
    saved = save_data(transformed)

    return saved

# 問題点:
# - ステップ1が失敗してもステップ2, 3が実行される
# - 各ステップで新しいエラーが発生
# - 本当の原因（ステップ1の失敗）が分からない
```

**After（早期失敗）**

```python
def multi_step_process(input_data):
    # ステップ1: データ検証
    validation_result = validate_data(input_data)
    if not validation_result["success"]:
        return {
            "success": False,
            "error": "データ検証に失敗しました",
            "step": "validation",
            "details": validation_result["error"]
        }

    # ステップ2: データ変換
    transformation_result = transform_data(validation_result["data"])
    if not transformation_result["success"]:
        return {
            "success": False,
            "error": "データ変換に失敗しました",
            "step": "transformation",
            "details": transformation_result["error"]
        }

    # ステップ3: データ保存
    save_result = save_data(transformation_result["data"])
    if not save_result["success"]:
        return {
            "success": False,
            "error": "データ保存に失敗しました",
            "step": "save",
            "details": save_result["error"]
        }

    return {
        "success": True,
        "data": save_result["data"]
    }
```

**回避方法**
- 早期失敗（Fail Fast）を実装
- 各ステップで出力を検証
- エラー発生時は即座に停止
- エラーの原因を明確に記録

## 3. プロンプト脆性

### アンチパターン3-1: 過度にハードコードされたプロンプト

**問題**
プロンプトが特定のケースに過度に最適化され、汎用性がない。

**症状**
- 少しでも入力が変わると動作しない
- 新しいユースケースごとにプロンプトを書き直す必要がある
- メンテナンスが困難

**Before（脆いプロンプト）**

```python
def classify_product(product_name):
    # 特定の商品名に依存したプロンプト
    prompt = f"""
以下の商品を分類してください。

商品名: {product_name}

カテゴリ:
- 「iPhone」「Galaxy」「Pixel」なら「スマートフォン」
- 「MacBook」「ThinkPad」「Surface」なら「ノートPC」
- 「AirPods」「WH-1000XM5」なら「イヤホン」
"""
    result = call_llm(prompt)
    return result

# 問題点:
# - 新しい商品名が出るたびにプロンプトを更新
# - スケールしない
# - メンテナンスが困難
```

**After（柔軟なプロンプト）**

```python
def classify_product(product_name, categories):
    # 汎用的なプロンプト
    categories_text = "\n".join([
        f"- {cat['name']}: {cat['description']}"
        for cat in categories
    ])

    prompt = f"""
以下の商品を適切なカテゴリに分類してください。

商品名: {product_name}

利用可能なカテゴリ:
{categories_text}

商品の特徴に基づいて最も適切なカテゴリを選択してください。
カテゴリ名のみを返してください。
"""
    result = call_llm(prompt)
    return result

# カテゴリ定義（データとして管理）
categories = [
    {
        "name": "スマートフォン",
        "description": "携帯電話、スマートデバイス"
    },
    {
        "name": "ノートPC",
        "description": "ラップトップコンピュータ"
    },
    {
        "name": "イヤホン",
        "description": "ヘッドフォン、イヤホン、オーディオ機器"
    }
]

result = classify_product("新しいスマホXYZ", categories)
```

**回避方法**
- プロンプトを汎用的に設計
- 固定値をデータとして外部化
- few-shot examplesを動的に生成
- テンプレート化して再利用

### アンチパターン3-2: 曖昧な指示

**問題**
プロンプトの指示が曖昧で、期待される出力が得られない。

**症状**
- 出力のフォーマットが一貫しない
- 必要な情報が含まれていない
- 解釈のブレが大きい

**Before（曖昧な指示）**

```python
def extract_info(text):
    prompt = f"""
以下のテキストから情報を抽出してください。

テキスト: {text}
"""
    result = call_llm(prompt)
    return result

# 問題点:
# - どの情報を抽出するか不明
# - フォーマットが指定されていない
# - 一貫性のない出力
```

**After（明確な指示）**

```python
def extract_info(text):
    prompt = f"""
以下のテキストから、指定された情報を抽出してください。

テキスト: {text}

抽出する情報:
1. 人名（すべて）
2. 組織名（すべて）
3. 日付（すべて）
4. 場所（すべて）

以下のJSON形式で出力してください:
{{
  "people": ["人名1", "人名2", ...],
  "organizations": ["組織名1", "組織名2", ...],
  "dates": ["日付1", "日付2", ...],
  "locations": ["場所1", "場所2", ...]
}}

情報が見つからない場合は、空の配列を返してください。
"""
    result = call_llm(prompt)
    return json.loads(result)
```

**回避方法**
- 具体的な指示を提供
- 出力フォーマットを明示
- 例を含める
- エッジケースの処理方法を指定

## 4. マルチエージェント調整の失敗

### アンチパターン4-1: エージェント間のコンテキスト喪失

**問題**
複数のエージェント間でコンテキストが適切に伝播されない。

**症状**
- 各エージェントが独立して動作し、全体の文脈を理解していない
- 重複した処理
- 一貫性のない出力

**Before（コンテキスト喪失）**

```python
def multi_agent_process(task):
    # エージェント1: データ収集
    data = data_collector.collect(task)

    # エージェント2: 分析（dataの詳細を知らない）
    analysis = analyzer.analyze(task)  # dataを渡していない

    # エージェント3: レポート生成（前のステップの詳細を知らない）
    report = reporter.generate(task)  # analysisを渡していない

    return report

# 問題点:
# - 各エージェントが独立して全タスクを実行
# - 重複した処理
# - 一貫性がない
```

**After（コンテキストの伝播）**

```python
def multi_agent_process(task):
    context = {"task": task}

    # エージェント1: データ収集
    data = data_collector.collect(context)
    context["collected_data"] = data

    # エージェント2: 分析（前のステップの結果を使用）
    analysis = analyzer.analyze(context)
    context["analysis"] = analysis

    # エージェント3: レポート生成（すべてのコンテキストを使用）
    report = reporter.generate(context)
    context["report"] = report

    return {
        "report": report,
        "context": context  # 全体のコンテキストも返す
    }
```

**回避方法**
- 共有コンテキストオブジェクトを使用
- 各エージェントに前のステップの結果を渡す
- オーケストレーターがコンテキストを管理
- コンテキストをログに記録

### アンチパターン4-2: 競合状態

**問題**
複数のエージェントが同時に同じリソースにアクセスし、競合が発生する。

**症状**
- データの不整合
- 予測不可能な動作
- 間欠的なエラー

**Before（競合状態）**

```python
async def parallel_update(items):
    # 複数のエージェントが同時にデータベースを更新
    tasks = [
        update_agent.update(item)
        for item in items
    ]
    results = await asyncio.gather(*tasks)
    return results

def update_agent(item):
    # 現在の値を読み取る
    current = database.get(item.id)

    # 値を更新
    new_value = calculate_new_value(current, item)

    # 保存（競合の可能性）
    database.set(item.id, new_value)

# 問題点:
# - Read-Modify-Writeの競合
# - 最後の書き込みが勝つ（他の更新が失われる）
```

**After（競合の解決）**

```python
import asyncio

# 方法1: ロックを使用
class ResourceLock:
    def __init__(self):
        self.locks = {}

    async def acquire(self, resource_id):
        if resource_id not in self.locks:
            self.locks[resource_id] = asyncio.Lock()
        await self.locks[resource_id].acquire()

    def release(self, resource_id):
        if resource_id in self.locks:
            self.locks[resource_id].release()

lock_manager = ResourceLock()

async def update_agent_safe(item):
    # リソースをロック
    await lock_manager.acquire(item.id)

    try:
        current = database.get(item.id)
        new_value = calculate_new_value(current, item)
        database.set(item.id, new_value)
    finally:
        # 必ずロックを解放
        lock_manager.release(item.id)

# 方法2: アトミックな操作を使用
def update_agent_atomic(item):
    # データベースのアトミックな更新機能を使用
    database.atomic_update(
        item.id,
        lambda current: calculate_new_value(current, item)
    )
```

**回避方法**
- ロック機構を使用
- アトミックな操作を使用
- 楽観的ロック（バージョン管理）
- タスクをシーケンシャルに実行（並列化しない）

## 5. 構造化出力の誤用

### アンチパターン5-1: 過度に厳格なスキーマ

**問題**
スキーマに過度な制約を設定し、LLMの柔軟性を損なう。

**症状**
- 生成失敗率が高い
- わずかな入力の変化で出力が生成できない
- 不自然に制約された出力

**Before（過度に厳格なスキーマ）**

```python
from pydantic import BaseModel, Field

class ProductDescription(BaseModel):
    """商品説明スキーマ（過度に厳格）"""

    # 問題: 文字数を厳格に制限
    title: str = Field(
        ...,
        min_length=50,
        max_length=60,
        description="商品タイトル（50-60文字）"
    )

    # 問題: 説明文も厳格に制限
    description: str = Field(
        ...,
        min_length=200,
        max_length=250,
        description="商品説明（200-250文字）"
    )

    # 問題: 固定数のキーワードを要求
    keywords: list[str] = Field(
        ...,
        min_length=5,
        max_length=5,
        description="キーワードは必ず5個"
    )

# 問題点:
# - 狭すぎる文字数制約により、自然な文章生成が困難
# - 商品によって適切な説明文の長さは異なる
# - キーワード数の固定化により、柔軟性が失われる
```

**After（柔軟なスキーマ）**

```python
from pydantic import BaseModel, Field

class ProductDescription(BaseModel):
    """商品説明スキーマ（柔軟）"""

    # 改善: 合理的な範囲を許容
    title: str = Field(
        ...,
        min_length=10,
        max_length=100,
        description="商品タイトル"
    )

    # 改善: 最小限の制約のみ
    description: str = Field(
        ...,
        min_length=50,
        description="商品説明"
    )

    # 改善: キーワード数に柔軟性を持たせる
    keywords: list[str] = Field(
        ...,
        min_length=3,
        max_length=10,
        description="商品キーワード（3-10個）"
    )
```

**回避方法**
- 必要最小限の制約のみ設定する
- 文字数制約は広い範囲を許容する
- LLMが自然な出力を生成できる余地を残す
- 制約は実際のビジネス要件に基づく

### アンチパターン5-2: スキーマの過剰な複雑化

**問題**
不必要に複雑なネスト構造やフィールドを定義し、メンテナンスとデバッグを困難にする。

**症状**
- スキーマ定義が数百行に及ぶ
- 深いネスト構造（5階層以上）
- 使用されないフィールドが多数存在

**Before（過剰な複雑化）**

```python
class Address(BaseModel):
    country: str
    state: str
    city: str
    postal_code: str
    street: str
    building: str
    floor: str
    room_number: str

class ContactInfo(BaseModel):
    email: str
    phone: str
    fax: str
    mobile: str
    emergency_contact: str
    emergency_phone: str

class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    nickname: str
    date_of_birth: str
    place_of_birth: str
    nationality: str
    contact_info: ContactInfo
    address: Address

class UserProfile(BaseModel):
    personal_info: PersonalInfo
    # さらに深くネストが続く...

# 問題点:
# - 7-8階層のネスト構造
# - ほとんどのユースケースで不要なフィールドを含む
# - スキーマの理解とメンテナンスが困難
```

**After（シンプルな構造）**

```python
class UserProfile(BaseModel):
    """ユーザープロフィール（必要最小限）"""

    name: str
    email: str
    location: str  # "Tokyo, Japan"のような簡潔な形式

    # 必要に応じてオプショナルフィールドを追加
    phone: str | None = None
    bio: str | None = None

# 改善結果:
# - フラットな構造で理解しやすい
# - 必須フィールドのみ定義
# - 拡張が容易
```

**回避方法**
- ネスト階層は3-4階層までに抑える
- 必須フィールドのみ定義する
- フラットな構造を優先する
- 実際のユースケースに基づいてスキーマを設計する

### アンチパターン5-3: バリデーションエラーの無視

**問題**
スキーマ生成やバリデーションのエラーを適切に処理せず、システムをクラッシュさせる。

**症状**
- 本番環境でのクラッシュ
- エラーの原因が不明
- ユーザーへの不適切なエラーメッセージ

**Before（エラーの無視）**

```python
async def generate_product_info(product_name: str):
    prompt = f"以下の商品の情報を生成してください: {product_name}"

    # エラーハンドリングなし
    result = await client.generate_content_with_schema(
        prompt,
        ProductInfo.model_json_schema()
    )

    # バリデーションなし
    return ProductInfo(**result)

# 問題点:
# - スキーマ生成失敗時にクラッシュ
# - JSONパースエラーがキャッチされない
# - バリデーションエラーが伝播する
```

**After（適切なエラーハンドリング）**

```python
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

async def generate_product_info(product_name: str):
    prompt = f"以下の商品の情報を生成してください: {product_name}"

    try:
        # スキーマ生成を試行
        result = await client.generate_content_with_schema(
            prompt,
            ProductInfo.model_json_schema()
        )

        # バリデーションを実行
        product_info = ProductInfo(**result)
        return {
            "success": True,
            "data": product_info
        }

    except ValidationError as e:
        # バリデーションエラーを記録
        logger.error(f"Validation error for product {product_name}: {e}")
        return {
            "success": False,
            "error": "生成されたデータが不正です",
            "error_type": "VALIDATION_ERROR",
            "details": str(e)
        }

    except json.JSONDecodeError as e:
        # JSONパースエラーを記録
        logger.error(f"JSON parse error for product {product_name}: {e}")
        return {
            "success": False,
            "error": "データのパースに失敗しました",
            "error_type": "PARSE_ERROR",
            "details": str(e)
        }

    except Exception as e:
        # その他のエラーを記録
        logger.exception(f"Unexpected error for product {product_name}: {e}")
        return {
            "success": False,
            "error": "予期しないエラーが発生しました",
            "error_type": "UNKNOWN",
            "details": str(e)
        }
```

**回避方法**
- すべてのバリデーションエラーをキャッチする
- エラーの詳細をログに記録する
- ユーザーに分かりやすいエラーメッセージを提供する
- グレースフルデグラデーション戦略を実装する
- リトライ戦略を検討する

## まとめ

### アンチパターンの回避原則

1. **シンプリシティ優先**: 過度な複雑性を避ける
2. **早期失敗**: エラーは即座に検出し、処理する
3. **明確な指示**: プロンプトは具体的で曖昧さをなくす
4. **適切なコンテキスト管理**: エージェント間でコンテキストを伝播
5. **競合の防止**: 共有リソースへのアクセスを制御
6. **柔軟なスキーマ設計**: 構造化出力では必要最小限の制約に留める

### チェックリスト

**アーキテクチャ**
- [ ] 複雑性は実測で効果を確認したか？
- [ ] 循環依存はないか？
- [ ] 依存関係は明確か？

**エラーハンドリング**
- [ ] すべてのエラーをログに記録しているか？
- [ ] 早期失敗を実装しているか？
- [ ] エラーメッセージは明確か？

**プロンプト**
- [ ] プロンプトは汎用的か？
- [ ] 指示は明確か？
- [ ] 出力フォーマットを指定しているか？

**マルチエージェント**
- [ ] コンテキストは適切に伝播されているか？
- [ ] 競合状態はないか？
- [ ] エージェント間の調整は適切か？

**構造化出力**
- [ ] スキーマ制約は必要最小限か？
- [ ] ネスト階層は3-4階層以内か？
- [ ] バリデーションエラーのハンドリングを実装したか？
- [ ] LLMの柔軟性を損なっていないか？

### 次のステップ

- 本番運用のベストプラクティス: [production-best-practices.md](production-best-practices.md)
- ワークフローパターンの詳細: [workflow-patterns-detail.md](workflow-patterns-detail.md)
- 評価とテスト戦略: [evaluation-testing.md](evaluation-testing.md)
