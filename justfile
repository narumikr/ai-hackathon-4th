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

# --- カテゴリA: 開発サーバー起動 ---

# バックエンド開発サーバー起動（FastAPI）
dev-backend:
    cd {{backend_dir}} && {{uv}} run fastapi dev app/main.py --port {{backend_port}}

# フロントエンド開発サーバー起動（Next.js）
dev-frontend:
    cd {{frontend_dir}} && {{pnpm}} dev

# バックエンド＋フロントエンド同時起動（並列実行）
dev-all:
    @echo "Starting backend and frontend servers..."
    @echo "Backend: http://localhost:{{backend_port}}"
    @echo "Frontend: http://localhost:{{frontend_port}}"
    just dev-backend & just dev-frontend

# --- カテゴリB: テスト実行 ---

# バックエンドテスト実行
test-backend:
    cd {{backend_dir}} && {{uv}} run pytest

# バックエンドテスト実行（カバレッジ付き）
test-backend-cov:
    cd {{backend_dir}} && {{uv}} run pytest --cov=app --cov-report=html

# フロントエンドテスト実行
test-frontend:
    cd {{frontend_dir}} && {{pnpm}} test

# フロントエンドテスト実行（カバレッジ付き）
test-frontend-cov:
    cd {{frontend_dir}} && {{pnpm}} test:coverage

# 全テスト実行（逐次実行、エラー時停止）
test-all: test-backend test-frontend

# --- カテゴリC: コード品質チェック ---

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

# --- カテゴリD: ビルド ---

# フロントエンドビルド
build-frontend:
    cd {{frontend_dir}} && {{pnpm}} build

# --- カテゴリE: 依存関係管理 ---

# バックエンド依存関係インストール
install-backend:
    cd {{backend_dir}} && {{uv}} sync

# フロントエンド依存関係インストール
install-frontend:
    cd {{frontend_dir}} && {{pnpm}} install

# 全依存関係インストール
install-all: install-backend install-frontend

# --- カテゴリF: コード品質一括チェック（CI/CD向け） ---

# バックエンド品質一括チェック
check-quality-backend: lint-backend format-backend typecheck-backend

# フロントエンド品質一括チェック
check-quality-frontend: lint-frontend format-frontend typecheck-frontend

# 全品質一括チェック
check-quality: check-quality-backend check-quality-frontend

# --- カテゴリG: クリーンアップ ---

# バックエンドのキャッシュ・ビルド成果物削除
clean-backend:
    cd {{backend_dir}} && rm -rf __pycache__ .pytest_cache .ruff_cache htmlcov .coverage

# フロントエンドのキャッシュ・ビルド成果物削除
clean-frontend:
    cd {{frontend_dir}} && rm -rf .next node_modules/.cache

# 全クリーンアップ
clean-all: clean-backend clean-frontend
