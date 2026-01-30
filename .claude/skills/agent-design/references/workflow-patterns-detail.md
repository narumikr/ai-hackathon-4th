# ワークフローパターン詳細ガイド

## はじめに

このドキュメントでは、AI Agent設計における5つの主要なワークフローパターンの詳細を解説する。各パターンの理論、実装方法、ユースケース、パラメータ設定を段階的に説明する。

## パターン選択ガイド（クイックリファレンス）

| パターン | 主な使用場面 | 複雑度 | レイテンシ | コスト |
|---------|------------|--------|----------|--------|
| プロンプト連鎖 | 明確なステップ、順序依存 | 低 | 中 | 中 |
| ルーティング | 入力タイプが多様 | 低 | 低 | 低〜中 |
| 並列化 | 独立したサブタスク | 低 | 低 | 中〜高 |
| オーケストレーター・ワーカー | 動的ワークフロー | 高 | 高 | 高 |
| 評価者・最適化者 | 反復的改善 | 中 | 高 | 高 |

## 1. プロンプト連鎖（Prompt Chaining）

### 概要

プロンプト連鎖は、複雑なタスクを順序立てた複数のステップに分解し、各ステップの出力を次のステップの入力として使用するパターンである。最もシンプルで理解しやすく、デバッグが容易である。

### 実装パターン

```python
# 基本的なプロンプト連鎖の実装

def prompt_chaining(user_input):
    # ステップ1: 入力の分析
    analysis_prompt = f"""
以下のユーザー入力を分析し、必要な情報を特定してください。

ユーザー入力: {user_input}

必要な情報をJSON形式で出力してください。
"""
    analysis_result = call_llm(analysis_prompt)

    # ステップ2: 情報の収集
    collection_prompt = f"""
以下の情報を収集してください。

必要な情報: {analysis_result}

各情報について、関連するデータを検索ツールで取得してください。
"""
    collected_data = call_llm(collection_prompt, tools=["search"])

    # ステップ3: 最終回答の生成
    answer_prompt = f"""
以下の情報を基に、ユーザーの質問に回答してください。

ユーザーの質問: {user_input}
収集したデータ: {collected_data}

明確で簡潔な回答を提供してください。
"""
    final_answer = call_llm(answer_prompt)

    return final_answer
```

### パラメータ設定

**ステップ数の決定**
- 最小限のステップから開始する（2-3ステップ）
- 各ステップが明確な目的を持つようにする
- ステップ数が5を超える場合は、他のパターンを検討する

**コンテキスト伝播**
- 各ステップに必要な情報のみを渡す
- 不要な情報を含めるとトークン消費が増加する
- 前のステップの出力全体ではなく、関連部分のみを抽出する

**エラーハンドリング**
- 各ステップで出力を検証する
- 期待される形式でない場合は再試行またはユーザーに通知
- 早期失敗を実装する

### ユースケース

**コンテンツ生成ワークフロー**
1. トピックの研究と情報収集
2. アウトラインの作成
3. 各セクションの執筆
4. 編集とリファインメント

**データ分析パイプライン**
1. データの前処理と検証
2. 統計分析の実行
3. インサイトの抽出
4. レポートの生成

**コード生成とレビュー**
1. 要件の理解と仕様の明確化
2. コードの生成
3. テストケースの作成
4. コードレビューと改善提案

### Before/After例

#### Before（単一プロンプトの問題）

```
プロンプト:
「Pythonでファイル処理を行うコードを書いてください。
要件を分析し、コードを生成し、テストも書いてください。」

問題点:
- すべてを一度に処理するため、各ステップの品質が低下
- 中間ステップの確認ができない
- エラーが発生した際にどのステップが問題か不明
- 改善の反復が困難
```

#### After（プロンプト連鎖の適用）

