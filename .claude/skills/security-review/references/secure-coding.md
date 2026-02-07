# セキュアコーディング

## 概要

セキュアコーディングは、ソフトウェアの脆弱性を防ぐためのコーディング手法である。入力処理、出力処理、エラー処理の各段階でセキュリティを考慮する。

## 1. 入力バリデーション

### 原則

- すべての外部入力は信頼できないものとして扱う
- ホワイトリスト方式を優先する（許可リストに基づく検証）
- バリデーションはサーバーサイドで必ず行う

### 文字列バリデーション

```python
from pydantic import BaseModel, Field, field_validator
import re

class UserInput(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    age: int = Field(..., ge=0, le=150)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Username must contain only alphanumeric characters, hyphens, and underscores")
        return v
```

### ファイルアップロードバリデーション

```python
import magic
from pathlib import Path

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_upload(file: UploadFile) -> None:
    # ファイルサイズチェック
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds {MAX_FILE_SIZE} bytes")

    # 拡張子チェック
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File extension {ext} is not allowed")

    # MIMEタイプチェック（マジックバイト）
    content = file.file.read(2048)
    file.file.seek(0)
    mime_type = magic.from_buffer(content, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"MIME type {mime_type} is not allowed")

    # ファイル名のサニタイズ
    safe_filename = re.sub(r'[^\w\-.]', '_', file.filename)
```

### パストラバーサル対策

```python
from pathlib import Path

UPLOAD_DIR = Path("/app/uploads")

def safe_file_path(filename: str) -> Path:
    # パストラバーサルを防止
    safe_name = Path(filename).name  # ディレクトリ部分を除去
    full_path = (UPLOAD_DIR / safe_name).resolve()

    # アップロードディレクトリ内であることを確認
    if not str(full_path).startswith(str(UPLOAD_DIR.resolve())):
        raise ValueError("Invalid file path")

    return full_path
```

## 2. 出力エスケープ

### HTMLエスケープ

```python
import html

def safe_html_output(user_input: str) -> str:
    return html.escape(user_input)
    # < → &lt;  > → &gt;  & → &amp;  " → &quot;  ' → &#x27;
```

### JSONレスポンスのセキュリティ

```python
from fastapi.responses import JSONResponse

# Content-Typeヘッダーの明示的な設定
@router.get("/data")
def get_data():
    return JSONResponse(
        content={"data": "value"},
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
```

### URLエンコード

```python
from urllib.parse import quote, urlencode

# URLパラメータのエンコード
safe_param = quote(user_input, safe="")
url = f"https://api.example.com/search?q={safe_param}"

# 複数パラメータのエンコード
params = urlencode({"q": user_input, "page": 1})
url = f"https://api.example.com/search?{params}"
```

## 3. SQLインジェクション対策

### パラメータ化クエリ

```python
# PostgreSQL (psycopg2)
cursor.execute(
    "SELECT * FROM users WHERE email = %s AND status = %s",
    (email, "active"),
)

# SQLite
cursor.execute(
    "SELECT * FROM users WHERE email = ? AND status = ?",
    (email, "active"),
)
```

### ORM使用

```python
# SQLAlchemy
from sqlalchemy import select

stmt = select(User).where(User.email == email, User.status == "active")
result = session.execute(stmt).scalars().all()

# Django ORM
users = User.objects.filter(email=email, status="active")
```

### 動的クエリの安全な構築

```python
from sqlalchemy import select, and_

def build_query(filters: dict):
    stmt = select(User)
    conditions = []

    if "email" in filters:
        conditions.append(User.email == filters["email"])
    if "status" in filters:
        conditions.append(User.status == filters["status"])
    if "role" in filters:
        conditions.append(User.role.in_(filters["role"]))

    if conditions:
        stmt = stmt.where(and_(*conditions))

    return stmt
```

## 4. XSS（クロスサイトスクリプティング）対策

### 種類と対策

| 種類 | 説明 | 主な対策 |
|------|------|---------|
| Stored XSS | サーバーに保存されるデータ経由 | 入力バリデーション + 出力エスケープ |
| Reflected XSS | URLパラメータ経由 | 出力エスケープ + CSPヘッダー |
| DOM-based XSS | クライアントサイドJavaScript経由 | 安全なDOM操作API使用 |

### サーバーサイド対策

```python
# Content Security Policy ヘッダー
@app.middleware("http")
async def add_csp_header(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'"
    )
    return response
```

