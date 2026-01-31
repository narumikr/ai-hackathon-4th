# Python 3.12のスリムイメージを使用
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新と必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# uvのインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 依存関係ファイルをコピー
COPY pyproject.toml ./

# 依存関係のインストール（開発依存関係は除外）
RUN uv pip install --system --no-cache .

# アプリケーションコードをコピー
COPY . .

# 非rootユーザーを作成して使用
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Cloud Runのポート（環境変数PORTから取得、デフォルトは8080）
ENV PORT=8080

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')"

# アプリケーションの起動
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
