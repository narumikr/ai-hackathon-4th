# インフラセキュリティ

## 概要

インフラセキュリティは、アプリケーションの実行環境やデプロイメント構成に関するセキュリティ対策である。セキュリティヘッダー、CORS設定、コンテナセキュリティ、CI/CDパイプラインの保護を含む。

## 1. セキュリティヘッダー

### 推奨ヘッダー一覧

| ヘッダー | 値 | 目的 |
|----------|-----|------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | HTTPS強制 |
| `X-Content-Type-Options` | `nosniff` | MIMEスニッフィング防止 |
| `X-Frame-Options` | `DENY` | クリックジャッキング防止 |
| `Content-Security-Policy` | 後述 | XSS等の防止 |
| `X-XSS-Protection` | `0` | ブラウザのXSSフィルター無効化（CSP推奨） |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | リファラー情報の制限 |
| `Permissions-Policy` | `camera=(), microphone=()` | ブラウザ機能の制限 |

### FastAPIでの実装

```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )
    return response
```

### Content-Security-Policy（CSP）

```python
# 開発環境
CSP_DEV = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # 開発ツール用
    "style-src 'self' 'unsafe-inline'; "
    "connect-src 'self' ws://localhost:*"  # WebSocket（HMR用）
)

# 本番環境（厳密）
CSP_PROD = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' https://cdn.example.com; "
    "font-src 'self'; "
    "connect-src 'self' https://api.example.com; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)
```

## 2. CORS設定

### 本番環境のCORS設定

```python
from fastapi.middleware.cors import CORSMiddleware

# Bad: 全開放
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Good: 厳密な設定
CORS_CONFIG = {
    "production": {
        "allow_origins": ["https://app.example.com"],
        "allow_methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Authorization", "Content-Type"],
        "allow_credentials": True,
        "max_age": 600,
    },
    "development": {
        "allow_origins": ["http://localhost:3000", "http://localhost:5173"],
        "allow_methods": ["*"],
        "allow_headers": ["*"],
        "allow_credentials": True,
    },
}

config = CORS_CONFIG[settings.ENVIRONMENT]
app.add_middleware(CORSMiddleware, **config)
```

### チェックポイント

- [ ] 本番環境で `allow_origins=["*"]` を使用していないか
- [ ] `allow_credentials=True` の場合、`allow_origins` にワイルドカードを使用していないか
- [ ] 不要なHTTPメソッドを許可していないか
- [ ] `max_age` を適切に設定しているか

## 3. レート制限

### アプリケーションレベル

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# エンドポイント別のレート制限
@router.post("/auth/login")
@limiter.limit("5/minute")  # ログイン: 1分に5回まで
async def login(request: Request, credentials: LoginRequest):
    ...

@router.post("/api/v1/resources")
@limiter.limit("30/minute")  # 一般API: 1分に30回まで
async def create_resource(request: Request, data: CreateResourceRequest):
    ...

@router.get("/api/v1/resources")
@limiter.limit("100/minute")  # 読み取り: 1分に100回まで
async def list_resources(request: Request):
    ...
```

### レスポンスヘッダー

```python
# レート制限情報をヘッダーに含める
response.headers["X-RateLimit-Limit"] = "100"
response.headers["X-RateLimit-Remaining"] = "95"
response.headers["X-RateLimit-Reset"] = "1706616000"
```

## 4. コンテナセキュリティ

### Dockerfile のベストプラクティス

```dockerfile
# 軽量なベースイメージを使用
FROM python:3.12-slim AS base

# rootユーザーで実行しない
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# 依存関係を先にコピー（キャッシュ活用）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY --chown=appuser:appuser . .

# 非rootユーザーに切り替え
USER appuser

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### チェックポイント

- [ ] rootユーザーで実行していないか
- [ ] 軽量なベースイメージを使用しているか
- [ ] 不要なパッケージをインストールしていないか
- [ ] マルチステージビルドを使用しているか
- [ ] `.dockerignore`で不要なファイルを除外しているか
- [ ] シークレットをイメージに含めていないか

