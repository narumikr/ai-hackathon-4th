# 本番運用のベストプラクティス

## はじめに

AI Agentシステムを本番環境で安定的に運用するには、モニタリング、エラーハンドリング、コスト最適化、スケーラビリティなどの考慮が必要である。このドキュメントでは、本番運用のベストプラクティスを解説する。

## モニタリングとロギング

### 1. 構造化ロギング

**重要性**
問題の早期発見と迅速な対応には、詳細なログが不可欠である。

**実装例**

```python
import logging
import json
import time
from typing import Dict, Any

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

    def log_agent_call(
        self,
        agent_name: str,
        input_data: Any,
        output_data: Any,
        metadata: Dict[str, Any]
    ):
        """エージェント呼び出しをログに記録"""
        log_entry = {
            "timestamp": time.time(),
            "event_type": "agent_call",
            "agent_name": agent_name,
            "input": self._sanitize(input_data),
            "output": self._sanitize(output_data),
            "metadata": metadata
        }
        self.logger.info(json.dumps(log_entry))

    def log_error(self, error: Exception, context: Dict[str, Any]):
        """エラーをログに記録"""
        log_entry = {
            "timestamp": time.time(),
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        self.logger.error(json.dumps(log_entry))

    def _sanitize(self, data: Any) -> Any:
        """機密情報を削除"""
        # PII、API key などを削除
        if isinstance(data, dict):
            return {
                k: "***REDACTED***" if self._is_sensitive(k) else v
                for k, v in data.items()
            }
        return data

    def _is_sensitive(self, key: str) -> bool:
        """機密フィールドかチェック"""
        sensitive_keys = ["password", "api_key", "token", "secret"]
        return any(s in key.lower() for s in sensitive_keys)

# 使用例
logger = StructuredLogger("agent_system")

def process_task(task):
    start_time = time.time()

    try:
        result = execute_agent(task)

        logger.log_agent_call(
            agent_name="task_processor",
            input_data=task,
            output_data=result,
            metadata={
                "duration_ms": (time.time() - start_time) * 1000,
                "success": True
            }
        )

        return result
    except Exception as e:
        logger.log_error(e, {"task": task})
        raise
```

### 2. メトリクスの追跡

**重要なメトリクス**
- レイテンシ（P50, P95, P99）
- エラー率
- スループット
- コスト
- ツール使用頻度

**実装例**

```python
from dataclasses import dataclass
from typing import List
import statistics

@dataclass
class Metrics:
    latencies: List[float] = None
    errors: int = 0
    successes: int = 0
    total_cost: float = 0.0

    def __post_init__(self):
        if self.latencies is None:
            self.latencies = []

    def record_latency(self, latency_ms: float):
        """レイテンシを記録"""
        self.latencies.append(latency_ms)

    def record_success(self):
        """成功を記録"""
        self.successes += 1

    def record_error(self):
        """エラーを記録"""
        self.errors += 1

    def record_cost(self, cost: float):
        """コストを記録"""
        self.total_cost += cost

    def get_percentile(self, percentile: int) -> float:
        """パーセンタイルを計算"""
        if not self.latencies:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        index = int(len(sorted_latencies) * percentile / 100)
        return sorted_latencies[min(index, len(sorted_latencies) - 1)]

    def get_error_rate(self) -> float:
        """エラー率を計算"""
        total = self.successes + self.errors
        return self.errors / total if total > 0 else 0.0

    def get_summary(self) -> dict:
        """メトリクスサマリーを取得"""
        return {
            "total_requests": self.successes + self.errors,
            "success_count": self.successes,
            "error_count": self.errors,
            "error_rate": self.get_error_rate(),
            "latency_p50": self.get_percentile(50),
            "latency_p95": self.get_percentile(95),
            "latency_p99": self.get_percentile(99),
            "total_cost": self.total_cost,
            "average_cost": self.total_cost / (self.successes + self.errors) if (self.successes + self.errors) > 0 else 0.0
        }

# 使用例
metrics = Metrics()

def process_with_metrics(task):
    start_time = time.time()

    try:
        result = execute_agent(task)
        cost = calculate_cost(result)

        latency_ms = (time.time() - start_time) * 1000
        metrics.record_latency(latency_ms)
        metrics.record_success()
        metrics.record_cost(cost)

        return result
    except Exception as e:
        metrics.record_error()
        raise

# 定期的にメトリクスを報告
def report_metrics():
    summary = metrics.get_summary()
    logger.info(f"Metrics Summary: {json.dumps(summary)}")
```

