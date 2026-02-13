# 実装計画: JWT認証への移行

## 概要

Firebase JWT認証への移行を実装します。クライアントがリクエストボディやクエリパラメータで`user_id`を送信する方式から、JWTトークンから取得した`uid`を使用する方式に変更します。

## タスク

- [ ] 1. バックエンドAPIスキーマの変更
  - [ ] 1.1 CreateTravelPlanRequestからuser_idフィールドを削除
    - `backend/app/interfaces/schemas/travel_plan.py`を修正
    - `user_id`フィールドとそのバリデーターを削除
    - _要件: 1.1_
  
  - [ ] 1.2 CreateReflectionRequestからuser_idフィールドを削除
    - `backend/app/interfaces/schemas/reflection.py`を修正
    - `user_id`フィールドとそのバリデーターを削除
    - _要件: 1.2_

- [ ] 2. バックエンド所有者チェックヘルパーの実装
  - [ ] 2.1 所有者チェックヘルパー関数を作成
    - `backend/app/interfaces/api/v1/ownership.py`を新規作成
    - `verify_ownership`関数を実装
    - _要件: 3.1, 3.2, 3.3, 3.4_

- [ ] 3. 旅行計画エンドポイントの修正
  - [ ] 3.1 GET /travel-plans/{plan_id}に所有者チェックを追加
    - `backend/app/interfaces/api/v1/travel_plans.py`を修正
    - 取得後に`verify_ownership`を呼び出し
    - _要件: 3.1_
  
  - [ ] 3.2 PUT /travel-plans/{plan_id}に所有者チェックを追加
    - `backend/app/interfaces/api/v1/travel_plans.py`を修正
    - 更新前に旅行計画を取得し、`verify_ownership`を呼び出し
    - _要件: 3.2_
  
  - [ ] 3.3 DELETE /travel-plans/{plan_id}に所有者チェックを追加
    - `backend/app/interfaces/api/v1/travel_plans.py`を修正
    - 削除前に旅行計画を取得し、`verify_ownership`を呼び出し
    - _要件: 3.3_

- [ ] 4. 旅行ガイドエンドポイントの修正
  - [ ] 4.1 POST /travel-guidesに所有者チェックを追加
    - `backend/app/interfaces/api/v1/travel_guides.py`を修正
    - 生成前に旅行計画を取得し、`verify_ownership`を呼び出し
    - _要件: 3.4_

- [ ] 5. チェックポイント - バックエンドの動作確認
  - すべてのバックエンド変更が完了したことを確認
  - 既存のテストが通ることを確認
  - ユーザーに質問があれば確認

- [ ]* 6. バックエンドユニットテストの作成
  - [ ]* 6.1 所有者チェックヘルパーのテストを作成
    - `backend/tests/interfaces/api/v1/test_ownership.py`を新規作成
    - 正常系と異常系（403エラー）をテスト
    - _要件: 3.5_
  
  - [ ]* 6.2 旅行計画エンドポイントのテストを更新
    - `backend/tests/interfaces/api/v1/test_travel_plans.py`を修正
    - スキーマ変更と所有者チェックのテストを追加
    - _要件: 1.1, 3.1, 3.2, 3.3_
  
  - [ ]* 6.3 振り返りエンドポイントのテストを更新
    - `backend/tests/interfaces/api/v1/test_reflections.py`を修正
    - スキーマ変更のテストを追加
    - _要件: 1.2_
  
  - [ ]* 6.4 旅行ガイドエンドポイントのテストを更新
    - `backend/tests/interfaces/api/v1/test_travel_guides.py`を修正
    - 所有者チェックのテストを追加
    - _要件: 3.4_

- [ ]* 7. バックエンドプロパティベーステストの作成
  - [ ]* 7.1 プロパティ1のテストを作成
    - **プロパティ1: 旅行計画作成時のauth.uid使用**
    - **検証: 要件2.1**
  
  - [ ]* 7.2 プロパティ2のテストを作成
    - **プロパティ2: 旅行計画一覧のフィルタリング**
    - **検証: 要件2.2**
  
  - [ ]* 7.3 プロパティ3のテストを作成
    - **プロパティ3: 振り返り作成時のauth.uid使用**
    - **検証: 要件2.3**
  
  - [ ]* 7.4 プロパティ4のテストを作成
    - **プロパティ4: スポット振り返りアップロード時のauth.uid使用**
    - **検証: 要件2.4**
  
  - [ ]* 7.5 プロパティ5-8のテストを作成
    - **プロパティ5-8: 所有者チェック（取得、更新、削除、ガイド生成）**
    - **検証: 要件3.1, 3.2, 3.3, 3.4**
  
  - [ ]* 7.6 プロパティ9のテストを作成
    - **プロパティ9: リクエストボディにuser_idが不要**
    - **検証: 要件1.3**

- [ ] 8. フロントエンド型定義の変更
  - [ ] 8.1 CreateTravelPlanRequestからuserIdを削除
    - `frontend/src/types/travel.ts`を修正
    - `userId`フィールドを削除
    - _要件: 4.1_
  
  - [ ] 8.2 CreateReflectionRequestからuserIdを削除
    - `frontend/src/types/reflection.ts`を修正
    - `userId`フィールドを削除
    - _要件: 4.2_

