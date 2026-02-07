# OWASP Top 10（2021）

## 概要

OWASP Top 10は、Webアプリケーションにおける最も重大なセキュリティリスクを示すリストである。セキュリティレビューの基準として広く参照される。

## A01: アクセス制御の不備（Broken Access Control）

### 説明

ユーザーが本来アクセスすべきでないリソースやアクションにアクセスできてしまう脆弱性。

### 主な脆弱性パターン

- 他のユーザーのリソースへの不正アクセス（IDOR）
- 管理者機能への無認可アクセス
- URLやパラメータの操作によるアクセス制御の迂回
- APIの認可チェック漏れ

### 対策

```python
# IDOR対策: リソース所有者の検証
@router.get("/documents/{doc_id}")
def get_document(doc_id: str, current_user: User = Depends(get_current_user)):
    document = repository.find(doc_id)
    if not document:
        raise HTTPException(status_code=404)
    if document.owner_id != current_user.id and not current_user.has_role("admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    return document

# 認可デコレータの活用
def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if not current_user.has_permission(permission):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

### チェックポイント

- [ ] すべてのエンドポイントで認可チェックを実施しているか
- [ ] リソースの所有者チェックを実施しているか
- [ ] ロールベースのアクセス制御が適切に設定されているか
- [ ] サーバーサイドで認可判定を行っているか（クライアントサイドのみに依存していないか）

## A02: 暗号化の失敗（Cryptographic Failures）

### 説明

暗号化に関する不備により、機密データが露出する脆弱性。

### 主な脆弱性パターン

- 平文でのパスワード保存
- 弱い暗号化アルゴリズムの使用（MD5, SHA-1）
- ハードコーディングされた暗号鍵
- HTTP（非暗号化通信）の使用
- 不適切なTLS設定

### 対策

```python
# パスワードのハッシュ化（bcrypt使用）
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 機密データの暗号化
from cryptography.fernet import Fernet

def encrypt_sensitive_data(data: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()
```

### チェックポイント

- [ ] パスワードはbcrypt/argon2でハッシュ化されているか
- [ ] 暗号化キーは環境変数から取得しているか
- [ ] HTTPS通信を強制しているか
- [ ] 弱い暗号アルゴリズム（MD5, SHA-1）を使用していないか
- [ ] 保存時の暗号化が必要なデータは暗号化されているか

## A03: インジェクション（Injection）

### 説明

外部入力がクエリやコマンドの一部として解釈され、意図しない操作が実行される脆弱性。

### 主な脆弱性パターン

- SQLインジェクション
- NoSQLインジェクション
- OSコマンドインジェクション
- LDAPインジェクション
- XSS（クロスサイトスクリプティング）
- テンプレートインジェクション（SSTI）

### 対策

```python
# SQLインジェクション対策
# Bad
query = f"SELECT * FROM users WHERE email = '{email}'"

# Good: パラメータ化クエリ
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# Good: ORM
user = session.query(User).filter(User.email == email).first()

# XSS対策
import html

def sanitize_output(value: str) -> str:
    return html.escape(value)

# OSコマンドインジェクション対策
# Bad
os.system(f"ls {user_input}")

# Good
subprocess.run(["ls", user_input], check=True, capture_output=True)
```

### チェックポイント

- [ ] 外部入力を直接SQL文に組み込んでいないか
- [ ] ORM またはパラメータ化クエリを使用しているか
- [ ] HTML出力時にエスケープを行っているか
- [ ] OSコマンドの実行時にシェル展開を避けているか
- [ ] テンプレートエンジンでユーザー入力を適切に処理しているか

## A04: 安全でない設計（Insecure Design）

### 説明

設計段階でのセキュリティ考慮不足に起因する脆弱性。実装の問題ではなく、設計そのものの問題。

### 主な脆弱性パターン

- 脅威モデリングの欠如
- ビジネスロジックの悪用
- レート制限の欠如
- 多要素認証の未実装

### 対策

- 設計段階で脅威モデリング（STRIDE）を実施する
- ビジネスロジックの境界条件をテストする
- レート制限やアカウントロックアウトを設計に組み込む
- セキュリティ要件を非機能要件として明文化する

### チェックポイント

- [ ] 脅威モデリングを実施したか
- [ ] ビジネスロジックの悪用シナリオを検討したか
- [ ] レート制限を設計に含めているか
- [ ] セキュリティ要件が明文化されているか

## A05: セキュリティ設定のミス（Security Misconfiguration）

### 説明

デフォルト設定の放置、不完全な設定、不要な機能の有効化などによる脆弱性。

### 主な脆弱性パターン

- デバッグモードの本番有効化
- デフォルトの認証情報
- 不要なポート・サービスの公開
- 過度に許容的なCORS設定
- セキュリティヘッダーの欠如
- ディレクトリリスティングの有効化

### 対策

```python
# 環境別設定
class Settings(BaseSettings):
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["https://app.example.com"]
    SECRET_KEY: str  # 必須（デフォルト値なし）

    class Config:
        env_file = ".env"

settings = Settings()

# 本番環境用セキュリティ設定
app = FastAPI(debug=settings.DEBUG, docs_url=None if not settings.DEBUG else "/docs")
```

### チェックポイント

- [ ] デフォルトの認証情報を変更しているか
- [ ] デバッグモードは本番で無効化されているか
- [ ] CORS設定は適切か
- [ ] 不要なエンドポイントやサービスを無効化しているか
- [ ] セキュリティヘッダーを設定しているか

## A06: 脆弱で古いコンポーネント（Vulnerable and Outdated Components）

### 説明

既知の脆弱性を含むライブラリやフレームワークを使用する脆弱性。

### 対策

```bash
# Python: 脆弱性スキャン
pip-audit
safety check

# Node.js: 脆弱性スキャン
npm audit
npx audit-ci

# 汎用: Dependabot / Renovateの設定
# .github/dependabot.yml
```

### チェックポイント

- [ ] 依存ライブラリの脆弱性を定期的にスキャンしているか
- [ ] ロックファイルが管理されているか
- [ ] サポート切れのライブラリを使用していないか
- [ ] 自動更新の仕組みがあるか（Dependabot等）

## A07: 識別と認証の失敗（Identification and Authentication Failures）

### 説明

認証メカニズムの実装不備により、攻撃者がユーザーIDを不正に取得できる脆弱性。

### 主な脆弱性パターン

- ブルートフォース攻撃への耐性不足
- 弱いパスワードポリシー
- セッション固定攻撃
- クレデンシャルスタッフィング

### 対策

```python
# アカウントロックアウト
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=30)

