# 要件定義書

## はじめに

本ドキュメントは、Firebase JWT認証への移行に関する要件を定義します。現在、バックエンドAPIはリクエストボディやクエリパラメータで`user_id`を要求していますが、Firebase Authenticationが既に導入されているため、JWTトークンから取得した`uid`を使用する方式に変更します。

## 用語集

- **System**: バックエンドAPIシステム全体
- **API_Client**: フロントエンドのAPIクライアント
- **JWT_Token**: Firebase Authenticationが発行するJSON Web Token
- **User_Context**: 認証ミドルウェアが提供するユーザー情報（`uid`を含む）
- **Request_Schema**: APIリクエストのPydanticスキーマ定義
- **Type_Definition**: フロントエンドのTypeScript型定義
- **Owner_Check**: リソースの所有者検証処理

## 要件

### 要件1: バックエンドAPIスキーマからuser_idフィールドを削除

**ユーザーストーリー:** 開発者として、APIスキーマから不要な`user_id`フィールドを削除したい。これにより、クライアントが`user_id`を送信する必要がなくなり、セキュリティが向上する。

#### 受入基準

1. WHEN `CreateTravelPlanRequest`スキーマが定義されるとき、THE System SHALL `user_id`フィールドを含まない
2. WHEN `CreateReflectionRequest`スキーマが定義されるとき、THE System SHALL `user_id`フィールドを含まない
3. WHEN APIエンドポイントがリクエストを受け取るとき、THE System SHALL `user_id`をリクエストボディから要求しない

### 要件2: バックエンドエンドポイントでauth.uidを使用

**ユーザーストーリー:** 開発者として、認証済みユーザーの識別に`auth.uid`を使用したい。これにより、クライアントから送信された`user_id`ではなく、JWTトークンから取得した信頼できる`uid`を使用できる。

#### 受入基準

1. WHEN 旅行計画作成エンドポイントが呼び出されるとき、THE System SHALL `auth.uid`を使用してユーザーを識別する
2. WHEN 旅行計画一覧取得エンドポイントが呼び出されるとき、THE System SHALL `auth.uid`でフィルタリングする
3. WHEN 振り返り作成エンドポイントが呼び出されるとき、THE System SHALL `auth.uid`を使用してユーザーを識別する
4. WHEN スポット振り返りアップロードエンドポイントが呼び出されるとき、THE System SHALL `auth.uid`を使用してユーザーを識別する
5. WHEN バックグラウンドタスクが実行されるとき、THE System SHALL 事前に取得した`auth.uid`を使用する

### 要件3: リソース所有者チェックの実装

**ユーザーストーリー:** ユーザーとして、自分のリソースのみにアクセスできるようにしたい。これにより、他のユーザーのデータが保護される。

#### 受入基準

1. WHEN 旅行計画取得エンドポイントが呼び出されるとき、THE System SHALL `travel_plan.user_id == auth.uid`を検証する
2. WHEN 旅行計画更新エンドポイントが呼び出されるとき、THE System SHALL `travel_plan.user_id == auth.uid`を検証する
3. WHEN 旅行計画削除エンドポイントが呼び出されるとき、THE System SHALL `travel_plan.user_id == auth.uid`を検証する
4. WHEN 旅行ガイド生成エンドポイントが呼び出されるとき、THE System SHALL `travel_plan.user_id == auth.uid`を検証する
5. IF 所有者チェックが失敗したとき、THEN THE System SHALL 403 Forbiddenエラーを返す

### 要件4: フロントエンド型定義からuserIdフィールドを削除

**ユーザーストーリー:** 開発者として、フロントエンドの型定義から不要な`userId`フィールドを削除したい。これにより、型安全性が向上し、バックエンドとの整合性が保たれる。

#### 受入基準

1. WHEN `CreateTravelPlanRequest`型が定義されるとき、THE API_Client SHALL `userId`フィールドを含まない
2. WHEN `CreateReflectionRequest`型が定義されるとき、THE API_Client SHALL `userId`フィールドを含まない
3. WHEN `SpotReflectionUploadRequest`型が定義されるとき、THE API_Client SHALL `userId`フィールドを含まない

### 要件5: フロントエンドAPIクライアントの修正

**ユーザーストーリー:** 開発者として、APIクライアントから`userId`パラメータを削除したい。これにより、JWTトークンのみを使用した認証が実現される。

#### 受入基準

1. WHEN `listTravelPlans`メソッドが呼び出されるとき、THE API_Client SHALL `userId`パラメータを要求しない
2. WHEN `createTravelPlan`メソッドが呼び出されるとき、THE API_Client SHALL リクエストに`userId`を含めない
3. WHEN `createReflection`メソッドが呼び出されるとき、THE API_Client SHALL リクエストに`userId`を含めない
4. WHEN `uploadSpotReflection`メソッドが呼び出されるとき、THE API_Client SHALL FormDataに`userId`を含めない
5. WHEN APIリクエストが送信されるとき、THE API_Client SHALL JWTトークンをAuthorizationヘッダーに含める

### 要件6: フロントエンドコンポーネントの修正

**ユーザーストーリー:** 開発者として、コンポーネントから`userId`の受け渡しを削除したい。これにより、コードが簡潔になり、保守性が向上する。

#### 受入基準

1. WHEN コンポーネントがAPIクライアントを呼び出すとき、THE API_Client SHALL `userId`を引数として受け取らない
2. WHEN コンポーネントがリクエストオブジェクトを構築するとき、THE API_Client SHALL `userId`フィールドを含めない

### 要件7: OpenAPI仕様の更新

**ユーザーストーリー:** 開発者として、OpenAPI仕様を最新のAPIスキーマに合わせて更新したい。これにより、APIドキュメントが正確になる。

#### 受入基準

1. WHEN OpenAPI仕様が生成されるとき、THE System SHALL `user_id`フィールドを含まないスキーマを反映する
2. WHEN OpenAPI仕様が生成されるとき、THE System SHALL 所有者チェックによる403エラーレスポンスを含める

### 要件8: 既存機能の保持

**ユーザーストーリー:** ユーザーとして、既存の認証機能が正常に動作し続けることを期待する。

#### 受入基準

1. WHEN 認証ミドルウェアが実行されるとき、THE System SHALL JWTトークンを検証し、`User_Context`に`uid`を格納する
2. WHEN データベースクエリが実行されるとき、THE System SHALL `user_id`カラムを使用してデータをフィルタリングする
3. WHEN 新しいリソースが作成されるとき、THE System SHALL `user_id`カラムに`auth.uid`を保存する