## エラーハンドリングとリトライ戦略

### 1. エクスポネンシャルバックオフ

**概要**
一時的なエラーに対して、待機時間を指数関数的に増やしながらリトライする。

**実装例**

```python
import time
import random

def exponential_backoff_retry(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """エクスポネンシャルバックオフでリトライ"""
    for attempt in range(max_retries):
        try:
            return func()
        except TemporaryError as e:
            if attempt == max_retries - 1:
                # 最後のリトライ
                raise

            # 待機時間を計算
            delay = min(base_delay * (exponential_base ** attempt), max_delay)

            # ジッターを追加（サンダリングハード問題を回避）
            if jitter:
                delay = delay * (0.5 + random.random())

            logger.info(f"Retry attempt {attempt + 1}/{max_retries} after {delay:.2f}s")
            time.sleep(delay)
        except PermanentError as e:
            # 永続的なエラーはリトライしない
            raise

# 使用例
def call_external_api():
    result = exponential_backoff_retry(
        lambda: api.call("endpoint"),
        max_retries=3,
        base_delay=1.0
    )
    return result
```

### 2. サーキットブレーカー

**概要**
連続的なエラーが発生した場合、一時的にリクエストを停止し、システムを保護する。

**実装例**

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # 正常動作
    OPEN = "open"          # エラー多発、リクエスト拒否
    HALF_OPEN = "half_open"  # 回復テスト中

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

    def call(self, func):
        """サーキットブレーカー経由で関数を呼び出し"""
        if self.state == CircuitState.OPEN:
            # タイムアウト経過後、回復テスト
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """成功時の処理"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                # 回復成功
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info("Circuit breaker: CLOSED")
        else:
            self.failure_count = 0

    def _on_failure(self):
        """失敗時の処理"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker: OPEN (failures: {self.failure_count})")

# 使用例
circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

def call_with_circuit_breaker():
    return circuit_breaker.call(lambda: external_service.call())
```

## コスト最適化

### 1. モデル選択の最適化

**戦略**
タスクの複雑性に応じて適切なモデルを選択する。

**実装例**

```python
def select_model(task_complexity: str) -> str:
    """タスクの複雑性に基づいてモデルを選択"""
    model_selection = {
        "simple": "haiku",      # 軽量で高速
        "moderate": "sonnet",   # バランス
        "complex": "opus"       # 高性能
    }
    return model_selection.get(task_complexity, "sonnet")

def estimate_complexity(task: str) -> str:
    """タスクの複雑性を推定"""
    # 簡易的な複雑性推定
    if len(task) < 100:
        return "simple"
    elif len(task) < 500:
        return "moderate"
    else:
        return "complex"

def process_with_optimal_model(task: str):
    complexity = estimate_complexity(task)
    model = select_model(complexity)

    logger.info(f"Using model: {model} for complexity: {complexity}")

    result = call_llm(task, model=model)
    return result
```

### 2. キャッシング

**戦略**
同じ入力に対する出力をキャッシュし、重複呼び出しを削減する。

**実装例**

```python
from functools import lru_cache
import hashlib

class LLMCache:
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size

    def get_key(self, prompt: str, model: str, temperature: float) -> str:
        """キャッシュキーを生成"""
        content = f"{prompt}:{model}:{temperature}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, prompt: str, model: str, temperature: float):
        """キャッシュから取得"""
        key = self.get_key(prompt, model, temperature)
        return self.cache.get(key)

    def set(self, prompt: str, model: str, temperature: float, result):
        """キャッシュに保存"""
        if len(self.cache) >= self.max_size:
            # 最も古いエントリを削除（FIFO）
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        key = self.get_key(prompt, model, temperature)
        self.cache[key] = result

llm_cache = LLMCache()

def call_llm_with_cache(prompt: str, model: str = "sonnet", temperature: float = 0.5):
    """キャッシュ付きLLM呼び出し"""
    # キャッシュを確認
    cached_result = llm_cache.get(prompt, model, temperature)
    if cached_result:
        logger.info("Cache hit")
        return cached_result

    # キャッシュミス、LLMを呼び出し
    logger.info("Cache miss, calling LLM")
    result = call_llm(prompt, model=model, temperature=temperature)

    # キャッシュに保存
    llm_cache.set(prompt, model, temperature, result)

    return result
