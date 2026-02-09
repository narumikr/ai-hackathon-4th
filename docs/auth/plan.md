認証機能 実装計画 (ボトルネック回避)

目的
- Firebase Authentication (SDK直接利用) を最小構成で導入し、開発スループットを落とさずに段階展開する

基本方針
- 小さな変更を短いサイクルで統合する
- フロント/バック/DBの依存関係を最小化して並行作業する
- 仕様の揺れが起きやすい箇所は先にインターフェースを固定する

実装戦略
- フェーズ0: 依存関係の明確化と合意形成
- フェーズ1: フロントの認証導線 (UI/SDK) を先行実装
- フェーズ2: バックエンドのトークン検証とAPI保護
- フェーズ3: データモデルの所有者対応とリグレッションテスト

ボトルネック回避のポイント
- フロントとバックで合意が必要なインターフェースを先に固定
- ミドルウェアとAPIの保護範囲を段階的に広げる
- DB変更は後半に寄せ、先にread-only検証で進める

成果物一覧
- docs/auth/design.md (設計)
- plan.md (実装計画)
- frontend/src/lib/firebase.ts (Firebase初期化)
- frontend/src/hooks/useAuth.ts (認証状態管理)
- backend/app/interfaces/middleware/auth.py (トークン検証)
- backend/app/interfaces/api/v1/* (API保護)
- DB migration (owner_uid追加)

フェーズ0: インターフェース固定 (1-2日)
- IDトークンの受け渡し方式を確定
  - Authorization: Bearer <Firebase ID Token>
- 認証失敗時のレスポンスを確定
  - 401: 未認証、403: 権限不足
- ユーザーコンテキストの最小項目を確定
  - uid, email, name(任意), provider(任意)
- 影響範囲を決める
  - まずは旅行計画作成/取得/更新で適用

フェーズ1: フロント先行 (2-4日)
- Firebase SDK初期化
  - frontend/src/lib/firebase.ts
- 認証フロー
  - Email/Password + Google OAuth
  - サインイン/サインアウト UI
- 認証状態管理
  - useAuthフック
- APIクライアント
  - IDトークンをAuthorizationヘッダーに付与
- ここまででバックエンド未対応でもUI検証が可能

フェーズ2: バックエンドのトークン検証 (2-3日)
- Firebase Admin SDKの初期化
- 認証ミドルウェアの追加
  - 失敗時は401
  - 成功時はrequest.state.userに格納
- APIの一部を保護
  - 旅行計画作成/取得/更新
- ログにトークンを出さない

フェーズ3: データモデルの所有者対応 (2-4日)
- TravelPlanにowner_uidを追加
- 取得系はowner_uidでフィルタ
- 既存データ移行
  - 管理ユーザーに紐付け
- 統合テスト
  - 認証必須エンドポイントの動作確認

作業分割 (並行化)
- フロント担当
  - Firebase設定/認証UI/状態管理
- バック担当
  - Firebase Admin SDK/ミドルウェア/エンドポイント保護
- データ担当
  - owner_uid追加/移行/フィルタ

リスクと軽減策
- Firebase設定ミス
  - 開発/本番の環境変数を分離
  - 初期化のフェイルファスト
- トークン期限切れ
  - フロントでgetIdTokenの再取得を標準化
- 既存データの不整合
  - 移行スクリプトを用意し、手動検証

完了条件
- 認証必須エンドポイントが401/403で正しく制御される
- ユーザーごとにリソースが分離される
- E2EでサインインからAPI操作まで通る
