Firebase Authentication (SDK直接利用) 設計と実装計画

目的
- Firebase Authenticationを使って簡易認証を導入し、UI表示やAPIアクセスをユーザー単位で制御する
- 早期検証に適した最小構成で開始し、将来的にAuthorization拡張へ移行できる構成にする

対象範囲
- フロントエンド: Firebase Auth SDK (Web) によるサインイン/サインアウト、IDトークン取得
- バックエンド: Firebase Admin SDK によるIDトークン検証、ユーザー情報の最小保持
- API: 認証済みアクセスが必要なエンドポイントの保護

前提
- まずはEmail/PasswordとGoogle OAuthを対象とする
- アカウント管理はFirebaseに委譲し、アプリ側は最低限のユーザー識別情報のみ保持
- 本番/開発でFirebaseプロジェクトを分離する

設計概要

認証方式
- フロントエンドでFirebase Auth SDKを直接利用し、サインイン後にIDトークンを取得
- バックエンドはAuthorizationヘッダーのBearerトークン (Firebase IDトークン) を検証
- 検証後のclaimsからユーザーID (uid) とメールを取り出してリクエストコンテキストに付与

主要コンポーネント
- Frontend Auth Client
	- Firebase SDK初期化
	- サインイン/サインアウトのUIと状態管理
	- APIリクエストにIDトークンを付与
- Backend Auth Middleware
	- AuthorizationヘッダーからIDトークンを抽出
	- Firebase Admin SDKで検証
	- リクエストスコープにuser情報を格納
- User Context
	- uid, email, name(任意), provider(任意)

データフロー
1. ユーザーがフロントでサインイン
2. FirebaseがIDトークンを発行
3. フロントがAPI呼び出し時にBearerトークンを付与
4. バックエンドがトークン検証し、uidを取得
5. ユーザーのデータへアクセス制御

API方針
- 既存APIは認証必須に切り替える段階を選択できるようにする
- 認証必須のAPIは401/403で応答
- まずはRead/Writeが同一ユーザーに限定されるリソースから保護

UI方針
- UI表示文言はfrontend/src/constants/*.tsに定義
- 認証状態でナビゲーションや操作ボタンを出し分け
- 未認証時の導線を分かりやすく配置

環境変数
- Frontend
	- NEXT_PUBLIC_FIREBASE_API_KEY
	- NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
	- NEXT_PUBLIC_FIREBASE_PROJECT_ID
	- NEXT_PUBLIC_FIREBASE_APP_ID
	- NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
	- NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
- Backend
	- FIREBASE_PROJECT_ID
	- FIREBASE_CLIENT_EMAIL
	- FIREBASE_PRIVATE_KEY

セキュリティ
- IDトークンの期限切れに対応 (期限切れ時はフロントで再取得)
- CORSは許可するオリジンを制限
- ログには生のトークンを出力しない

スコープ外
- ロールベースのAuthorization
- 課金/ライセンス管理
- 多要素認証

実装計画

1. Firebaseプロジェクト準備
- 開発用/本番用のFirebaseプロジェクトを作成
- AuthenticationでEmail/PasswordとGoogleを有効化
- Webアプリを作成し、SDK設定値を取得

2. フロントエンド実装
- Firebase SDK初期化
	- frontend/src/lib/firebase.tsを追加
	- initializeApp, getAuthの設定
- 認証用のUI/状態管理
	- サインイン/サインアウトのUI
	- ユーザー状態はContextまたはHookで管理
- APIクライアントでIDトークン付与
	- リクエスト前にgetIdTokenを取得してAuthorizationヘッダーに設定
	- トークン取得失敗時のハンドリング
- 文言はfrontend/src/constantsに追加

3. バックエンド実装
- Firebase Admin SDK初期化
	- backend/app/infrastructure/ai配下ではなくauth用の初期化を追加
	- サービスアカウント情報を環境変数から読み込む
- 認証ミドルウェア
	- backend/app/interfaces/middlewareにauth.pyを追加
	- Authorizationヘッダーを検証し、request.state.userに格納
- ルーティング保護
	- まずは旅行計画作成/取得/更新に適用
	- 各エンドポイントでuser.uidを参照

4. データモデル最小対応
- TravelPlanにowner_uidを持たせる
- 取得系はowner_uidでフィルタ

5. テスト
- バックエンド: トークン検証失敗時の401、成功時のコンテキスト付与を確認
- フロントエンド: 未認証時の操作不可、認証時のAPI呼び出し確認

リスクと対応
- Firebase設定の誤り
	- 開発/本番の環境変数とプロジェクトIDを分離
- トークン期限切れ
	- フロントで自動再取得を標準化
- 既存データとの整合
	- 既存データは管理者ユーザーに紐付け、移行スクリプトを用意

将来拡張
- カスタムクレームでロール管理
- Authorizationのポリシーベース化
- サーバーサイドでのセッションキャッシュ

参考
- Firebase Authentication Web SDK
- Firebase Admin SDK (Python)
