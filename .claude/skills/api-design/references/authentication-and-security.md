# 認証とセキュリティ

## 概要

APIセキュリティは、不正アクセスやデータ漏洩を防ぐために不可欠である。認証、認可、暗号化、入力バリデーション、レート制限などの対策を適切に実装する必要がある。

## 認証方式

### Bearer Token（JWT）

**概要**: JSON Web Token（JWT）を使用した認証。最も一般的な方式。

**実装例**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """JWTトークンを検証する"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

@router.get("/travel-plans")
def list_travel_plans(user: dict = Depends(verify_token)):
    """旅行計画一覧を取得する（認証必須）"""
    user_id = user["sub"]
    ...
```

**リクエスト例**:
```
GET /api/v1/travel-plans
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**メリット**:
- ステートレス（サーバーでセッション管理不要）
- 複数サービス間で共有可能
- 有効期限を設定できる

**デメリット**:
- トークンを取り消せない（有効期限まで有効）
- トークンサイズが大きい

### OAuth 2.0

**概要**: サードパーティ認証プロバイダを使用した認証。

**実装例**:
```python
from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://provider.com/oauth/authorize",
    tokenUrl="https://provider.com/oauth/token",
)

@router.get("/travel-plans")
def list_travel_plans(token: str = Depends(oauth2_scheme)):
    """旅行計画一覧を取得する（OAuth 2.0認証）"""
    # トークンを検証
    user = verify_oauth_token(token)
    ...
```

**メリット**:
- サードパーティ認証（Google、GitHub など）
- スコープベースの権限管理
- リフレッシュトークンによる長期認証

**デメリット**:
- 実装が複雑
- サードパーティへの依存

### API Key

**概要**: APIキーを使用した認証。シンプルだが安全性は低い。

**実装例**:
```python
from fastapi import Header, HTTPException, status

def verify_api_key(api_key: str = Header(..., alias="X-API-Key")):
    """APIキーを検証する"""
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return api_key

@router.get("/travel-plans")
def list_travel_plans(api_key: str = Depends(verify_api_key)):
    """旅行計画一覧を取得する（APIキー認証）"""
    ...
```

**リクエスト例**:
```
GET /api/v1/travel-plans
X-API-Key: your-api-key-here
```

**メリット**:
- 実装がシンプル
- マシン間通信に適している

**デメリット**:
- 有効期限がない（手動で取り消す必要がある）
- キーが漏洩すると危険
- ユーザー固有の権限管理が難しい

## 認可パターン

### RBAC（Role-Based Access Control）

**概要**: ユーザーの役割（Role）に基づいてアクセス制御を行う。

**実装例**:
```python
from functools import wraps
from fastapi import HTTPException, status

def require_role(*allowed_roles: str):
    """指定された役割を持つユーザーのみアクセスを許可する"""
    def decorator(func):
        @wraps(func)
        def wrapper(user: dict = Depends(verify_token), *args, **kwargs):
            if user.get("role") not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this resource",
                )
            return func(user, *args, **kwargs)
        return wrapper
    return decorator

@router.delete("/travel-plans/{plan_id}")
@require_role("admin", "moderator")
def delete_travel_plan(plan_id: str, user: dict):
    """旅行計画を削除する（管理者・モデレーターのみ）"""
    ...
```

### スコープベース認可

**概要**: OAuth 2.0のスコープを使用したアクセス制御。

**実装例**:
```python
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_scopes(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
):
    """スコープを検証する"""
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    token_scopes = payload.get("scopes", [])

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required scope: {scope}",
            )
    return payload

@router.delete("/travel-plans/{plan_id}")
def delete_travel_plan(
    plan_id: str,
    user: dict = Security(verify_scopes, scopes=["travel-plans:delete"]),
):
    """旅行計画を削除する（travel-plans:deleteスコープ必須）"""
    ...
```

## セキュリティヘッダー

### HTTPS必須化

すべてのAPI通信はHTTPSを使用する。

**実装例**:
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# 本番環境でのみ有効化
if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### セキュリティヘッダーの設定

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# 信頼できるホストのみ許可
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"],
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    """セキュリティヘッダーを追加する"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

## CORS設定

