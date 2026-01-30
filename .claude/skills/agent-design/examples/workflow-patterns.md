# ワークフローパターン実装例

このドキュメントでは、5つのワークフローパターンの具体的な実装例を提供する。各パターンについて、擬似コードと実装ステップを示す。

## 1. プロンプト連鎖（Prompt Chaining）

### 基本実装

```python
def prompt_chaining_example(user_input: str) -> dict:
    """
    プロンプト連鎖の基本実装例
    タスク: ユーザーの質問に対して、調査→分析→回答のステップで処理
    """

    # ステップ1: 質問の分析
    analysis_result = analyze_question(user_input)

    # ステップ2: 情報収集
    collected_info = collect_information(analysis_result)

    # ステップ3: 回答生成
    final_answer = generate_answer(user_input, collected_info)

    return {
        "answer": final_answer,
        "analysis": analysis_result,
        "sources": collected_info
    }

def analyze_question(question: str) -> dict:
    """ステップ1: 質問を分析し、必要な情報を特定"""
    prompt = f"""
以下の質問を分析し、回答に必要な情報を特定してください。

質問: {question}

以下のJSON形式で出力してください:
{{
  "topic": "主なトピック",
  "required_info": ["必要な情報1", "必要な情報2", ...],
  "complexity": "simple/moderate/complex"
}}
"""
    result = call_llm(prompt, temperature=0.2)
    return json.loads(result)

def collect_information(analysis: dict) -> list:
    """ステップ2: 必要な情報を収集"""
    collected = []

    for info_type in analysis["required_info"]:
        prompt = f"""
以下の情報を検索してください: {info_type}

トピック: {analysis["topic"]}

関連する情報を簡潔にまとめてください。
"""
        info = call_llm(prompt, tools=["search_web"], temperature=0.3)
        collected.append({
            "type": info_type,
            "content": info
        })

    return collected

def generate_answer(question: str, information: list) -> str:
    """ステップ3: 収集した情報を基に回答を生成"""
    info_text = "\n".join([f"- {item['type']}: {item['content']}" for item in information])

    prompt = f"""
以下の情報を基に、ユーザーの質問に回答してください。

質問: {question}

収集した情報:
{info_text}

明確で簡潔な回答を提供してください。
"""
    answer = call_llm(prompt, temperature=0.5)
    return answer
```

### 実装ステップ

1. **タスクを明確なステップに分解**: 質問分析 → 情報収集 → 回答生成
2. **各ステップのプロンプトを設計**: 各ステップの入出力を明確に定義
3. **ステップ間でデータを伝播**: 前のステップの出力を次のステップの入力として使用
4. **各ステップのパラメータを最適化**: 温度、ツール、モデルを調整
5. **エラーハンドリングを追加**: 各ステップで出力を検証

## 2. ルーティング（Routing）

### 基本実装

```python
def routing_example(user_input: str) -> dict:
    """
    ルーティングの基本実装例
    タスク: 入力タイプに応じて適切なハンドラーに振り分け
    """

    # ルーター: 入力タイプを分類
    category = route_input(user_input)

    # カテゴリに応じたハンドラーを選択
    handlers = {
        "factual_question": handle_factual_question,
        "creative_task": handle_creative_task,
        "code_request": handle_code_request,
        "data_analysis": handle_data_analysis
    }

    handler = handlers.get(category, handle_general_query)

    # ハンドラーを実行
    result = handler(user_input)

    return {
        "category": category,
        "result": result
    }

def route_input(user_input: str) -> str:
    """入力タイプを分類"""
    prompt = f"""
以下の入力を分類してください。

入力: {user_input}

分類カテゴリ:
- factual_question: 事実に基づく質問
- creative_task: 創作タスク（物語、詩、アイデアなど）
- code_request: コード生成・レビューのリクエスト
- data_analysis: データ分析のリクエスト
- general_query: 一般的な問い合わせ

カテゴリ名のみを返してください。
"""
    category = call_llm(prompt, model="haiku", temperature=0.1)
    return category.strip()

def handle_factual_question(question: str) -> str:
    """事実に基づく質問のハンドラー"""
    prompt = f"""
以下の質問に、正確な事実に基づいて回答してください。

質問: {question}

必要に応じて検索ツールを使用してください。
"""
    return call_llm(prompt, tools=["search_web"], temperature=0.2)

def handle_creative_task(task: str) -> str:
    """創作タスクのハンドラー"""
    prompt = f"""
以下の創作タスクを実行してください。

タスク: {task}

創造的で魅力的な内容を生成してください。
"""
    return call_llm(prompt, temperature=0.8)

def handle_code_request(request: str) -> str:
    """コードリクエストのハンドラー"""
    prompt = f"""
以下のリクエストに基づいてコードを生成してください。

リクエスト: {request}

コードには適切なコメントと説明を含めてください。
"""
    return call_llm(prompt, tools=["run_code"], temperature=0.3)

def handle_data_analysis(request: str) -> str:
    """データ分析のハンドラー"""
    prompt = f"""
以下のデータ分析リクエストを実行してください。

リクエスト: {request}

分析結果を可視化し、インサイトを提供してください。
"""
    return call_llm(prompt, tools=["run_code", "create_chart"], temperature=0.3)

def handle_general_query(query: str) -> str:
    """一般的な問い合わせのハンドラー"""
    prompt = f"""
以下の問い合わせに回答してください。

問い合わせ: {query}
"""
    return call_llm(prompt, temperature=0.5)
```