```
ステップ1: 要件分析
プロンプト: 「以下の要件を分析し、必要な機能をリスト化してください」
出力: 機能リスト

ステップ2: コード生成
プロンプト: 「以下の機能リストに基づいてコードを生成してください: {機能リスト}」
出力: コード

ステップ3: テスト生成
プロンプト: 「以下のコードのテストを書いてください: {コード}」
出力: テストコード

改善ポイント:
- 各ステップを独立して改善できる
- 中間結果を確認し、必要に応じて修正できる
- デバッグが容易
- 段階的に品質を向上できる
```

## 2. ルーティング（Routing）

### 概要

ルーティングは、入力を分類し、それぞれに特化したプロンプトやワークフローに振り分けるパターンである。異なるタイプの入力に対して最適化された処理を適用できる。

### 実装パターン

```python
# 基本的なルーティングの実装

def routing_pattern(user_input):
    # ルーター: 入力タイプを分類
    router_prompt = f"""
以下のユーザー入力を分類してください。

ユーザー入力: {user_input}

分類カテゴリ:
- "technical_question": 技術的な質問
- "billing_inquiry": 請求に関する問い合わせ
- "feature_request": 機能リクエスト
- "general_inquiry": 一般的な問い合わせ

カテゴリ名のみを返してください。
"""
    category = call_llm(router_prompt)

    # カテゴリに応じた処理
    if category == "technical_question":
        return handle_technical_question(user_input)
    elif category == "billing_inquiry":
        return handle_billing_inquiry(user_input)
    elif category == "feature_request":
        return handle_feature_request(user_input)
    else:
        return handle_general_inquiry(user_input)

def handle_technical_question(user_input):
    # 技術的な質問に特化したプロンプト
    prompt = f"""
あなたは技術サポート専門のアシスタントです。
以下の技術的な質問に、詳細なコード例を含めて回答してください。

質問: {user_input}
"""
    return call_llm(prompt, temperature=0.2)  # 正確性重視

def handle_billing_inquiry(user_input):
    # 請求に特化したプロンプト（ツール使用）
    prompt = f"""
請求情報を取得し、ユーザーの問い合わせに回答してください。

問い合わせ: {user_input}
"""
    return call_llm(prompt, tools=["get_billing_info", "update_billing"])

def handle_feature_request(user_input):
    # 機能リクエストに特化したプロンプト
    prompt = f"""
以下の機能リクエストを分析し、実現可能性と優先度を評価してください。

リクエスト: {user_input}
"""
    return call_llm(prompt, temperature=0.5)  # 創造性と正確性のバランス
```

### パラメータ設定

**ルーターの設計**
- カテゴリ数は3-7が適切（多すぎると分類精度が低下）
- カテゴリの定義を明確にする
- 境界が曖昧なカテゴリは避ける
- "その他"カテゴリを用意する

**モデル選択**
- ルーター: 軽量なモデル（Haiku）で十分な場合が多い
- 各ハンドラー: タスクの複雑性に応じて選択
- コスト最適化のため、シンプルなタスクには軽量モデルを使用

**フォールバック戦略**
- 分類に失敗した場合のデフォルト処理を定義
- 確信度が低い場合は、ユーザーに選択を促す
- 誤分類をログに記録し、ルーターを改善

### ユースケース

**カスタマーサポート**
- 技術サポート vs 請求問い合わせ vs 一般的な質問
- 各タイプに特化したプロンプトとツール

**コンテンツ処理**
- テキスト vs 画像 vs コード
- メディアタイプに応じた処理パイプライン

**言語ルーティング**
- 入力言語の検出
- 言語ごとに最適化されたプロンプト

**複雑度ベースのルーティング**
- シンプルな質問 → 軽量モデル
- 複雑な質問 → 高性能モデル

### Before/After例

#### Before（単一プロンプトの問題）

```
プロンプト:
「カスタマーサポートアシスタントとして、以下の問い合わせに回答してください: {user_input}」

問題点:
- すべてのタイプの問い合わせに同じプロンプトを使用
- 技術的な質問と請求問い合わせで異なるツールが必要だが、常にすべてのツールを提供
- 各タイプに最適化されていないため、回答品質が低下
- コストが高い（不要なツールの記述を常に含む）
```

