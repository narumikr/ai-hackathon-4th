# スポット画像生成ジョブ設計（案A）

## 目的
旅行ガイド生成後にスポット画像生成を確実に実行するため、DBジョブキュー方式を導入する。FastAPIのBackgroundTasksに依存せず、ジョブ登録とワーカー実行を分離する

## スコープ
- 画像生成はジョブとしてDBに登録し、専用ワーカーが処理する
- ガイド生成ユースケースは画像生成を実行せず、ジョブ登録のみ行う
- 再試行・進捗更新・重複防止を最小構成で実現する

## 用語
- ジョブ: 後で非同期に実行する作業単位。DBに保存しワーカーが順次処理する
- ワーカー: ジョブを取得し実行する常駐プロセスまたはバッチ

## 状態遷移
### 画像ステータス（SpotDetail.image_status）
- not_started → processing → succeeded / failed

### ジョブステータス（spot_image_jobs.status）
- queued → processing → succeeded
- queued → processing → failed
- failed → queued（再試行時）

## データモデル
### テーブル: spot_image_jobs
最小構成で再試行・排他・重複防止に対応する

カラム定義:
- id: UUID, PK
- plan_id: TEXT, NOT NULL
- spot_name: TEXT, NOT NULL
- status: TEXT, NOT NULL, CHECK(queued|processing|succeeded|failed)
- attempts: INT, NOT NULL, DEFAULT 0
- max_attempts: INT, NOT NULL, DEFAULT 3
- last_error: TEXT, NULL
- created_at: TIMESTAMPTZ, NOT NULL, DEFAULT now()
- updated_at: TIMESTAMPTZ, NOT NULL, DEFAULT now()
- locked_at: TIMESTAMPTZ, NULL
- locked_by: TEXT, NULL

制約・インデックス:
- plan_id + spot_name のユニーク制約（同一スポットの重複ジョブ防止）
- status + locked_at のインデックス（取得効率）

DDL例:
```sql
CREATE TABLE spot_image_jobs (
  id UUID PRIMARY KEY,
  plan_id TEXT NOT NULL,
  spot_name TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('queued', 'processing', 'succeeded', 'failed')),
  attempts INT NOT NULL DEFAULT 0,
  max_attempts INT NOT NULL DEFAULT 3,
  last_error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  locked_at TIMESTAMPTZ,
  locked_by TEXT
);

CREATE UNIQUE INDEX spot_image_jobs_plan_spot_unique
  ON spot_image_jobs (plan_id, spot_name);

CREATE INDEX spot_image_jobs_status_locked_idx
  ON spot_image_jobs (status, locked_at);
```

## ジョブ登録仕様
### 登録タイミング
- 旅行ガイド生成完了直後に登録する

### 対象スポット
- image_url が空、かつ image_status が not_started または failed のスポット
- image_status が succeeded のスポットは登録しない

### 重複防止
- plan_id + spot_name のユニーク制約で既存ジョブをスキップする

### 期待される副作用
- 画像生成の失敗がガイド生成の成否に影響しない

## ワーカー仕様
### ジョブ取得（排他制御）
- PostgreSQLの row lock を使用する
- 取得時に FOR UPDATE SKIP LOCKED を用い、複数ワーカーでも競合しない

擬似コード:
```text
loop:
  tx begin
    jobs = select * from spot_image_jobs
           where status = 'queued'
           order by created_at asc
           limit N
           for update skip locked
    for job in jobs:
      update spot_image_jobs
        set status='processing', locked_at=now(), locked_by=:worker_id, updated_at=now()
        where id=job.id
  tx commit

  if jobs is empty: sleep(short) and continue

  parallel for job in jobs (max_concurrent):
    try:
      # 1) SpotDetail.image_status=processing に更新
      # 2) プロンプト生成 → 画像生成 → アップロード
      # 3) SpotDetail.image_url と image_status=succeeded を保存
      # 4) job.status=succeeded, updated_at=now
    except e:
      # job.attempts += 1
      # if attempts < max_attempts:
      #   job.status='queued'
      # else:
      #   job.status='failed'
      # job.last_error = str(e)
      # job.updated_at=now
```

### 並列数
- ワーカー内部で max_concurrent を設定する
- 既存のセマフォ制御を流用してよい

### 再試行
- max_attempts = 3
- 失敗時は attempts を加算し、未到達なら queued に戻す
- 最小実装では即時再投入とする

## 既存コードとの責務分割
### GenerateTravelGuideUseCase
- 旅行ガイド生成のみ
- 画像生成を呼ばない
- 完了後にジョブ登録のみ行う

### GenerateSpotImagesUseCase
- 1スポット単位の生成処理を公開または再利用する
- ワーカーはこの処理を呼ぶ

## UI表示方針
- image_status=processing: ローディング表示
- image_status=failed: 失敗表示

