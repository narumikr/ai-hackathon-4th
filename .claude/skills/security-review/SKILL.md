---
name: security-review
description: 実装、設計、要件からセキュリティリスクを特定しレビューする。ユーザーが「セキュリティレビューして」「脆弱性がないか確認して」「セキュリティリスクを洗い出して」と依頼した時、またはセキュリティに関する質問をした時に使用する。OWASP Top 10、認証・認可、入力バリデーション、データ保護、インフラセキュリティなどの観点から包括的にレビューする。
---

# セキュリティレビュー ベストプラクティス

## 概要

セキュリティレビューは、システムの実装・設計・要件に潜むセキュリティリスクを早期に発見し、対策を講じるためのプロセスである。効果的なセキュリティレビューは以下を実現する:

- **脆弱性の早期発見**: 本番環境にリリースされる前にリスクを特定
- **セキュリティ意識の向上**: 開発チーム全体のセキュリティリテラシー向上
- **コンプライアンス対応**: 業界標準やセキュリティ基準への準拠

### 対象範囲

- **実装レビュー**: ソースコード、設定ファイル、依存ライブラリの脆弱性チェック
- **設計レビュー**: アーキテクチャ、データフロー、認証・認可設計の妥当性評価
- **要件レビュー**: セキュリティ要件の網羅性、脅威モデリングの妥当性検証

## 基本原則

### 1. 多層防御（Defense in Depth）

単一の防御策に依存せず、複数のセキュリティ層で保護する。ある層が突破されても、他の層が攻撃を阻止する。

### 2. 最小権限の原則（Principle of Least Privilege）

ユーザー、プロセス、サービスに必要最小限の権限のみを付与する。不要な権限はリスクの増大に直結する。

### 3. セキュリティ・バイ・デフォルト（Secure by Default）

デフォルト設定でセキュアな状態とする。ユーザーが明示的にセキュリティを緩和しない限り、最も安全な設定を適用する。

### 4. フェイルセキュア（Fail Secure）

エラーや障害が発生した場合、安全な状態にフォールバックする。例外発生時にアクセスを許可してはならない。

### 5. 信頼境界の明確化（Trust Boundary）

外部入力（ユーザー入力、API呼び出し、外部サービスからのデータ）は常に信頼できないものとして扱い、バリデーションとサニタイズを行う。

## レビュー観点（優先順位順）

### 1. インジェクション攻撃

SQL、NoSQL、OS コマンド、LDAP、XPathなどのインジェクション攻撃を防ぐ。外部入力をそのままクエリやコマンドに組み込まない。

#### 危険なコード例

```python
# SQLインジェクション
query = f"SELECT * FROM users WHERE id = '{user_id}'"

# OSコマンドインジェクション
os.system(f"convert {filename} output.png")

# テンプレートインジェクション
template = Template(user_input)
```

#### 安全なコード例

```python
# パラメータ化クエリ / ORM使用
stmt = select(User).where(User.id == user_id)

# サブプロセスにリスト引数を使用
subprocess.run(["convert", filename, "output.png"], check=True)

# ユーザー入力をテンプレートに直接渡さない
template = Template(PREDEFINED_TEMPLATE)
result = template.render(data=sanitize(user_input))
```

### 2. 認証・認可の不備

認証の迂回、セッション管理の不備、権限チェックの欠如を防ぐ。

#### 危険なコード例

```python
# 認証なしのエンドポイント
@router.delete("/users/{user_id}")
def delete_user(user_id: str):
    repository.delete(user_id)

# 他人のリソースへのアクセスチェックなし（IDOR）
@router.get("/users/{user_id}/profile")
def get_profile(user_id: str, current_user = Depends(get_current_user)):
    return repository.find(user_id)  # current_userとの一致を確認していない
```

#### 安全なコード例

```python
# 認証・認可を実装
@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    repository.delete(user_id)

# IDORの防止
@router.get("/users/{user_id}/profile")
def get_profile(user_id: str, current_user = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return repository.find(user_id)
```

### 3. 機密データの露出

パスワード、APIキー、個人情報などの機密データが意図せず露出することを防ぐ。

#### 危険なコード例

```python
# パスワードをレスポンスに含める
@router.get("/users/{user_id}")
def get_user(user_id: str):
    user = repository.find(user_id)
    return user  # password_hash も含まれる

# エラーメッセージに内部情報を露出
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # スタックトレースが含まれる可能性

# ログに機密情報を出力
logger.info(f"User login: {username}, password: {password}")
```