## 5. CI/CDパイプラインセキュリティ

### GitHub Actionsのセキュリティ

```yaml
# .github/workflows/security.yml
name: Security Checks

on:
  pull_request:
    branches: [main]

permissions:
  contents: read  # 最小権限

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 依存関係の脆弱性スキャン
      - name: Run dependency audit
        run: pip-audit -r requirements.txt

      # シークレットの検出
      - name: Scan for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./

      # SAST（静的アプリケーションセキュリティテスト）
      - name: Run Bandit (Python SAST)
        run: bandit -r src/ -f json -o bandit-report.json

      # コンテナイメージのスキャン
      - name: Scan Docker image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:latest
          format: table
          severity: CRITICAL,HIGH
```

### チェックポイント

- [ ] CI/CDパイプラインに脆弱性スキャンを含めているか
- [ ] シークレット検出ツールを使用しているか
- [ ] GitHub Actionsのpermissionsを最小限に設定しているか
- [ ] サードパーティActionのバージョンをピン止めしているか
- [ ] シークレットをGitHub Secretsに保存しているか

## 6. 依存関係管理

### 脆弱性スキャン

```bash
# Python
pip-audit                    # PyPI脆弱性データベース
safety check                 # Safety DB

# Node.js
npm audit                    # npm脆弱性データベース
npx audit-ci --critical      # CI用（criticalのみ失敗）

# 汎用
trivy fs .                   # Trivyによるファイルシステムスキャン
```

### Dependabot設定

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: pip
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 10
    reviewers:
      - security-team

  - package-ecosystem: npm
    directory: /frontend
    schedule:
      interval: weekly

  - package-ecosystem: docker
    directory: /
    schedule:
      interval: weekly

  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
```

## 7. 環境別設定

### 設定管理のベストプラクティス

```python
from pydantic_settings import BaseSettings
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    SECRET_KEY: str
    DATABASE_URL: str
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # 本番環境のバリデーション
    def validate_production(self):
        if self.ENVIRONMENT == Environment.PRODUCTION:
            assert not self.DEBUG, "DEBUG must be False in production"
            assert "localhost" not in str(self.ALLOWED_ORIGINS), \
                "localhost must not be in ALLOWED_ORIGINS in production"
            assert len(self.SECRET_KEY) >= 32, \
                "SECRET_KEY must be at least 32 characters in production"

    class Config:
        env_file = ".env"
```

## 8. ネットワークセキュリティ

### ファイアウォール設定の原則

- デフォルト拒否（Deny All）の方針
- 必要なポートのみ開放
- 内部サービス間通信はプライベートネットワークで実施
- データベースをパブリックネットワークに公開しない

### リバースプロキシ設定

```nginx
# Nginx設定例
server {
    listen 443 ssl http2;
    server_name api.example.com;

    # TLS設定
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    # セキュリティヘッダー
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;

    # リクエストサイズ制限
    client_max_body_size 10m;

    # レート制限
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend:8000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## チェックリスト

### セキュリティヘッダー
- [ ] HSTS、X-Content-Type-Options、X-Frame-Optionsを設定しているか
- [ ] Content-Security-Policyを適切に設定しているか
- [ ] Referrer-Policyを設定しているか

### CORS
- [ ] 本番環境でオリジンを限定しているか
- [ ] 不要なメソッド・ヘッダーを許可していないか

### コンテナ
- [ ] 非rootユーザーで実行しているか
- [ ] イメージにシークレットを含めていないか
- [ ] イメージの脆弱性スキャンを実施しているか

### CI/CD
- [ ] セキュリティスキャンをパイプラインに含めているか
- [ ] シークレット検出を自動化しているか
- [ ] 依存関係の自動更新を設定しているか

### ネットワーク
- [ ] デフォルト拒否のファイアウォールポリシーを採用しているか
- [ ] データベースをパブリックネットワークから隔離しているか
- [ ] TLS 1.2以上を強制しているか