### フロントエンド対策

```javascript
// Bad: innerHTMLの使用
element.innerHTML = userInput;  // XSS脆弱

// Good: textContentの使用
element.textContent = userInput;  // 安全

// Good: DOMPurifyの使用（HTMLを許可する場合）
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

## 5. CSRF（クロスサイトリクエストフォージェリ）対策

### トークンベースの対策

```python
from fastapi import Form, Cookie
import secrets

def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)

@router.post("/transfer")
async def transfer_funds(
    amount: float = Form(...),
    csrf_token: str = Form(...),
    session_csrf: str = Cookie(..., alias="csrf_token"),
):
    if csrf_token != session_csrf:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
    # 処理を続行
```

### SameSite Cookie

```python
from fastapi.responses import Response

response = Response()
response.set_cookie(
    key="session_id",
    value=session_id,
    httponly=True,     # JavaScriptからアクセス不可
    secure=True,       # HTTPS通信のみ
    samesite="strict", # 同一サイトのみ
    max_age=3600,      # 有効期限
)
```

## 6. OSコマンドインジェクション対策

```python
import subprocess
import shlex

# Bad: shell=True + 文字列連結
subprocess.run(f"convert {user_file} output.png", shell=True)

# Good: リスト引数（shell=False）
subprocess.run(["convert", user_file, "output.png"], check=True)

# どうしてもシェルが必要な場合はエスケープ
safe_input = shlex.quote(user_file)
subprocess.run(f"convert {safe_input} output.png", shell=True, check=True)
```

## 7. デシリアライゼーション

```python
# Bad: 安全でないデシリアライゼーション
import pickle
import yaml

data = pickle.loads(user_input)          # 任意コード実行の危険
data = yaml.load(user_input)             # 任意コード実行の危険

# Good: 安全な形式を使用
import json

data = json.loads(user_input)            # 安全
data = yaml.safe_load(user_input)        # 安全

# Pydanticでの型安全なデシリアライゼーション
class UserData(BaseModel):
    name: str
    age: int

data = UserData.model_validate_json(user_input)
```

## 8. 正規表現のDoS（ReDoS）対策

```python
import re

# Bad: 指数的なバックトラッキングが発生する正規表現
pattern = re.compile(r'^(a+)+$')  # ReDoS脆弱

# Good: 効率的な正規表現
pattern = re.compile(r'^a+$')     # 安全

# タイムアウト付き正規表現マッチング
import signal

def regex_with_timeout(pattern: str, text: str, timeout: int = 1) -> bool:
    def handler(signum, frame):
        raise TimeoutError("Regex timed out")

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    try:
        return bool(re.match(pattern, text))
    except TimeoutError:
        return False
    finally:
        signal.alarm(0)
```

## 9. 安全な乱数生成

```python
import secrets
import os

# Bad: 予測可能な乱数
import random
token = ''.join(random.choices('abcdef0123456789', k=32))  # 暗号学的に安全でない

# Good: 暗号学的に安全な乱数
token = secrets.token_hex(32)           # ランダムな16進文字列
token = secrets.token_urlsafe(32)       # URLセーフなランダム文字列
random_bytes = os.urandom(32)           # ランダムなバイト列
```

## 10. メモリ安全性

```python
# 機密データの使用後のクリア
import ctypes

def secure_clear(s: str):
    """文字列のメモリをクリアする（ベストエフォート）"""
    if isinstance(s, str):
        # Python文字列は不変なので完全なクリアは困難
        # 可能な限りGCを促進する
        del s

# より安全なアプローチ: bytearray使用
def process_secret(secret: bytes):
    secret_array = bytearray(secret)
    try:
        # 処理を実行
        pass
    finally:
        # メモリをゼロクリア
        for i in range(len(secret_array)):
            secret_array[i] = 0
```

## まとめ

セキュアコーディングの要点:

1. **入力は常にバリデーション**: ホワイトリスト方式でサーバーサイドで検証
2. **出力は常にエスケープ**: コンテキストに応じたエスケープ処理
3. **パラメータ化クエリ**: SQL文字列結合を避ける
4. **安全なAPI使用**: 危険なAPIの代わりに安全な代替手段を使用
5. **最小権限**: 必要最小限の権限で実行
6. **暗号学的に安全な乱数**: セキュリティ用途には`secrets`モジュールを使用
7. **デシリアライゼーション**: pickle等を避け、JSON等の安全な形式を使用