### 実装ステップ

1. **カテゴリを定義**: 入力タイプを3-7個のカテゴリに分類
2. **ルーターを実装**: 軽量モデル（Haiku）で分類
3. **各カテゴリのハンドラーを作成**: カテゴリごとに特化したプロンプトとツール
4. **フォールバックを用意**: 分類できない場合のデフォルトハンドラー
5. **パラメータを最適化**: 各ハンドラーの温度、モデル、ツールを調整

## 3. 並列化（Parallelization）

### 基本実装

```python
import asyncio

async def parallelization_example(urls: list) -> dict:
    """
    並列化の基本実装例
    タスク: 複数のURLを並列で処理し、結果を統合
    """

    # 並列タスクを作成
    tasks = [process_url(url) for url in urls]

    # すべてのタスクを並列実行
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # エラーハンドリングと結果の整理
    valid_results = []
    errors = []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append({
                "url": urls[i],
                "error": str(result)
            })
        else:
            valid_results.append(result)

    # 結果を統合
    final_result = integrate_results(valid_results)

    return {
        "result": final_result,
        "processed": len(valid_results),
        "errors": len(errors),
        "error_details": errors
    }

async def process_url(url: str) -> dict:
    """個別URLを処理"""
    # コンテンツを取得
    content = await fetch_url_async(url)

    # コンテンツを要約
    summary_prompt = f"""
以下のWebページの内容を要約してください。

URL: {url}
コンテンツ: {content[:2000]}

主要なポイントを3-5個の箇条書きで提供してください。
"""
    summary = await call_llm_async(summary_prompt)

    return {
        "url": url,
        "summary": summary
    }

def integrate_results(results: list) -> str:
    """複数の結果を統合"""
    summaries = "\n\n".join([
        f"URL: {r['url']}\n{r['summary']}"
        for r in results
    ])

    integration_prompt = f"""
以下の要約を統合し、包括的なレポートを生成してください。

要約:
{summaries}

共通テーマ、主要なインサイト、推奨事項を含めてください。
"""
    return call_llm(integration_prompt)

# 実行例
async def main():
    urls = [
        "https://example.com/article1",
        "https://example.com/article2",
        "https://example.com/article3",
        "https://example.com/article4",
        "https://example.com/article5"
    ]
    result = await parallelization_example(urls)
    print(result)

# asyncio.run(main())
```

### 実装ステップ

1. **独立したタスクを特定**: 並列実行可能なサブタスクを特定
2. **非同期関数を実装**: `async`/`await`を使用
3. **タスクを作成**: `asyncio.create_task()`または内包表記
4. **並列実行**: `asyncio.gather()`でタスクを実行
5. **エラーハンドリング**: `return_exceptions=True`でエラーを捕捉
6. **結果を統合**: すべての結果を1つにまとめる

## 4. オーケストレーター・ワーカー（Orchestrator-Workers）

### 基本実装