### CORS（Cross-Origin Resource Sharing）

**実装例**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],  # 本番環境では厳密に設定
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**プロジェクト実装例**:
```python
# backend/app/interfaces/middleware.py (推定)
def setup_cors(app: FastAPI):
    """CORSミドルウェアの設定"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 開発環境用（本番では厳密に設定）
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

## レート制限（Rate Limiting）

### リクエスト数の制限

**実装例**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/travel-plans")
@limiter.limit("10/minute")
def create_travel_plan(request: Request, ...):
    """旅行計画を作成する（1分間に10回まで）"""
    ...
```

**レスポンス例（レート制限超過）**:
```
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "detail": "Rate limit exceeded: 10 per 1 minute"
}
```

## 入力バリデーション

### Pydanticバリデーション

**実装例**:
```python
from pydantic import BaseModel, Field, field_validator

class CreateTravelPlanRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    destination: str = Field(..., min_length=1, max_length=200)

    @field_validator("user_id", "title", "destination")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """空文字列でないことを検証する"""
        if not value.strip():
            raise ValueError("must not be empty")
        return value
```

**プロジェクト実装例**:
```python
# backend/app/interfaces/schemas/travel_plan.py:37-43
@field_validator("user_id", "title", "destination")
@classmethod
def validate_not_empty(cls, value: str) -> str:
    """空文字列でないことを検証する"""
    if not value.strip():
        raise ValueError("must not be empty")
    return value
```

### SQLインジェクション対策

ORMを使用し、直接SQL文字列を構築しない。

**悪い例**:
```python
# SQLインジェクションの脆弱性
query = f"SELECT * FROM travel_plans WHERE user_id = '{user_id}'"
```

**良い例**:
```python
# ORMを使用（安全）
from sqlalchemy import select

stmt = select(TravelPlan).where(TravelPlan.user_id == user_id)
result = session.execute(stmt)
```

### XSS（Cross-Site Scripting）対策

入力値をエスケープし、HTMLタグを含めない。

**実装例**:
```python
import html

class CreateTravelPlanRequest(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def escape_html(cls, value: str) -> str:
        """HTMLタグをエスケープする"""
        return html.escape(value)
```

## パスワード管理

### パスワードハッシュ化

**実装例**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """パスワードをハッシュ化する"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワードを検証する"""
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/users")
def create_user(request: CreateUserRequest):
    """ユーザーを作成する（パスワードはハッシュ化して保存）"""
    hashed_password = hash_password(request.password)
    # ハッシュ化されたパスワードを保存
    ...
```

## セキュリティチェックリスト

APIをリリースする前に、以下の項目を確認する:

- [ ] すべてのエンドポイントで認証を実装しているか?
- [ ] 認可（権限チェック）を実装しているか?
- [ ] HTTPS通信を使用しているか?
- [ ] セキュリティヘッダーを設定しているか?
- [ ] CORS設定は適切か（本番環境で`allow_origins=["*"]`を使用していないか）?
- [ ] レート制限を実装しているか?
- [ ] 入力バリデーションを実装しているか?
- [ ] SQLインジェクション対策を実施しているか（ORMを使用しているか）?
- [ ] XSS対策を実施しているか（入力値をエスケープしているか）?
- [ ] パスワードをハッシュ化して保存しているか?
- [ ] 機密情報（パスワード、APIキー）をログに出力していないか?
- [ ] エラーメッセージに機密情報を含めていないか?

## まとめ

APIセキュリティのポイント:

1. **認証**: Bearer Token（JWT）、OAuth 2.0、API Keyから適切な方式を選択
2. **認可**: RBAC、スコープベース認可で権限管理
3. **HTTPS**: すべての通信をHTTPSで暗号化
4. **セキュリティヘッダー**: X-Content-Type-Options、X-Frame-Optionsなどを設定
5. **CORS**: 本番環境では厳密に設定
6. **レート制限**: リクエスト数を制限してDDoS攻撃を防ぐ
7. **入力バリデーション**: Pydanticでバリデーション、SQLインジェクション・XSS対策
8. **パスワード管理**: ハッシュ化して保存

これらの対策を適切に実装することで、安全なAPIを構築できる。