#### 安全なコード例

```python
# レスポンススキーマで公開フィールドを制限
class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    # password_hash は含めない

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    user = repository.find(user_id)
    return UserResponse(**user.__dict__)

# 汎用的なエラーメッセージを返す（内部情報は露出しない）
except Exception as e:
    logger.error(f"Internal error: {e}")  # ログには記録
    raise HTTPException(status_code=500, detail="Internal server error")

# 機密情報をマスクしてログ出力
logger.info(f"User login: {username}")  # パスワードは含めない
```

### 4. セキュリティ設定の不備

デフォルト設定のまま運用、不要なサービスの有効化、デバッグモードの放置を防ぐ。

#### 危険なコード例

```python
# デバッグモードが本番で有効
app = FastAPI(debug=True)

# CORS全開放
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# シークレットのハードコーディング
SECRET_KEY = "my-secret-key-12345"

# 不要なエンドポイントの公開
@router.get("/debug/db-dump")
def dump_database():
    return repository.dump_all()
```

#### 安全なコード例

```python
# 環境に応じた設定
app = FastAPI(debug=settings.DEBUG)  # 本番では False

# 本番環境では厳密なCORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # ["https://example.com"]
)

# 環境変数からシークレットを取得
SECRET_KEY = os.environ["SECRET_KEY"]

# デバッグエンドポイントは開発環境のみ
if settings.DEBUG:
    @router.get("/debug/db-dump")
    def dump_database():
        return repository.dump_all()
```

### 5. 依存ライブラリの脆弱性

既知の脆弱性を含むライブラリの使用を防ぐ。定期的な依存関係の監査とアップデートを実施する。

#### チェックポイント

- 依存ライブラリに既知の脆弱性（CVE）がないか
- ライブラリのバージョンは最新か、またはサポート中か
- 不要なライブラリが含まれていないか
- ロックファイル（`package-lock.json`, `poetry.lock`等）が管理されているか

### 6. ロギングとモニタリング

セキュリティイベントの記録不足は、攻撃の検知と事後分析を困難にする。

#### チェックポイント

- 認証失敗、認可失敗のログを記録しているか
- ログに機密情報（パスワード、トークン、クレジットカード番号等）を含めていないか
- ログの改ざん防止策はあるか
- 異常なアクセスパターンを検知する仕組みがあるか

## クイックチェックリスト

セキュリティレビュー時に確認する項目:

### 入力処理
- [ ] すべての外部入力にバリデーションを実装しているか?
- [ ] SQLインジェクション対策（パラメータ化クエリ/ORM）を実施しているか?
- [ ] XSS対策（出力エスケープ）を実施しているか?
- [ ] OSコマンドインジェクション対策を実施しているか?
- [ ] ファイルアップロードのバリデーション（サイズ、タイプ、ファイル名）を実施しているか?

### 認証・認可
- [ ] すべてのエンドポイントで適切な認証を実装しているか?
- [ ] 認可チェック（権限確認）を実装しているか?
- [ ] IDOR（Insecure Direct Object Reference）を防止しているか?
- [ ] セッション管理は適切か（有効期限、無効化）?
- [ ] パスワードはハッシュ化して保存しているか（bcrypt/argon2）?

### データ保護
- [ ] 機密データをレスポンスに含めていないか?
- [ ] 通信はHTTPSで暗号化されているか?
- [ ] 機密データは保存時に暗号化されているか?
- [ ] ログに機密情報を出力していないか?
- [ ] エラーメッセージに内部情報を露出していないか?

### 設定・インフラ
- [ ] シークレットはハードコーディングされていないか（環境変数を使用）?
- [ ] CORS設定は本番環境で適切か（`*`を使用していないか）?
- [ ] デバッグモードは本番環境で無効化されているか?
- [ ] 不要なエンドポイントやサービスが公開されていないか?
- [ ] セキュリティヘッダー（HSTS, X-Content-Type-Options等）を設定しているか?

### 依存関係
- [ ] 依存ライブラリに既知の脆弱性がないか?
- [ ] ロックファイルが管理されているか?
- [ ] 不要な依存ライブラリを削除しているか?

### ロギング・監視
- [ ] セキュリティイベント（認証失敗等）をログに記録しているか?
- [ ] 異常検知の仕組みがあるか?
- [ ] ログに機密情報を含めていないか?

