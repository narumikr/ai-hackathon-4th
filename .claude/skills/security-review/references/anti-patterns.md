# セキュリティ アンチパターン

## 概要

ソフトウェア開発において頻繁に見られるセキュリティ上のアンチパターンを示す。これらのパターンは脆弱性の原因となり、攻撃の対象となる。

## 1. シークレットのハードコーディング

### アンチパターン

```python
# APIキーをソースコードに直接記述
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://admin:password123@db.example.com/production"
JWT_SECRET = "my-jwt-secret"
```

### 問題点

- ソースコード管理システム（Git）にシークレットがコミットされる
- コードにアクセスできる全員がシークレットを取得できる
- シークレットの変更にコード変更とデプロイが必要
- 環境ごとに異なるシークレットを使用できない

### 正しい設計

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEY: str
    DATABASE_URL: str
    JWT_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()
```

## 2. エラーメッセージでの情報露出

### アンチパターン

```python
@router.post("/login")
def login(request: LoginRequest):
    user = repository.find_by_email(request.email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")  # ユーザーの存在を漏洩
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong password")  # パスワードが間違いと特定

@router.get("/users/{user_id}")
def get_user(user_id: str):
    try:
        user = repository.find(user_id)
        return user
    except Exception as e:
        # スタックトレースや内部情報を露出
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
```

### 問題点

- ユーザー列挙攻撃（ユーザーの存在確認）が可能
- 内部のデータベース構造やシステム情報が漏洩
- 攻撃者が詳細なエラーメッセージを利用して攻撃を精緻化

### 正しい設計

```python
@router.post("/login")
def login(request: LoginRequest):
    user = repository.find_by_email(request.email)
    if not user or not verify_password(request.password, user.password_hash):
        # 同一のエラーメッセージ（ユーザー列挙攻撃を防止）
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/users/{user_id}")
def get_user(user_id: str):
    try:
        user = repository.find(user_id)
        return user
    except Exception as e:
        logger.error(f"Failed to fetch user {user_id}: {e}")  # ログには記録
        raise HTTPException(status_code=500, detail="Internal server error")  # 汎用メッセージ
```

## 3. 認可チェックの漏れ（IDOR）

### アンチパターン

```python
# 認証はあるが、認可チェックがない
@router.get("/orders/{order_id}")
def get_order(order_id: str, current_user: User = Depends(get_current_user)):
    # どのユーザーでも任意の注文を閲覧できる
    return repository.find(order_id)

@router.put("/users/{user_id}/email")
def update_email(user_id: str, request: UpdateEmailRequest, current_user: User = Depends(get_current_user)):
    # 他のユーザーのメールアドレスを変更できる
    repository.update_email(user_id, request.email)
```

### 問題点

- 他のユーザーのリソースに不正アクセス可能
- URLのIDを変更するだけで攻撃が成立
- 水平権限昇格（同一権限レベルの他ユーザーリソースへのアクセス）

### 正しい設計

```python
@router.get("/orders/{order_id}")
def get_order(order_id: str, current_user: User = Depends(get_current_user)):
    order = repository.find(order_id)
    if not order:
        raise HTTPException(status_code=404)
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return order

@router.put("/users/{user_id}/email")
def update_email(user_id: str, request: UpdateEmailRequest, current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    repository.update_email(user_id, request.email)
```

## 4. 不適切なCORS設定

### アンチパターン

```python
# 本番環境で全オリジンを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # 全オリジン + credentials は特に危険
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 問題点

- 任意のオリジンからの認証付きリクエストを許可
- CSRF攻撃のリスクが増大
- 機密データが意図しないオリジンから取得可能

### 正しい設計

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com", "https://admin.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## 5. SQLクエリの文字列連結

### アンチパターン

```python
# ユーザー入力を直接SQL文に埋め込む
def search_users(name: str):
    query = f"SELECT * FROM users WHERE name LIKE '%{name}%'"
    cursor.execute(query)
    return cursor.fetchall()

# フィルター条件の動的構築
def get_users(filters: dict):
    conditions = []
    for key, value in filters.items():
        conditions.append(f"{key} = '{value}'")
    query = f"SELECT * FROM users WHERE {' AND '.join(conditions)}"
    cursor.execute(query)
```

### 問題点

- SQLインジェクションにより任意のSQL文を実行可能
- データの読み取り、変更、削除が可能
- 最悪の場合、OSコマンド実行も可能

### 正しい設計

```python
# パラメータ化クエリ
def search_users(name: str):
    cursor.execute(
        "SELECT * FROM users WHERE name LIKE %s",
        (f"%{name}%",),
    )
    return cursor.fetchall()

# ORMの使用
def get_users(filters: dict):
    stmt = select(User)
    allowed_fields = {"name", "email", "status"}
    for key, value in filters.items():
        if key in allowed_fields:
            stmt = stmt.where(getattr(User, key) == value)
    return session.execute(stmt).scalars().all()
```

## 6. フェイルオープン

### アンチパターン

```python
# エラー時にアクセスを許可してしまう
def check_permission(user_id: str, resource_id: str) -> bool:
    try:
        result = permission_service.check(user_id, resource_id)
        return result.allowed
    except Exception:
        return True  # エラー時にアクセスを許可

# 認証エラーを無視
def get_current_user(token: str = Header(None)):
    if not token:
        return None  # 未認証ユーザーとして続行
    try:
        return verify_token(token)
    except Exception:
        return None  # トークン検証失敗でも続行
```

### 問題点

- サービス障害時に認可が迂回される
- エラーハンドリングの不備が認証迂回に直結
- 意図しないアクセス許可が発生

### 正しい設計（フェイルクローズ）

```python
# エラー時はアクセスを拒否
def check_permission(user_id: str, resource_id: str) -> bool:
    try:
        result = permission_service.check(user_id, resource_id)
        return result.allowed
    except Exception as e:
        logger.error(f"Permission check failed: {e}")
        return False  # エラー時はアクセスを拒否

# 認証を必須とする
def get_current_user(token: str = Header(...)):  # 必須パラメータ
    try:
        return verify_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## 7. クライアントサイド検証のみ

### アンチパターン

```javascript
// フロントエンドのみでバリデーション
function submitForm(data) {
    if (data.age < 0 || data.age > 150) {
        alert("Invalid age");
        return;
    }
    fetch("/api/users", { method: "POST", body: JSON.stringify(data) });
}
```

```python
# バックエンドにバリデーションなし
@router.post("/users")
def create_user(request: dict):
    repository.create(request)  # バリデーションなし
```

### 問題点

- クライアントサイドのバリデーションは簡単に迂回できる
- curlやPostman等でバリデーションなしにリクエスト送信可能
- XSSやインジェクション攻撃の入口になる

### 正しい設計

```python
# サーバーサイドでバリデーション（クライアントサイドはUXのため）
class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    age: int = Field(..., ge=0, le=150)

@router.post("/users")
def create_user(request: CreateUserRequest):  # Pydanticが自動バリデーション
    repository.create(request)
```

## 8. 不十分なログ記録

### アンチパターン

```python
# セキュリティイベントのログなし
@router.post("/login")
def login(request: LoginRequest):
    user = authenticate(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401)  # ログなし
    return create_token(user)

# 機密情報をログに含める
logger.info(f"Login attempt: email={email}, password={password}")
```

### 問題点

- 攻撃の検知ができない
- セキュリティインシデントの事後分析が困難
- コンプライアンス要件を満たせない
- 機密情報がログファイルに残る

### 正しい設計

```python
@router.post("/login")
def login(request: Request, credentials: LoginRequest):
    user = authenticate(credentials.email, credentials.password)
    if not user:
        logger.warning(
            "authentication_failed",
            email=credentials.email,
            ip=request.client.host,
            user_agent=request.headers.get("user-agent"),
        )
        raise HTTPException(status_code=401)

    logger.info(
        "authentication_success",
        user_id=user.id,
        ip=request.client.host,
    )
    return create_token(user)
```

## 9. 暗号化の誤用

### アンチパターン

```python
import hashlib
import base64

# MD5でパスワードをハッシュ化
password_hash = hashlib.md5(password.encode()).hexdigest()

# 自前の暗号化実装
def encrypt(data: str, key: str) -> str:
    result = ""
    for i, char in enumerate(data):
        result += chr(ord(char) ^ ord(key[i % len(key)]))
    return base64.b64encode(result.encode()).decode()

# ECBモードの使用
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
cipher = Cipher(algorithms.AES(key), modes.ECB())  # ECBはパターンが漏洩する
```

### 問題点

- MD5は衝突攻撃が実証済みで安全でない
- 自前の暗号化実装は脆弱性を含む可能性が高い
- ECBモードはデータのパターンが暗号文に現れる

### 正しい設計

```python
# パスワード: bcrypt/argon2を使用
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_hash = pwd_context.hash(password)

# 暗号化: 確立されたライブラリを使用
from cryptography.fernet import Fernet
key = Fernet.generate_key()
f = Fernet(key)
encrypted = f.encrypt(data.encode())

# AES-GCM（認証付き暗号化）
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
aesgcm = AESGCM(key)
nonce = os.urandom(12)
encrypted = aesgcm.encrypt(nonce, data, associated_data)
```

## 10. セッション管理の不備

### アンチパターン

```python
# セッションIDが予測可能
import random
session_id = str(random.randint(100000, 999999))

# ログアウト時にセッションを無効化しない
@router.post("/logout")
def logout():
    return {"message": "Logged out"}  # サーバー側のセッションは有効なまま

# セッションの有効期限なし
session_store.set(session_id, user_data)  # 永続的なセッション
```

### 問題点

- セッションIDが予測可能で、セッションハイジャックのリスク
- ログアウト後もセッションが有効
- セッションの有効期限がなく、盗まれたセッションが永続的に使用可能

### 正しい設計

```python
import secrets

# 暗号学的に安全なセッションID
session_id = secrets.token_urlsafe(32)

# ログアウト時にセッションを無効化
@router.post("/logout")
def logout(session_id: str = Depends(get_session_id)):
    session_store.delete(session_id)
    response = Response(status_code=200)
    response.delete_cookie("session_id")
    return response

# 有効期限付きセッション
session_store.set(session_id, user_data, ex=3600)  # 1時間
```

## まとめ

避けるべきセキュリティアンチパターン:

1. **シークレットのハードコーディング**: 環境変数やシークレットマネージャーを使用
2. **エラーメッセージでの情報露出**: 汎用メッセージを返し、詳細はログに記録
3. **認可チェックの漏れ**: リソース所有者チェックを実施
4. **不適切なCORS設定**: 本番環境でオリジンを限定
5. **SQLクエリの文字列連結**: パラメータ化クエリまたはORMを使用
6. **フェイルオープン**: エラー時はアクセスを拒否
7. **クライアントサイド検証のみ**: サーバーサイドで必ずバリデーション
8. **不十分なログ記録**: セキュリティイベントを適切にログ記録
9. **暗号化の誤用**: 確立されたライブラリとアルゴリズムを使用
10. **セッション管理の不備**: 安全なセッションID生成と適切な有効期限管理