#### After（ルーティングの適用）

```
ステップ1: ルーター
プロンプト: 「問い合わせを分類してください: {user_input}」
出力: "technical_question"

ステップ2: 技術サポートハンドラー
プロンプト: 「技術サポート専門として回答してください」
ツール: ["search_docs", "run_code"]
温度: 0.2（正確性重視）

改善ポイント:
- 各タイプに特化したプロンプトで品質向上
- 必要なツールのみ提供してコスト削減
- モデルパラメータを最適化
- シンプルな問い合わせには軽量モデルを使用してコスト削減
```

## 3. 並列化（Parallelization）

### 概要

並列化は、独立した複数のタスクを同時実行し、結果を統合するパターンである。レイテンシの大幅な削減が可能である。

### 実装パターン

```python
# 基本的な並列化の実装

import asyncio

async def parallelization_pattern(documents):
    # 独立したタスクを並列実行
    tasks = []
    for doc in documents:
        task = asyncio.create_task(summarize_document(doc))
        tasks.append(task)

    # すべてのタスクの完了を待つ
    summaries = await asyncio.gather(*tasks)

    # 結果を統合
    integration_prompt = f"""
以下の要約を統合し、包括的なレポートを生成してください。

要約:
{format_summaries(summaries)}

レポートには、共通テーマ、主要なインサイト、推奨事項を含めてください。
"""
    final_report = await call_llm_async(integration_prompt)

    return final_report

async def summarize_document(document):
    prompt = f"""
以下のドキュメントを要約してください。

ドキュメント: {document}

主要なポイントを3-5個の箇条書きで提供してください。
"""
    return await call_llm_async(prompt)
```

### パラメータ設定

**並列度の決定**
- 同時実行数の上限を設定（レート制限を考慮）
- 一般的には5-10タスクが適切
- バッチ処理で大量のタスクを処理する場合は、チャンク化

**タイムアウト管理**
- 各タスクにタイムアウトを設定
- 遅延タスクのハンドリング戦略を定義
- 全体のタイムアウトも設定

**エラーハンドリング**
- 部分的な失敗を許容するか決定
- 失敗したタスクの再試行戦略
- 最小成功数の閾値を設定

**結果の統合**
- タスク数が多い場合、階層的な統合を検討
- 統合プロンプトに含める情報量を調整

### ユースケース

**複数ドキュメントの分析**
- 各ドキュメントを並列で要約
- 結果を統合して包括的なレポート生成

**多面的な調査**
- 複数の情報源を同時に検索
- 各検索結果を並列で分析

**A/Bテスト生成**
- 複数のバリエーションを同時生成
- ユーザーが最適なものを選択

**マルチモーダル処理**
- テキスト、画像、音声を並列で処理
- 結果を統合して総合的な分析

### Before/After例

#### Before（シーケンシャル実行の問題）

```
def process_documents_sequential(documents):
    summaries = []
    for doc in documents:  # 5つのドキュメント
        summary = summarize_document(doc)  # 各3秒
        summaries.append(summary)
    # 合計: 15秒
    return integrate_summaries(summaries)

問題点:
- 各ドキュメントを順次処理するため、時間がかかる
- 5つのドキュメントで15秒（各3秒 × 5）
- スケールしない（ドキュメントが増えると線形に時間増加）
```

#### After（並列化の適用）

```
async def process_documents_parallel(documents):
    tasks = [summarize_document(doc) for doc in documents]  # 5つのタスク
    summaries = await asyncio.gather(*tasks)  # 並列実行
    # 合計: 3秒（最長タスクの時間）
    return await integrate_summaries(summaries)

改善ポイント:
- レイテンシが15秒から3秒に削減（80%削減）
- スループット向上（同時に5つのドキュメントを処理）
- ユーザー体験の大幅な改善
- コストは変わらない（同じ数のLLM呼び出し）
```

## 4. オーケストレーター・ワーカー（Orchestrator-Workers）

### 概要