## 詳細リファレンス

より詳細な情報は以下のファイルを参照:

- **OWASP Top 10**: `references/owasp-top-10.md`
  - Webアプリケーションの主要な脆弱性カテゴリ
  - 各脆弱性の説明、影響度、対策

- **セキュアコーディング**: `references/secure-coding.md`
  - インジェクション対策の詳細
  - 入力バリデーションのパターン
  - 出力エスケープの手法

- **認証・認可**: `references/authentication-authorization.md`
  - 認証方式の選択基準
  - 認可パターンの実装
  - セッション管理のベストプラクティス

- **データ保護**: `references/data-protection.md`
  - 暗号化の実装
  - シークレット管理
  - 個人情報保護

- **インフラセキュリティ**: `references/infrastructure-security.md`
  - セキュリティヘッダー設定
  - CORS設定
  - コンテナ・クラウドセキュリティ

- **アンチパターン**: `references/anti-patterns.md`
  - よくあるセキュリティ上のミス
  - 避けるべきパターンと改善策

## 実装例

実際の使用例は以下のファイルを参照:

- **改善前後の比較**: `examples/before-after-examples.md`
  - 脆弱なコードとセキュアなコードの対比
  - 各改善の解説と効果

- **脆弱性パターン例**: `examples/vulnerability-examples.md`
  - 言語・フレームワーク別の脆弱性パターン
  - 実際に発生しやすい脆弱性シナリオ

## テンプレート

- **セキュリティレビューチェックリスト**: `templates/security-review-checklist.md`
  - レビュー実施時の包括的チェックリスト
  - レビュー結果の記録テンプレート

## 使用方法

このスキルは以下の場合に自動的に呼び出される:

- ユーザーが「セキュリティレビューして」と依頼した時
- 「脆弱性がないか確認して」と要求した時
- 「セキュリティリスクを洗い出して」と依頼した時
- セキュリティに関する質問をした時

手動で呼び出す場合: `/security-review`

## セキュリティレビューの実践手順

### 1. レビュー対象の分析

以下を特定する:

- レビュー対象の種類（実装/設計/要件）
- 使用言語・フレームワーク
- 扱うデータの機密性レベル
- 外部との通信箇所
- 認証・認可の仕組み

### 2. 脅威モデリング

対象システムに対する脅威を特定する:

- **STRIDE**: なりすまし(Spoofing)、改ざん(Tampering)、否認(Repudiation)、情報漏洩(Information Disclosure)、DoS(Denial of Service)、権限昇格(Elevation of Privilege)
- 信頼境界の特定
- データフローの分析
- 攻撃面（Attack Surface）の洗い出し

### 3. 観点別レビュー

上記6つのレビュー観点に基づいて、順に確認する:

1. インジェクション攻撃
2. 認証・認可の不備
3. 機密データの露出
4. セキュリティ設定の不備
5. 依存ライブラリの脆弱性
6. ロギングとモニタリング

### 4. リスク評価と報告

発見された問題を以下の形式で報告する:

```markdown
### [深刻度: Critical/High/Medium/Low] 問題のタイトル

**場所**: ファイルパス:行番号
**カテゴリ**: OWASP Top 10 カテゴリ（例: A03 インジェクション）
**説明**: 問題の詳細説明
**影響**: 攻撃された場合の影響
**再現手順**: 脆弱性の再現方法（該当する場合）

**Before（脆弱なコード）**:
[問題のあるコード]

**After（修正後のコード）**:
[修正されたコード]

**対策の説明**: なぜこの修正が有効かの説明
```

### 5. 優先順位付けと対応計画

- **Critical**: 即座に対応が必要（本番環境へのリリースをブロック）
- **High**: 次のリリースまでに対応が必要
- **Medium**: 計画的に対応する
- **Low**: リスクを受容するか、余裕がある時に対応する

## 重要な注意事項

- **網羅性よりも深度を重視**: すべての脆弱性を見つけることよりも、重大な脆弱性を確実に発見することを優先する
- **コンテキストを考慮**: 同じコードでも、扱うデータや公開範囲によってリスクレベルは異なる
- **誤検知に注意**: セキュリティ上の問題でないものを問題として報告しないよう、十分な分析を行う
- **修正の提案を含める**: 問題の指摘だけでなく、具体的な修正方法を提示する
- **段階的な改善**: 一度にすべてを修正するのではなく、リスクの高い順に対応する
