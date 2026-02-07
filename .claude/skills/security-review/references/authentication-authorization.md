# 認証・認可セキュリティ

## 概要

認証（Authentication）はユーザーの身元を確認するプロセス、認可（Authorization）はユーザーが特定のリソースやアクションにアクセスする権限を持つかを確認するプロセスである。

## 1. 認証のベストプラクティス

### パスワード管理

#### パスワードポリシー

```python
import re

def validate_password(password: str) -> list[str]:
    errors = []
    if len(password) < 12:
        errors.append("Password must be at least 12 characters long")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    return errors
```

#### パスワードハッシュ化

```python
# 推奨: bcrypt or argon2
from passlib.context import CryptContext

# bcrypt（最も広く使われている）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# argon2（より新しく、推奨度が高い）
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

#### 避けるべきハッシュアルゴリズム

| アルゴリズム | 安全性 | 理由 |
|------------|--------|------|
| MD5 | 危険 | 衝突攻撃、高速すぎる |
| SHA-1 | 危険 | 衝突攻撃が実証済み |
| SHA-256（単純） | 不十分 | 高速すぎる（ソルトなし） |
| bcrypt | 推奨 | 適応的コスト、ソルト内蔵 |
| argon2 | 最推奨 | メモリハードネス、最新のPHC推奨 |

### JWT（JSON Web Token）セキュリティ

#### 安全な実装

```python
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = os.environ["JWT_SECRET_KEY"]  # 環境変数から取得
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 短い有効期限
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(user_id: str, roles: list[str]) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "roles": roles,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "jti": secrets.token_urlsafe(16),  # トークンID（リプレイ攻撃対策）
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],  # 使用アルゴリズムを明示的に指定
            options={
                "require": ["sub", "exp", "iat"],  # 必須クレームを指定
            },
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### JWTのセキュリティチェックポイント

- [ ] `algorithm`パラメータを明示的に指定しているか（`"none"`を許可していないか）
- [ ] 有効期限（`exp`）を設定しているか（15分以下を推奨）
- [ ] リフレッシュトークンは安全に保存されているか
- [ ] シークレットキーは十分な長さか（256ビット以上）
- [ ] トークン無効化の仕組みがあるか（ブラックリスト等）

### セッション管理

```python
import secrets
from datetime import timedelta

SESSION_TIMEOUT = timedelta(hours=1)

def create_session(user_id: str) -> str:
    session_id = secrets.token_urlsafe(32)
    # セッションストアに保存
    session_store.set(
        session_id,
        {"user_id": user_id, "created_at": datetime.utcnow().isoformat()},
        ex=int(SESSION_TIMEOUT.total_seconds()),
    )
    return session_id

def regenerate_session(old_session_id: str) -> str:
    """ログイン成功時にセッションIDを再生成（セッション固定攻撃対策）"""
    session_data = session_store.get(old_session_id)
    if session_data:
        session_store.delete(old_session_id)
        return create_session(session_data["user_id"])
    raise HTTPException(status_code=401, detail="Invalid session")
```

### ブルートフォース対策

```python
from datetime import datetime, timedelta

MAX_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=30)
ATTEMPT_WINDOW = timedelta(minutes=15)

class LoginAttemptTracker:
    def __init__(self, store):
        self.store = store

    async def check_and_record(self, identifier: str) -> None:
        key = f"login_attempts:{identifier}"
        attempts = self.store.get(key)

        if attempts and attempts["count"] >= MAX_ATTEMPTS:
            locked_until = datetime.fromisoformat(attempts["locked_until"])
            if datetime.utcnow() < locked_until:
                remaining = (locked_until - datetime.utcnow()).seconds
                raise HTTPException(
                    status_code=429,
                    detail=f"Account locked. Try again in {remaining} seconds",
                )
            # ロックアウト期間が過ぎた場合はリセット
            self.store.delete(key)

    async def record_failure(self, identifier: str) -> None:
        key = f"login_attempts:{identifier}"
        attempts = self.store.get(key) or {"count": 0}
        attempts["count"] += 1

        if attempts["count"] >= MAX_ATTEMPTS:
            attempts["locked_until"] = (
                datetime.utcnow() + LOCKOUT_DURATION
            ).isoformat()

        self.store.set(key, attempts, ex=int(ATTEMPT_WINDOW.total_seconds()))

    async def reset(self, identifier: str) -> None:
        self.store.delete(f"login_attempts:{identifier}")
```