オーケストレーター・ワーカーは、中央のLLM（オーケストレーター）がタスクを動的に分解し、専用のワーカーエージェントに委譲するパターンである。複雑で予測困難なワークフローに対応できる。

### 実装パターン

```python
# オーケストレーター・ワーカーの実装

def orchestrator_worker_pattern(user_task):
    # オーケストレーター: タスクを分析し、計画を立てる
    orchestrator_prompt = f"""
あなたはタスクオーケストレーターです。以下のタスクを分析し、実行計画を立ててください。

タスク: {user_task}

利用可能なワーカー:
- data_collector: データ収集と検索
- data_analyzer: データ分析と統計処理
- report_generator: レポートとドキュメントの生成
- code_executor: コードの実行とテスト

実行計画をJSON形式で出力してください:
{{
  "steps": [
    {{"worker": "worker_name", "task": "具体的なタスク内容"}},
    ...
  ]
}}
"""
    plan = call_llm(orchestrator_prompt)

    # 各ステップを実行
    results = []
    for step in plan["steps"]:
        worker = step["worker"]
        task = step["task"]
        result = execute_worker(worker, task, results)
        results.append(result)

    # 結果を統合
    integration_prompt = f"""
以下のワーカーの実行結果を統合し、最終回答を生成してください。

実行計画: {plan}
実行結果: {results}

ユーザーのタスク: {user_task}
"""
    final_answer = call_llm(integration_prompt)

    return final_answer

def execute_worker(worker_name, task, previous_results):
    # ワーカー固有のプロンプトとツール
    worker_configs = {
        "data_collector": {
            "prompt": "データ収集専門のアシスタントとして、以下のタスクを実行してください",
            "tools": ["search", "fetch_url"],
            "temperature": 0.3
        },
        "data_analyzer": {
            "prompt": "データ分析専門家として、以下のタスクを実行してください",
            "tools": ["run_code", "calculate"],
            "temperature": 0.2
        },
        "report_generator": {
            "prompt": "レポート生成専門のライターとして、以下のタスクを作成してください",
            "tools": [],
            "temperature": 0.7
        },
        "code_executor": {
            "prompt": "コード実行環境として、以下のタスクを実行してください",
            "tools": ["run_code", "install_package"],
            "temperature": 0.1
        }
    }

    config = worker_configs[worker_name]
    worker_prompt = f"""
{config["prompt"]}

タスク: {task}
前のステップの結果: {previous_results}
"""

    return call_llm(
        worker_prompt,
        tools=config["tools"],
        temperature=config["temperature"]
    )
```

### パラメータ設定

**オーケストレーターの設計**
- 高性能モデルを使用（Sonnet以上）
- thinking tagsを使用して計画プロセスを明示
- 計画の再評価を可能にする（必要に応じて計画を修正）

**ワーカーの専門化**
- 各ワーカーに明確な役割を定義
- 役割に応じたツールとパラメータを設定
- ワーカー数は3-7が適切

**動的な計画調整**
- ワーカーの結果に基づいて計画を修正できるようにする
- 最大ステップ数を設定して無限ループを防ぐ
- 早期終了条件を定義

### ユースケース

**複雑な調査タスク**
- オーケストレーターが調査戦略を立案
- データ収集ワーカーが情報を収集
- 分析ワーカーがデータを処理
- レポートワーカーが結果をまとめる

**エンドツーエンドのデータパイプライン**
- データ取得 → 前処理 → 分析 → 可視化
- 各ステップに専門ワーカーを配置

**動的なタスク自動化**
- ユーザーの要求に応じてワークフローを生成
- 必要なツールを動的に選択

### Before/After例

#### Before（固定ワークフローの問題）

```
def fixed_workflow(user_task):
    # 常に同じステップを実行
    data = collect_data()
    analysis = analyze_data(data)
    report = generate_report(analysis)
    return report

問題点:
- すべてのタスクに同じワークフローを適用
- タスクによっては不要なステップを実行
- 新しいタイプのタスクに対応できない
- 柔軟性がない
```

