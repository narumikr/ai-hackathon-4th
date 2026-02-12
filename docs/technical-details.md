# 技術詳細

## 目的

このドキュメントは、開発・運用・デプロイの実務情報を実装準拠でまとめる

## システム構成

- Backend: FastAPI（`backend`）
- Frontend: Next.js App Router（`frontend`）
- API接続: Frontend の `frontend/src/lib/api.ts` 経由で `/api/v1/*` を利用
- インフラ: Cloud Run / Cloud SQL / Cloud Storage / Secret Manager / Artifact Registry

## 前提条件

- `just`
- `uv`
- `pnpm`
- Python 3.12以上
- Node.js 18以上

## セットアップ

1. 依存関係をインストール

```bash
just install-all
```

2. 環境変数を作成

```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

3. DBとRedisを起動

```bash
cd infrastructure/docker
docker-compose up -d
```

4. マイグレーションを適用

```bash
just migrate-up
```

5. 開発サーバーを起動

```bash
just dev-all
# または
just dev-backend
just dev-frontend
```

## 画像生成ワーカー

```bash
just dev-worker
```

- `IMAGE_EXECUTION_MODE=local_worker` のときに使用
- `IMAGE_EXECUTION_MODE=cloud_tasks` の本番構成では常駐ワーカーは不要

## API仕様

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- 静的仕様: `docs/backend/openapi.json`
- 更新コマンド: `just docs-generate-openapi`

## よく使うコマンド

```bash
# テスト
just test-all
just test-backend
just test-frontend
just test-backend-cov
just test-frontend-ci

# 品質チェック
just check-quality
just check-quality-backend
just check-quality-frontend

# ビルド
just build-frontend

# DB
just migrate-create "name"
just migrate-up
just migrate-down
just migrate-history
just migrate-current
```

## CI/CD（Workflow準拠）

### Stage 1

- 定義: `.github/workflows/01-lint-check.yml`
- frontend: `just check-quality-frontend`
- backend: `just check-quality-backend`

### Stage 2

- 定義: `.github/workflows/02-quality-check.yml`
- frontend: `just test-frontend-ci`, `just build-frontend`
- backend: `just test-backend-cov`

### ステータス集約

- 定義: `.github/workflows/pipeline-status.yml`

詳細: `docs/actions/ci-workflow-design.md`

## デプロイ

デプロイ手順とTerraform運用は以下を参照

- `infrastructure/terraform/README.md`
- `infrastructure/terraform/docs/quickstart-development.md`
- `infrastructure/terraform/docs/setup-production.md`