- [ ] 9. フロントエンドAPIクライアントの変更
  - [ ] 9.1 SpotReflectionUploadRequest型からuserIdを削除
    - `frontend/src/lib/api.ts`を修正
    - `userId`フィールドを削除
    - _要件: 4.3_
  
  - [ ] 9.2 ApiClientインターフェースからuserIdパラメータを削除
    - `frontend/src/lib/api.ts`を修正
    - `listTravelPlans`、`createTravelPlan`、`createReflection`、`uploadSpotReflection`のシグネチャを変更
    - _要件: 5.1, 5.2, 5.3, 5.4_
  
  - [ ] 9.3 APIクライアントメソッドの実装を更新
    - `frontend/src/lib/api.ts`を修正
    - 各メソッドから`userId`の処理を削除
    - _要件: 5.1, 5.2, 5.3, 5.4_

- [ ] 10. フロントエンドコンポーネントの変更
  - [ ] 10.1 旅行計画一覧ページを更新
    - `frontend/src/app/travel/page.tsx`を修正
    - `listTravelPlans`呼び出しから`userId`を削除
    - _要件: 6.1_
  
  - [ ] 10.2 旅行計画作成ページを更新
    - `frontend/src/app/travel/new/page.tsx`を修正
    - `createTravelPlan`呼び出しから`userId`を削除
    - _要件: 6.2_
  
  - [ ] 10.3 振り返り一覧ページを更新
    - `frontend/src/app/reflection/page.tsx`を修正
    - `listTravelPlans`呼び出しから`userId`を削除
    - _要件: 6.1_
  
  - [ ] 10.4 振り返り作成ページを更新
    - `frontend/src/app/reflection/[id]/page.tsx`を修正
    - `uploadSpotReflection`と`createReflection`呼び出しから`userId`を削除
    - _要件: 6.2_

- [ ] 11. チェックポイント - フロントエンドの動作確認
  - すべてのフロントエンド変更が完了したことを確認
  - 型チェックが通ることを確認
  - ユーザーに質問があれば確認

- [ ]* 12. フロントエンドユニットテストの更新
  - [ ]* 12.1 APIクライアントのテストを更新
    - `frontend/src/lib/api.test.ts`を修正（存在する場合）
    - `userId`パラメータが送信されないことを確認
    - _要件: 5.1, 5.2, 5.3, 5.4_
  
  - [ ]* 12.2 旅行計画ページのテストを更新
    - `frontend/src/app/travel/page.test.tsx`を修正
    - `frontend/src/app/travel/new/page.test.tsx`を修正
    - モックから`userId`パラメータを削除
    - _要件: 6.1, 6.2_
  
  - [ ]* 12.3 振り返りページのテストを更新
    - `frontend/src/app/reflection/page.test.tsx`を修正（存在する場合）
    - `frontend/src/app/reflection/[id]/page.test.tsx`を修正
    - モックから`userId`パラメータを削除
    - _要件: 6.1, 6.2_
  
  - [ ]* 12.4 コンポーネントテストを更新
    - `frontend/src/components/features/reflection/ReflectionViewer.test.tsx`を修正
    - `frontend/tests/components/ReflectionViewer.test.tsx`を修正
    - モックデータは変更不要（レスポンスには`userId`が含まれる）
    - _要件: なし（既存テストの維持）_

- [ ]* 13. フロントエンドプロパティベーステストの作成
  - [ ]* 13.1 プロパティ10-13のテストを作成
    - `frontend/src/lib/api.property.test.ts`を新規作成
    - **プロパティ10-13: APIクライアントがuserIdを含めない**
    - **検証: 要件5.1, 5.2, 5.3, 5.4**
  
  - [ ]* 13.2 プロパティ14のテストを作成
    - `frontend/src/lib/api.property.test.ts`に追加
    - **プロパティ14: Authorizationヘッダーの設定**
    - **検証: 要件5.5**

- [ ] 14. OpenAPI仕様の更新
  - [ ] 14.1 スキーマ定義を更新
    - `docs/backend/openapi.json`を修正
    - `CreateTravelPlanRequest`と`CreateReflectionRequest`から`user_id`を削除
    - _要件: 7.1_
  
  - [ ] 14.2 エンドポイントに403レスポンスを追加
    - `docs/backend/openapi.json`を修正
    - GET/PUT/DELETE /travel-plans/{plan_id}、POST /travel-guidesに403レスポンスを追加
    - _要件: 7.2_

- [ ] 15. 最終チェックポイント - 統合テスト
  - すべてのテストが通ることを確認
  - バックエンドとフロントエンドが正しく連携することを確認
  - ユーザーに質問があれば確認

## 注意事項

- タスクに`*`が付いているものはオプションです（テスト関連）
- バックエンドとフロントエンドは同時にデプロイする必要があります（破壊的変更）
- 既存の認証ミドルウェアは変更しません
- データベーススキーマは変更しません