#### After（オーケストレーター・ワーカーの適用）

```
def orchestrator_workflow(user_task):
    # オーケストレーターが動的に計画を立てる
    plan = orchestrator.create_plan(user_task)

    # 計画例（シンプルなタスク）:
    # [{"worker": "data_collector", "task": "情報収集"},
    #  {"worker": "report_generator", "task": "レポート生成"}]

    # 計画例（複雑なタスク）:
    # [{"worker": "data_collector", "task": "複数ソースから収集"},
    #  {"worker": "data_analyzer", "task": "統計分析"},
    #  {"worker": "data_analyzer", "task": "パターン認識"},
    #  {"worker": "report_generator", "task": "包括的レポート"}]

    results = execute_plan(plan)
    return integrate_results(results)

改善ポイント:
- タスクに応じて最適なワークフローを生成
- 不要なステップをスキップしてコスト削減
- 新しいタイプのタスクに自動対応
- 専門ワーカーによる高品質な出力
```

## 5. 評価者・最適化者（Evaluator-Optimizer）

### 概要

評価者・最適化者は、出力を評価し、基準を満たすまで反復的に改善するパターンである。品質が重要なタスクに有効である。

### 実装パターン

```python
# 評価者・最適化者の実装

def evaluator_optimizer_pattern(user_task, quality_criteria, max_iterations=3):
    # 初期出力を生成
    initial_prompt = f"""
以下のタスクを実行してください。

タスク: {user_task}
"""
    current_output = call_llm(initial_prompt)

    iteration = 0
    while iteration < max_iterations:
        # 評価者: 出力を評価
        evaluation_prompt = f"""
以下の出力を評価してください。

タスク: {user_task}
出力: {current_output}

評価基準:
{quality_criteria}

以下の形式で評価結果を提供してください:
{{
  "meets_criteria": true/false,
  "score": 0-100,
  "strengths": ["強み1", "強み2", ...],
  "weaknesses": ["改善点1", "改善点2", ...],
  "suggestions": ["提案1", "提案2", ...]
}}
"""
        evaluation = call_llm(evaluation_prompt)

        # 基準を満たしている場合は終了
        if evaluation["meets_criteria"]:
            return current_output

        # 最適化者: 評価を基に改善
        optimization_prompt = f"""
以下の出力を改善してください。

元のタスク: {user_task}
現在の出力: {current_output}

評価結果:
- スコア: {evaluation["score"]}
- 弱点: {evaluation["weaknesses"]}
- 改善提案: {evaluation["suggestions"]}

評価基準を満たすように出力を改善してください。
"""
        current_output = call_llm(optimization_prompt)

        iteration += 1

    # 最大反復回数に達した場合は最後の出力を返す
    return current_output
```

### パラメータ設定

**評価基準の定義**
- 具体的で測定可能な基準を設定
- 複数の評価軸を使用（正確性、完全性、読みやすさなど）
- 各基準に重み付けを行う

**最大反復回数**
- 一般的には2-3回が適切
- コストとレイテンシのトレードオフを考慮
- タスクの重要性に応じて調整

**終了条件**
- スコア閾値を設定（例: 80点以上）
- すべての必須基準を満たす
- 改善が収束した場合（前回との差が小さい）

**評価者と最適化者の分離**
- 別々のプロンプトを使用
- 評価者は厳格に、最適化者は創造的に
- 評価者のみモデルベース評価を使用することも可能

### ユースケース

**コンテンツ作成**
- 初稿を生成
- 品質基準（文法、トーン、情報の正確性）で評価
- フィードバックを基に改善

**コード生成**
- コードを生成
- テスト実行、静的解析で評価
- エラーや警告を修正

**創作物の生成**
- ストーリー、詩、マーケティングコピーなど
- スタイル、感情的インパクト、ブランドガイドラインで評価
- 反復的にリファイン

### Before/After例

#### Before（単一生成の問題）

