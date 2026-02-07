# データ保護

## 概要

データ保護は、機密データの漏洩、改ざん、不正アクセスを防ぐためのセキュリティ対策である。保存時（at rest）、転送時（in transit）、使用時（in use）の各段階で適切な保護を実施する。

## 1. 機密データの分類

### データ分類レベル

| レベル | 説明 | 例 | 必要な保護 |
|--------|------|-----|----------|
| Critical | 漏洩時に重大な損害 | パスワード、暗号鍵、クレジットカード番号 | 暗号化必須、アクセスログ必須 |
| Confidential | 漏洩時に業務影響 | 個人情報（PII）、メールアドレス | 暗号化推奨、アクセス制御必須 |
| Internal | 社内利用に限定 | 内部ドキュメント、設計書 | アクセス制御必須 |
| Public | 公開情報 | 公開API仕様、ドキュメント | 改ざん防止 |

## 2. 転送時の暗号化（In Transit）

### HTTPS/TLS

```python
# HTTPS強制（FastAPI）
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# HSTSヘッダーの設定
@app.middleware("http")
async def add_hsts_header(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains; preload"
    )
    return response
```

### 内部通信の暗号化

```python
# サービス間通信もTLSを使用
import httpx

async def call_internal_service(url: str, data: dict) -> dict:
    async with httpx.AsyncClient(
        verify=True,  # TLS証明書の検証を有効化
        cert=("/path/to/client.crt", "/path/to/client.key"),  # mTLS
    ) as client:
        response = await client.post(url, json=data)
        return response.json()
```

## 3. 保存時の暗号化（At Rest）

### アプリケーションレベルの暗号化

```python
from cryptography.fernet import Fernet

class DataEncryptor:
    def __init__(self, key: bytes):
        self.fernet = Fernet(key)

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.fernet.decrypt(encrypted_data.encode()).decode()

# 使用例
encryptor = DataEncryptor(os.environ["ENCRYPTION_KEY"].encode())

# 保存時に暗号化
encrypted_ssn = encryptor.encrypt(user.ssn)
db.save(user_id=user.id, ssn_encrypted=encrypted_ssn)

# 読み取り時に復号
record = db.find(user_id=user.id)
ssn = encryptor.decrypt(record.ssn_encrypted)
```

### データベースフィールドレベルの暗号化

```python
from sqlalchemy import Column, String, TypeDecorator

class EncryptedString(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, encryptor: DataEncryptor, *args, **kwargs):
        self.encryptor = encryptor
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None:
            return self.encryptor.encrypt(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return self.encryptor.decrypt(value)
        return value

# モデル定義
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    name = Column(String)
    ssn = Column(EncryptedString(encryptor))  # 自動的に暗号化/復号
```

## 4. シークレット管理

### 環境変数

```python
import os

# Bad: ハードコーディング
SECRET_KEY = "my-secret-key-12345"
DATABASE_URL = "postgresql://user:password@localhost/db"

# Good: 環境変数
SECRET_KEY = os.environ["SECRET_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]

# Good: pydantic-settingsの使用
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    API_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### .envファイルの管理

```gitignore
# .gitignore
.env
.env.local
.env.production
*.pem
*.key
credentials.json
```

### シークレットマネージャーの使用

```python
# AWS Secrets Manager
import boto3
import json

def get_secret(secret_name: str) -> dict:
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

# 使用例
secrets = get_secret("myapp/production/db")
database_url = secrets["DATABASE_URL"]
```

## 5. レスポンスでのデータ保護

### 機密データのフィルタリング

```python
from pydantic import BaseModel

# Bad: 全フィールドを返す
@router.get("/users/{user_id}")
def get_user(user_id: str):
    user = repository.find(user_id)
    return user.__dict__  # password_hash等が含まれる

# Good: レスポンススキーマで制御
class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    # password_hash, ssn, credit_card等は含めない

    class Config:
        from_attributes = True

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    user = repository.find(user_id)
    return user  # UserResponseに定義されたフィールドのみ返る
```

### データマスキング

```python
def mask_email(email: str) -> str:
    """メールアドレスをマスクする"""
    local, domain = email.split("@")
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"

