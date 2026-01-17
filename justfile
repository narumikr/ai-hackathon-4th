# justfile
# プロジェクト: Historical Travel Agent
# 説明: 歴史学習特化型旅行AIエージェント

# デフォルトレシピ: コマンド一覧を表示
default:
	@just --list

# --- 変数定義 ---
backend_dir := "backend"
frontend_dir := "frontend"
backend_port := "8000"
frontend_port := "3000"
uv := "uv"
pnpm := "pnpm"

# --- 開発サーバー起動 ---

# バックエンド開発サーバー起動（FastAPI）
dev-backend:
	cd {{backend_dir}} && {{uv}} run fastapi dev main.py --port {{backend_port}}

# フロントエンド開発サーバー起動（Next.js）
dev-frontend:
	cd {{frontend_dir}} && {{pnpm}} dev

# バックエンド＋フロントエンド同時起動（並列実行）
dev-all:
	@echo "Starting backend and frontend servers..."
	@echo "Backend: http://localhost:{{backend_port}}"
	@echo "Frontend: http://localhost:{{frontend_port}}"
	backend_cmd="just dev-backend"
	frontend_cmd="just dev-frontend"
	$backend_cmd &
	backend_pid=$!
	$frontend_cmd &
	frontend_pid=$!
	trap 'echo "Stopping dev servers..."; kill "$backend_pid" "$frontend_pid" 2>/dev/null || true' INT TERM EXIT
	wait "$backend_pid"
	backend_status=$?
	wait "$frontend_pid"
	frontend_status=$?
	if [ "$backend_status" -ne 0 ] || [ "$frontend_status" -ne 0 ]; then
	echo "One of the dev servers exited with an error (backend: $backend_status, frontend: $frontend_status)."
	exit 1
	ßfi
# --- テスト実行 ---

# バックエンドテスト実行
test-backend:
	cd {{backend_dir}} && {{uv}} run pytest

# バックエンドテスト実行（カバレッジ付き）
test-backend-cov:
	cd {{backend_dir}} && {{uv}} run pytest --cov=app --cov-report=html

# フロントエンドテスト実行
test-frontend:
	cd {{frontend_dir}} && {{pnpm}} test

# フロントエンドテスト実行（CI用、watch modeなし）
test-frontend-ci:
	cd {{frontend_dir}} && {{pnpm}} test:run

# フロントエンドテスト実行（カバレッジ付き）
test-frontend-cov:
	cd {{frontend_dir}} && {{pnpm}} test:coverage

# 全テスト実行（逐次実行、エラー時停止）
test-all: test-backend test-frontend

# 全テスト実行（CI用、watch modeなし）
test-all-ci: test-backend test-frontend-ci

# --- コード品質チェック ---

# バックエンドLint実行（自動修正なし）
lint-backend:
	cd {{backend_dir}} && {{uv}} run ruff check app/

# バックエンドLint実行（自動修正あり）
lint-backend-fix:
	cd {{backend_dir}} && {{uv}} run ruff check --fix app/

# フロントエンドLint実行（自動修正なし）
lint-frontend:
	cd {{frontend_dir}} && {{pnpm}} lint

# フロントエンドLint実行（自動修正あり）
lint-frontend-fix:
	cd {{frontend_dir}} && {{pnpm}} lint:fix

# 全Lint実行
lint-all: lint-backend lint-frontend

# バックエンドフォーマット実行
format-backend:
	cd {{backend_dir}} && {{uv}} run ruff format app/

# フロントエンドフォーマット実行
format-frontend:
	cd {{frontend_dir}} && {{pnpm}} format

# バックエンドフォーマットチェック
format-check-backend:
	cd {{backend_dir}} && {{uv}} run ruff format --check app/

# 全フォーマット実行
format-all: format-backend format-frontend

# バックエンド型チェック
typecheck-backend:
	cd {{backend_dir}} && {{uv}} run pyright app/

# フロントエンド型チェック
typecheck-frontend:
	cd {{frontend_dir}} && {{pnpm}} exec tsc --noEmit

# 全型チェック実行
typecheck-all: typecheck-backend typecheck-frontend

# --- ビルド ---

# フロントエンドビルド
build-frontend:
	cd {{frontend_dir}} && {{pnpm}} build

# --- 依存関係管理 ---

# バックエンド依存関係インストール
install-backend:
	cd {{backend_dir}} && {{uv}} sync

# フロントエンド依存関係インストール
install-frontend:
	cd {{frontend_dir}} && {{pnpm}} install

# 全依存関係インストール
install-all: install-backend install-frontend

# --- コード品質一括チェック（CI/CD向け） ---

# バックエンド品質一括チェック
check-quality-backend: lint-backend format-backend typecheck-backend

# フロントエンド品質一括チェック
check-quality-frontend: lint-frontend format-frontend typecheck-frontend

# 全品質一括チェック
check-quality: check-quality-backend check-quality-frontend

# コミット前品質チェック（フォーマットはチェックのみ）
check-quality-commit: lint-backend format-check-backend lint-frontend typecheck-backend typecheck-frontend

# --- クリーンアップ ---

# バックエンドのキャッシュ・ビルド成果物削除
clean-backend:
	cd {{backend_dir}} && rm -rf __pycache__ .pytest_cache .ruff_cache htmlcov .coverage

# フロントエンドのキャッシュ・ビルド成果物削除
clean-frontend:
	cd {{frontend_dir}} && rm -rf .next node_modules/.cache

# 全クリーンアップ
clean-all: clean-backend clean-frontend

# --- データベース管理 ---

# データベースマイグレーション作成
migrate-create message:
    cd {{backend_dir}} && {{uv}} run alembic revision --autogenerate -m "{{message}}"

# データベースマイグレーション適用
migrate-up:
    cd {{backend_dir}} && {{uv}} run alembic upgrade head

# データベースマイグレーション取り消し
migrate-down:
    cd {{backend_dir}} && {{uv}} run alembic downgrade -1

# データベースマイグレーション履歴表示
migrate-history:
    cd {{backend_dir}} && {{uv}} run alembic history

# データベース現在のリビジョン表示
migrate-current:
    cd {{backend_dir}} && {{uv}} run alembic current

# データベースリセット（開発用）
db-reset:
    cd {{backend_dir}} && {{uv}} run alembic downgrade base && {{uv}} run alembic upgrade head

# --- ドキュメント生成 ---

# OpenAPI仕様書を生成（JSON形式）
docs-generate-openapi:
	cd {{backend_dir}} && {{uv}} run python scripts/generate_openapi.py

# バックエンドドキュメント全体を生成
docs-generate-backend: docs-generate-openapi

# 全ドキュメントを生成
docs-generate: docs-generate-backend