```
def generate_content(topic):
    prompt = f"{topic}について記事を書いてください"
    article = call_llm(prompt)
    return article

問題点:
- 初回の出力がそのまま使用される
- 品質基準を満たさない可能性がある
- 改善の機会がない
- ユーザーが手動で修正する必要がある
```

#### After（評価者・最適化者の適用）

```
def generate_content_with_evaluation(topic, quality_criteria):
    # 初稿生成
    article = generate_initial_article(topic)

    # 評価
    evaluation = evaluate_article(article, quality_criteria)
    # 結果: {"meets_criteria": false, "score": 65,
    #        "weaknesses": ["構成が弱い", "例が不足"],
    #        "suggestions": ["明確な構成を追加", "具体例を3つ追加"]}

    # 改善
    improved_article = optimize_article(article, evaluation)

    # 再評価
    final_evaluation = evaluate_article(improved_article, quality_criteria)
    # 結果: {"meets_criteria": true, "score": 85}

    return improved_article

改善ポイント:
- 品質基準を自動的に適用
- 初稿のスコア65から改善版のスコア85に向上
- ユーザーの手動修正作業を削減
- 一貫した品質を保証
```

## パターンの組み合わせ

複数のパターンを組み合わせることで、さらに強力なワークフローを構築できる。

### 例1: ルーティング + プロンプト連鎖

```
ステップ1: ルーターで入力タイプを分類
  → "複雑な技術的質問"

ステップ2: 技術的質問専用のプロンプト連鎖を実行
  a. 質問の詳細分析
  b. ドキュメント検索
  c. コード例生成
  d. 最終回答の作成
```

### 例2: 並列化 + 評価者・最適化者

```
ステップ1: 複数のバリエーションを並列生成

ステップ2: 各バリエーションを並列で評価

ステップ3: 最高スコアのバリエーションを選択

ステップ4: 選択されたバリエーションを最適化
```

### 例3: オーケストレーター・ワーカー + 並列化

```
オーケストレーター: タスクを分解
  → サブタスクA、B、Cを特定

並列実行:
  ワーカー1: サブタスクAを実行
  ワーカー2: サブタスクBを実行
  ワーカー3: サブタスクCを実行

オーケストレーター: 結果を統合
```

## パターン選択のデシジョンツリー

```
タスクの分析
  |
  ├─ 単一プロンプトで解決可能か？
  |    └─ はい → 単一プロンプトを使用
  |    └─ いいえ ↓
  |
  ├─ ステップが明確に定義できるか？
  |    └─ はい → プロンプト連鎖
  |    └─ いいえ ↓
  |
  ├─ 入力タイプが多様か？
  |    └─ はい → ルーティング
  |    └─ いいえ ↓
  |
  ├─ 独立したサブタスクがあるか？
  |    └─ はい → 並列化
  |    └─ いいえ ↓
  |
  ├─ タスク構造が動的に変わるか？
  |    └─ はい → オーケストレーター・ワーカー
  |    └─ いいえ ↓
  |
  └─ 反復的な改善が必要か？
       └─ はい → 評価者・最適化者
       └─ いいえ → プロンプト連鎖（デフォルト）
```

## まとめ

### パターンの選択原則

1. **シンプリシティ優先**: 最もシンプルなパターンから始める
2. **実測に基づく改善**: 複雑性の追加は実データで効果を検証
3. **段階的な導入**: 一度にすべてを実装せず、段階的に改善
4. **組み合わせの活用**: 単一パターンに固執せず、組み合わせを検討

### パターン別の推奨使用順序

1. プロンプト連鎖（最初に検討）
2. ルーティング（入力が多様な場合）
3. 並列化（レイテンシが問題の場合）
4. 評価者・最適化者（品質が重要な場合）
5. オーケストレーター・ワーカー（最も複雑、最後の選択肢）

### 次のステップ

- 実装例を参照: [examples/workflow-patterns.md](../examples/workflow-patterns.md)
- Before/After改善例を確認: [examples/before-after-examples.md](../examples/before-after-examples.md)
- アーキテクチャ原則を理解: [architecture-principles.md](architecture-principles.md)