def mask_credit_card(card_number: str) -> str:
    """クレジットカード番号をマスクする"""
    return f"****-****-****-{card_number[-4:]}"

def mask_phone(phone: str) -> str:
    """電話番号をマスクする"""
    return f"***-****-{phone[-4:]}"
```

## 6. ログの機密データ保護

### ログからの機密情報除外

```python
import logging
import re

class SensitiveDataFilter(logging.Filter):
    PATTERNS = [
        (re.compile(r'password["\s:=]+["\']?[\w!@#$%^&*]+["\']?', re.I), 'password=***'),
        (re.compile(r'token["\s:=]+["\']?[\w\-._~+/]+=*["\']?', re.I), 'token=***'),
        (re.compile(r'api[_-]?key["\s:=]+["\']?[\w\-]+["\']?', re.I), 'api_key=***'),
        (re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'), '****-****-****-****'),
    ]

    def filter(self, record):
        message = record.getMessage()
        for pattern, replacement in self.PATTERNS:
            message = pattern.sub(replacement, message)
        record.msg = message
        record.args = ()
        return True

# フィルター適用
logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())
```

### 構造化ログでの機密データ除外

```python
import structlog

def sanitize_log_event(logger, method_name, event_dict):
    """ログイベントから機密データを除外する"""
    sensitive_keys = {"password", "token", "api_key", "secret", "credit_card", "ssn"}
    for key in list(event_dict.keys()):
        if key.lower() in sensitive_keys:
            event_dict[key] = "***REDACTED***"
    return event_dict

structlog.configure(
    processors=[
        sanitize_log_event,
        structlog.dev.ConsoleRenderer(),
    ]
)
```

## 7. 個人情報保護（PII）

### データの最小化

```python
# Bad: 不要な個人情報を収集
class UserRegistration(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    ssn: str          # 不要な情報
    date_of_birth: str  # 不要な情報

# Good: 必要最小限の情報のみ収集
class UserRegistration(BaseModel):
    name: str
    email: str
```

### データの保持期間

```python
from datetime import datetime, timedelta

# 個人データの保持期間ポリシー
DATA_RETENTION_POLICIES = {
    "user_sessions": timedelta(days=30),
    "access_logs": timedelta(days=90),
    "user_data": timedelta(days=365 * 3),  # 3年
    "audit_logs": timedelta(days=365 * 7),  # 7年
}

async def cleanup_expired_data():
    """保持期間を過ぎたデータを削除する"""
    for data_type, retention in DATA_RETENTION_POLICIES.items():
        cutoff = datetime.utcnow() - retention
        await repository.delete_before(data_type, cutoff)
```

### データ削除（忘れられる権利）

```python
async def delete_user_data(user_id: str):
    """ユーザーの個人データを完全に削除する"""
    # 関連データの削除
    await user_repository.delete(user_id)
    await session_repository.delete_by_user(user_id)
    await activity_log_repository.anonymize(user_id)

    # 監査ログには匿名化したIDを残す
    await audit_log_repository.anonymize_user(
        user_id,
        anonymized_id=f"deleted_user_{secrets.token_hex(8)}",
    )
```

## チェックリスト

### 転送時
- [ ] すべての通信でHTTPS/TLSを使用しているか
- [ ] HSTSヘッダーを設定しているか
- [ ] 内部サービス間通信も暗号化しているか

### 保存時
- [ ] 機密データ（PII、クレジットカード等）を暗号化して保存しているか
- [ ] 暗号化キーを安全に管理しているか
- [ ] パスワードはハッシュ化して保存しているか

### シークレット管理
- [ ] シークレットをソースコードにハードコーディングしていないか
- [ ] `.env`ファイルを`.gitignore`に追加しているか
- [ ] 本番環境でシークレットマネージャーを使用しているか

### レスポンス
- [ ] レスポンスから機密データを除外しているか
- [ ] 必要に応じてデータをマスキングしているか

### ログ
- [ ] ログに機密情報を含めていないか
- [ ] ログのサニタイズ処理を実装しているか

### 個人情報
- [ ] 収集する個人情報を必要最小限にしているか
- [ ] データ保持期間ポリシーを定義しているか
- [ ] データ削除の仕組みを実装しているか