async def login(username: str, password: str):
    attempts = await get_failed_attempts(username)
    if attempts >= MAX_LOGIN_ATTEMPTS:
        lockout_until = await get_lockout_until(username)
        if datetime.utcnow() < lockout_until:
            raise HTTPException(status_code=429, detail="Account temporarily locked")

    user = await authenticate(username, password)
    if not user:
        await increment_failed_attempts(username)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    await reset_failed_attempts(username)
    return create_access_token(user)
```

### チェックポイント

- [ ] ブルートフォース対策（アカウントロックアウト、レート制限）を実装しているか
- [ ] パスワードポリシーは適切か（最小長、複雑性）
- [ ] セッションIDはログイン成功時に再生成されているか
- [ ] 多要素認証をサポートしているか

## A08: ソフトウェアとデータの整合性の不具合（Software and Data Integrity Failures）

### 説明

コードやデータの整合性を検証しないことに起因する脆弱性。

### 主な脆弱性パターン

- 信頼できないソースからのデシリアライゼーション
- CI/CDパイプラインの整合性チェック不足
- 署名なしのソフトウェアアップデート

### 対策

```python
# 安全でないデシリアライゼーションの回避
# Bad: pickleの使用
import pickle
data = pickle.loads(user_input)  # 任意コード実行の危険

# Good: JSON等の安全な形式を使用
import json
data = json.loads(user_input)

# JWTの署名検証
import jwt
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
except jwt.InvalidSignatureError:
    raise HTTPException(status_code=401, detail="Invalid token signature")
```

### チェックポイント

- [ ] pickleなど安全でないデシリアライゼーションを使用していないか
- [ ] JWTの署名を検証しているか
- [ ] CI/CDパイプラインのアクセス制御は適切か
- [ ] 依存ライブラリの整合性を検証しているか

## A09: セキュリティログとモニタリングの不備（Security Logging and Monitoring Failures）

### 説明

セキュリティイベントの記録不足により、攻撃の検知と対応が遅れる脆弱性。

### 対策

```python
import logging
import structlog

logger = structlog.get_logger()

# セキュリティイベントのログ記録
async def login(request: LoginRequest):
    user = await authenticate(request.username, request.password)
    if not user:
        logger.warning(
            "authentication_failed",
            username=request.username,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
        )
        raise HTTPException(status_code=401)

    logger.info(
        "authentication_success",
        user_id=user.id,
        ip_address=request.client.host,
    )
    return create_access_token(user)
```

### チェックポイント

- [ ] 認証成功・失敗をログに記録しているか
- [ ] 認可失敗をログに記録しているか
- [ ] ログに機密情報を含めていないか
- [ ] ログの集約と分析の仕組みがあるか
- [ ] アラート設定はされているか

## A10: サーバーサイドリクエストフォージェリ（Server-Side Request Forgery: SSRF）

### 説明

サーバーが外部から指定されたURLにリクエストを送信させられる脆弱性。内部ネットワークへのアクセスやクラウドメタデータの取得に悪用される。

### 対策

```python
from urllib.parse import urlparse
import ipaddress

ALLOWED_HOSTS = ["api.example.com", "cdn.example.com"]
BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # メタデータエンドポイント
]

def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_HOSTS:
        return False
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        for network in BLOCKED_NETWORKS:
            if ip in network:
                return False
    except ValueError:
        pass  # ホスト名の場合
    return True
```

### チェックポイント

- [ ] ユーザー指定のURLにリクエストを送信する機能があるか
- [ ] URLのホワイトリスト検証を実施しているか
- [ ] 内部ネットワークへのアクセスをブロックしているか
- [ ] クラウドメタデータエンドポイントへのアクセスをブロックしているか

## まとめ

OWASP Top 10は定期的に更新される。最新の脅威動向を把握し、継続的にセキュリティ対策を見直すことが重要である。レビュー時は、対象システムの特性に応じて重点的にチェックする項目を選択する。