## 2. 認可のベストプラクティス

### RBAC（Role-Based Access Control）

```python
from enum import Enum
from functools import wraps

class Role(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

ROLE_PERMISSIONS = {
    Role.ADMIN: {"read", "write", "delete", "manage_users"},
    Role.EDITOR: {"read", "write"},
    Role.VIEWER: {"read"},
}

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            user_permissions = ROLE_PERMISSIONS.get(current_user.role, set())
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission '{permission}' required",
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

@router.delete("/documents/{doc_id}")
@require_permission("delete")
async def delete_document(doc_id: str, current_user: User):
    ...
```

### ABAC（Attribute-Based Access Control）

```python
class AccessPolicy:
    def __init__(self, rules: list[dict]):
        self.rules = rules

    def evaluate(self, subject: dict, resource: dict, action: str) -> bool:
        for rule in self.rules:
            if self._matches(rule, subject, resource, action):
                return rule["effect"] == "allow"
        return False  # デフォルト拒否

    def _matches(self, rule: dict, subject: dict, resource: dict, action: str) -> bool:
        if rule.get("action") and action not in rule["action"]:
            return False
        if rule.get("subject_role") and subject.get("role") not in rule["subject_role"]:
            return False
        if rule.get("resource_owner"):
            if resource.get("owner_id") != subject.get("id"):
                return False
        return True

# 使用例
policy = AccessPolicy([
    {
        "effect": "allow",
        "action": ["read", "update", "delete"],
        "resource_owner": True,  # 自分のリソースのみ
    },
    {
        "effect": "allow",
        "action": ["read", "update", "delete"],
        "subject_role": ["admin"],  # 管理者はすべてのリソース
    },
])
```

### IDOR（Insecure Direct Object Reference）防止

```python
# Bad: IDORの脆弱性
@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str, current_user: User = Depends(get_current_user)):
    return repository.find(invoice_id)  # 他人の請求書も取得できる

# Good: リソース所有者の検証
@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str, current_user: User = Depends(get_current_user)):
    invoice = repository.find(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404)
    if invoice.user_id != current_user.id and not current_user.has_role("admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    return invoice

# Better: クエリレベルでフィルタリング
@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str, current_user: User = Depends(get_current_user)):
    invoice = repository.find_by_id_and_user(invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404)
    return invoice
```

## 3. OAuth 2.0 / OIDC セキュリティ

### 安全なOAuth 2.0フロー

```python
# Authorization Code Flow with PKCE（推奨）
import hashlib
import base64

def generate_pkce_pair():
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode()
    return code_verifier, code_challenge
```

### チェックポイント

- [ ] Authorization Code Flow（+ PKCE）を使用しているか
- [ ] `state`パラメータでCSRF対策をしているか
- [ ] リダイレクトURIを厳密にバリデーションしているか
- [ ] トークンをURLパラメータに含めていないか
- [ ] Implicit Flowを使用していないか（非推奨）

## 4. API認証セキュリティ

### APIキー管理

```python
# APIキーのセキュアな生成
def generate_api_key() -> str:
    return f"sk_{secrets.token_urlsafe(32)}"  # プレフィックスで識別しやすくする

# APIキーのハッシュ保存（平文で保存しない）
def store_api_key(api_key: str) -> str:
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    # key_hashをデータベースに保存
    return key_hash

def verify_api_key(api_key: str) -> bool:
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return repository.find_by_hash(key_hash) is not None
```

## チェックリスト

### 認証
- [ ] パスワードはbcrypt/argon2でハッシュ化されているか
- [ ] パスワードポリシーは適切か（12文字以上、複雑性要件）
- [ ] ブルートフォース対策（アカウントロックアウト）を実装しているか
- [ ] セッションIDはログイン成功時に再生成されているか
- [ ] JWTの有効期限は短く設定されているか（15分以下）
- [ ] JWTのアルゴリズムを明示的に指定しているか

### 認可
- [ ] すべてのエンドポイントで認可チェックを実施しているか
- [ ] IDOR対策（リソース所有者チェック）を実施しているか
- [ ] デフォルト拒否の方針を採用しているか
- [ ] サーバーサイドで認可判定を行っているか

### セッション/トークン
- [ ] セッションCookieにhttponly、secure、samesite属性を設定しているか
- [ ] トークンの無効化（ログアウト時）の仕組みがあるか
- [ ] リフレッシュトークンは安全に保存されているか