```python
def orchestrator_worker_example(task: str) -> dict:
    """
    オーケストレーター・ワーカーの基本実装例
    タスク: 複雑なタスクを動的に分解し、ワーカーに委譲
    """

    # オーケストレーター: タスクを分析し、実行計画を立てる
    plan = create_execution_plan(task)

    # 計画に基づいてワーカーを実行
    results = execute_plan(plan)

    # 結果を統合
    final_result = integrate_worker_results(task, plan, results)

    return {
        "task": task,
        "plan": plan,
        "results": results,
        "final_result": final_result
    }

def create_execution_plan(task: str) -> dict:
    """オーケストレーター: 実行計画を立てる"""
    prompt = f"""
あなたはタスクオーケストレーターです。以下のタスクを分析し、実行計画を立ててください。

タスク: {task}

利用可能なワーカー:
1. researcher: 情報収集と調査（ツール: search_web, fetch_url）
2. analyst: データ分析と処理（ツール: run_code, calculate）
3. writer: コンテンツ作成とレポート生成
4. reviewer: 品質チェックと改善提案

<thinking>タグ内でタスクを分析し、必要なステップを決定してください。

実行計画をJSON形式で出力してください:
{{
  "steps": [
    {{
      "step_number": 1,
      "worker": "ワーカー名",
      "task": "具体的なタスク内容",
      "depends_on": []  // 依存するステップ番号
    }},
    ...
  ]
}}
"""
    result = call_llm(prompt, model="sonnet", temperature=0.3)
    return json.loads(result)

def execute_plan(plan: dict) -> list:
    """計画に基づいてワーカーを実行"""
    results = {}

    for step in plan["steps"]:
        step_number = step["step_number"]
        worker_name = step["worker"]
        task = step["task"]
        depends_on = step.get("depends_on", [])

        # 依存するステップの結果を取得
        dependencies = {
            dep: results[dep]
            for dep in depends_on
            if dep in results
        }

        # ワーカーを実行
        result = execute_worker(worker_name, task, dependencies)

        results[step_number] = {
            "worker": worker_name,
            "task": task,
            "result": result
        }

    return list(results.values())

def execute_worker(worker_name: str, task: str, dependencies: dict) -> str:
    """個別のワーカーを実行"""
    worker_configs = {
        "researcher": {
            "system_prompt": "あなたは情報収集と調査の専門家です。",
            "tools": ["search_web", "fetch_url"],
            "temperature": 0.3
        },
        "analyst": {
            "system_prompt": "あなたはデータ分析の専門家です。",
            "tools": ["run_code", "calculate"],
            "temperature": 0.2
        },
        "writer": {
            "system_prompt": "あなたはコンテンツ作成とレポート生成の専門家です。",
            "tools": [],
            "temperature": 0.7
        },
        "reviewer": {
            "system_prompt": "あなたは品質チェックと改善提案の専門家です。",
            "tools": [],
            "temperature": 0.4
        }
    }

    config = worker_configs[worker_name]

    # 依存する結果をコンテキストに含める
    context = ""
    if dependencies:
        context = "前のステップの結果:\n" + "\n".join([
            f"ステップ {step_num}: {dep['result']}"
            for step_num, dep in dependencies.items()
        ])

    prompt = f"""
{config['system_prompt']}

{context}

タスク: {task}

タスクを実行し、結果を提供してください。
"""

    result = call_llm(
        prompt,
        tools=config["tools"],
        temperature=config["temperature"]
    )

    return result

def integrate_worker_results(task: str, plan: dict, results: list) -> str:
    """ワーカーの結果を統合"""
    results_text = "\n\n".join([
        f"ステップ {i+1} ({r['worker']}): {r['task']}\n結果: {r['result']}"
        for i, r in enumerate(results)
    ])

    prompt = f"""
以下のワーカーの実行結果を統合し、最終回答を生成してください。

元のタスク: {task}

実行結果:
{results_text}

包括的で明確な最終回答を提供してください。
"""

    final_result = call_llm(prompt, temperature=0.5)
    return final_result
```

### 実装ステップ

1. **ワーカーを定義**: 各ワーカーの役割、ツール、パラメータを定義
2. **オーケストレーターを実装**: タスクを分析し、計画を立てる
3. **依存関係を管理**: ステップ間の依存関係を追跡
4. **ワーカーを実行**: 計画に基づいて順次実行
5. **結果を統合**: すべてのワーカーの結果をまとめる
6. **エラーハンドリング**: 各ワーカーのエラーを処理

## 5. 評価者・最適化者（Evaluator-Optimizer）

### 基本実装