## 実装順序
1. spot_image_jobsテーブルのマイグレーション追加
2. ジョブ登録処理の追加（ガイド生成完了時）
3. 画像生成のBackgroundTasks呼び出し削除
4. ワーカー追加
5. UIでprocessing/failedの表示対応

## 非機能要件
- 画像生成失敗はガイド生成の成功に影響しない
- ジョブ処理の失敗原因は last_error に記録する
- ワーカーは複数起動可能であること

## 実装差分（最小）
### 変更点一覧
1. マイグレーション追加
   - 追加: spot_image_jobs テーブル
   - 配置: backend/alembic/versions/ に新規マイグレーション

2. ジョブ登録処理の追加
   - 追加先: backend/app/application/use_cases/generate_travel_guide.py
   - 内容: ガイド生成完了後にジョブ登録関数を呼ぶ

3. BackgroundTasksでの画像生成呼び出し削除
   - 削除先: backend/app/application/use_cases/generate_travel_guide.py
   - 内容: background_tasks.add_task(self._image_use_case.execute, ...) を削除

4. ジョブリポジトリ追加
   - 追加: backend/app/infrastructure/repositories/spot_image_job_repository.py
   - 役割: ジョブ登録、取得、ロック、更新

5. ワーカー追加
   - 追加: backend/app/application/workers/spot_image_worker.py
   - 役割: queued取得→processing→画像生成→succeeded/failed

6. DI追加（必要なら）
   - 変更: backend/app/interfaces/api/dependencies.py
   - 目的: ジョブ登録時のリポジトリ生成

7. UI対応（最小）
   - 変更: frontend/src/app/travel/[id]/page.tsx
   - 追加: image_status=processing/failed の表示

### 影響ファイル最小セット
- backend/alembic/versions/<new>.py
- backend/app/application/use_cases/generate_travel_guide.py
- backend/app/infrastructure/repositories/spot_image_job_repository.py
- backend/app/application/workers/spot_image_worker.py
- backend/app/interfaces/api/dependencies.py
- frontend/src/app/travel/[id]/page.tsx

## ジョブリポジトリAPI設計
### 目的
ジョブの登録・取得・状態更新・排他制御を一箇所に集約する

### 想定インターフェース
- create_job(plan_id: str, spot_name: str, max_attempts: int = 3) -> None
  - plan_id + spot_name が既存の場合は登録しない（ユニーク制約で担保）

- fetch_queued_jobs(limit: int) -> list[SpotImageJob]
  - status='queued' を created_at 昇順で取得

- lock_jobs(job_ids: list[str], worker_id: str) -> None
  - status='processing' へ更新し、locked_at/locked_by を設定

- mark_succeeded(job_id: str) -> None
  - status='succeeded' に更新

- mark_failed(job_id: str, error_message: str) -> None
  - attempts += 1
  - attempts < max_attempts の場合は status='queued'
  - attempts >= max_attempts の場合は status='failed'

### 取得・ロックの一括処理
- fetch + lock を同一トランザクションで行う
- SQLでは SELECT ... FOR UPDATE SKIP LOCKED を使用する

## ワーカー起動方式
### 目的
spot_image_jobs の queued ジョブを継続的に処理する

### 起動方法（ローカル）
- 例: `just dev-worker` を追加して起動する
- ワーカーは常駐プロセスとして動かす

### 起動方法（本番）
- Cloud Runの常駐コンテナ、または定期起動（cron）で運用する
- 複数ワーカー起動を許可する（SKIP LOCKEDで競合回避）

### 実行ループ仕様
- 1ループで最大N件を取得
- 空の場合は短い sleep（例: 0.5〜1秒）で再試行
- max_concurrent で並列生成数を制御

## 既存ユースケースへの組み込み位置
- GenerateTravelGuideUseCase のガイド保存完了直後でジョブ登録を行う
- BackgroundTasksへの画像生成追加は削除する

## UI表示ルール
- image_status=processing: ローディング表示
- image_status=failed: 失敗表示
- image_urlがある場合は表示優先

## 実装計画（タスク分割と優先順）
1. マイグレーション作成
   - spot_image_jobs テーブルを追加
   - 既存テーブルへの変更は行わない

2. リポジトリ実装
   - SpotImageJobRepository を追加
   - 取得・ロックを同一トランザクションで行う

3. ジョブ登録処理
   - ガイド生成完了時にジョブ登録する処理を追加
   - image_statusがsucceededのスポットは登録しない

4. 画像生成のBackgroundTasks削除
   - GenerateTravelGuideUseCase から画像生成の追加処理を削除

5. ワーカー実装
   - queued取得→processing→生成→succeeded/failed
   - 失敗時の再試行処理を実装

6. UI最小対応
   - processing/failed の表示追加

7. 動作確認
   - ジョブが登録されること
   - ワーカーがジョブを処理すること
   - image_statusが更新されること