```

### 3. バッチ処理

**戦略**
複数のリクエストをバッチ化して効率を向上させる。

**実装例**

```python
import asyncio
from typing import List

class BatchProcessor:
    def __init__(self, batch_size: int = 10, max_wait_ms: int = 100):
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.queue = []

    async def add_to_batch(self, item):
        """バッチにアイテムを追加"""
        self.queue.append(item)

        if len(self.queue) >= self.batch_size:
            return await self._process_batch()

        # タイムアウトを待つ
        await asyncio.sleep(self.max_wait_ms / 1000)

        if self.queue:
            return await self._process_batch()

    async def _process_batch(self):
        """バッチを処理"""
        batch = self.queue[:self.batch_size]
        self.queue = self.queue[self.batch_size:]

        # バッチで処理
        results = await process_batch_api_call(batch)

        return results

batch_processor = BatchProcessor(batch_size=10)
```

## レイテンシ改善

### 1. ストリーミング

**戦略**
出力をストリーミングし、最初のトークンまでの時間を短縮する。

**実装例**

```python
def stream_response(prompt: str):
    """ストリーミングレスポンス"""
    for chunk in call_llm_stream(prompt):
        # チャンクを即座に処理/返す
        yield chunk

# 使用例
for chunk in stream_response("質問"):
    print(chunk, end="", flush=True)
```

### 2. 並列化

**戦略**
独立したタスクを並列実行する。

**実装例**

```python
import asyncio

async def parallel_processing(tasks: List):
    """タスクを並列処理"""
    # すべてのタスクを並列実行
    results = await asyncio.gather(*[process_task(task) for task in tasks])
    return results
```

## スケーラビリティ

### 1. レート制限

**戦略**
API呼び出しのレートを制限し、リソースを保護する。

**実装例**

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()

    def acquire(self):
        """レート制限をチェック"""
        now = time.time()

        # 古い呼び出しを削除
        while self.calls and self.calls[0] < now - self.time_window:
            self.calls.popleft()

        # レート制限チェック
        if len(self.calls) >= self.max_calls:
            # 待機時間を計算
            wait_time = self.calls[0] + self.time_window - now
            raise RateLimitExceeded(f"Rate limit exceeded. Wait {wait_time:.2f}s")

        # 呼び出しを記録
        self.calls.append(now)

rate_limiter = RateLimiter(max_calls=100, time_window=60)

def call_with_rate_limit():
    rate_limiter.acquire()
    return call_llm("prompt")
```

### 2. ロードバランシング

**戦略**
複数のインスタンス間でリクエストを分散する。

**実装例**

```python
import random

class LoadBalancer:
    def __init__(self, instances: List):
        self.instances = instances
        self.current_index = 0

    def get_instance(self, strategy: str = "round_robin"):
        """インスタンスを選択"""
        if strategy == "round_robin":
            instance = self.instances[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.instances)
            return instance
        elif strategy == "random":
            return random.choice(self.instances)

load_balancer = LoadBalancer(["instance1", "instance2", "instance3"])
```

## まとめ

### 本番運用のチェックリスト

**モニタリング**
- [ ] 構造化ロギングを実装したか？
- [ ] 重要なメトリクスを追跡しているか？
- [ ] アラートを設定したか？

**エラーハンドリング**
- [ ] リトライ戦略を実装したか？
- [ ] サーキットブレーカーを実装したか？
- [ ] エラーを適切にログに記録しているか？

**コスト最適化**
- [ ] モデル選択を最適化したか？
- [ ] キャッシングを実装したか？
- [ ] バッチ処理を活用しているか？

**パフォーマンス**
- [ ] レイテンシを測定しているか？
- [ ] ストリーミングを活用しているか？
- [ ] 並列化を適用したか？

**スケーラビリティ**
- [ ] レート制限を実装したか？
- [ ] ロードバランシングを設定したか？
- [ ] 容量計画を立てたか？

### 次のステップ

- 評価とテスト戦略: [evaluation-testing.md](evaluation-testing.md)
- アンチパターンの回避: [anti-patterns.md](anti-patterns.md)
- ワークフローパターンの詳細: [workflow-patterns-detail.md](workflow-patterns-detail.md)