```python
def evaluator_optimizer_example(task: str, quality_criteria: dict, max_iterations: int = 3) -> dict:
    """
    評価者・最適化者の基本実装例
    タスク: 品質基準を満たすまで反復的に改善
    """

    # 初期出力を生成
    current_output = generate_initial_output(task)

    iteration_history = []
    iteration = 0

    while iteration < max_iterations:
        # 評価者: 出力を評価
        evaluation = evaluate_output(current_output, quality_criteria)

        iteration_history.append({
            "iteration": iteration,
            "output": current_output,
            "evaluation": evaluation
        })

        # 基準を満たしている場合は終了
        if evaluation["meets_criteria"]:
            return {
                "final_output": current_output,
                "iterations": iteration + 1,
                "evaluation": evaluation,
                "history": iteration_history
            }

        # 最適化者: 評価を基に改善
        current_output = optimize_output(task, current_output, evaluation)

        iteration += 1

    # 最大反復回数に達した場合
    return {
        "final_output": current_output,
        "iterations": iteration,
        "evaluation": evaluation,
        "history": iteration_history,
        "note": "最大反復回数に達しました。基準を完全には満たしていません。"
    }

def generate_initial_output(task: str) -> str:
    """初期出力を生成"""
    prompt = f"""
以下のタスクを実行してください。

タスク: {task}
"""
    return call_llm(prompt, temperature=0.7)

def evaluate_output(output: str, criteria: dict) -> dict:
    """出力を評価"""
    criteria_text = "\n".join([
        f"- {name}: {description} (重み: {info['weight']})"
        for name, info in criteria.items()
        for description in [info['description']]
    ])

    prompt = f"""
以下の出力を評価してください。

出力:
{output}

評価基準:
{criteria_text}

各基準について0-100点で評価し、以下のJSON形式で出力してください:
{{
  "scores": {{
    "基準名": 点数,
    ...
  }},
  "overall_score": 全体スコア（加重平均）,
  "meets_criteria": true/false（80点以上でtrue）,
  "strengths": ["強み1", "強み2", ...],
  "weaknesses": ["弱点1", "弱点2", ...],
  "suggestions": ["改善提案1", "改善提案2", ...]
}}
"""
    result = call_llm(prompt, temperature=0.2)
    return json.loads(result)

def optimize_output(task: str, current_output: str, evaluation: dict) -> str:
    """評価を基に出力を改善"""
    weaknesses = "\n".join(evaluation["weaknesses"])
    suggestions = "\n".join(evaluation["suggestions"])

    prompt = f"""
以下の出力を改善してください。

元のタスク: {task}

現在の出力:
{current_output}

評価結果:
- 全体スコア: {evaluation["overall_score"]}/100
- 弱点:
{weaknesses}

改善提案:
{suggestions}

評価基準を満たすように出力を改善してください。
元の良い部分は保持しながら、弱点を修正してください。
"""
    return call_llm(prompt, temperature=0.6)

# 実行例
quality_criteria = {
    "accuracy": {
        "description": "情報の正確性",
        "weight": 0.3
    },
    "clarity": {
        "description": "明確性と読みやすさ",
        "weight": 0.3
    },
    "completeness": {
        "description": "情報の完全性",
        "weight": 0.2
    },
    "relevance": {
        "description": "タスクとの関連性",
        "weight": 0.2
    }
}

result = evaluator_optimizer_example(
    "AIエージェントの利点について説明してください",
    quality_criteria,
    max_iterations=3
)
```

### 実装ステップ

1. **品質基準を定義**: 評価軸と重み付けを設定
2. **初期出力を生成**: 創造的な温度設定で生成
3. **評価者を実装**: 各基準に基づいて評価
4. **終了条件を設定**: スコア閾値または最大反復回数
5. **最適化者を実装**: 評価フィードバックを基に改善
6. **反復ループ**: 基準を満たすまで評価→最適化を繰り返す
7. **履歴を記録**: 各反復の出力と評価を保存

## パラメータチューニングガイド

### 温度設定

| タスクタイプ | 推奨温度 | 理由 |
|------------|---------|------|
| 事実に基づく質問 | 0.1-0.3 | 正確性を優先 |
| データ分析 | 0.2-0.3 | 精密な計算と分析 |
| コード生成 | 0.2-0.4 | 正確性と若干の柔軟性 |
| 創作タスク | 0.7-0.9 | 創造性を優先 |
| 一般的な回答 | 0.5-0.7 | バランス |

### モデル選択

| タスクタイプ | 推奨モデル | 理由 |
|------------|-----------|------|
| 分類・ルーティング | Haiku | 軽量で高速、コスト効率 |
| 複雑な分析 | Opus | 最高の性能 |
| 一般的なタスク | Sonnet | 品質とコストのバランス |

### ツール数

| シナリオ | 推奨ツール数 | 理由 |
|---------|------------|------|
| シンプルなタスク | 0-3 | 最小限のオーバーヘッド |
| 中程度のタスク | 3-7 | 十分な機能性 |
| 複雑なタスク | 5-10 | 柔軟性を維持 |

## まとめ

### 実装のベストプラクティス

1. **シンプルから始める**: プロンプト連鎖から開始
2. **段階的に複雑化**: 必要に応じて他のパターンを追加
3. **パラメータを最適化**: 温度、モデル、ツールを調整
4. **エラーハンドリングを実装**: すべてのステップで検証
5. **ログとモニタリング**: 各ステップの入出力を記録

### 次のステップ

- Before/After改善例: [before-after-examples.md](before-after-examples.md)
- ユースケース別実装: [use-case-examples.md](use-case-examples.md)
- アーキテクチャ原則: [../references/architecture-principles.md](../references/architecture-principles.md)
