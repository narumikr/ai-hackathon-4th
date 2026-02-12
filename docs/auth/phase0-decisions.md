フェーズ0 決定事項 (ドラフト)

目的
- フロント/バックが並行して進められる最小の認証インターフェースを固定する

決定事項 (提案デフォルト)
- 認証ヘッダー: Authorization: Bearer <Firebase ID Token>
- 認証失敗時のステータスコード:
  - 401 Unauthorized: トークン無し/不正/期限切れ
  - 403 Forbidden: トークンは有効だが許可されない (将来のロール用に予約)
- ユーザーコンテキスト項目 (リクエストスコープ):
  - uid (必須)
  - email (任意)
  - name (任意)
  - provider (任意)
- 初期の保護対象API (フェーズ1):
  - POST /api/v1/travel-plans
  - GET /api/v1/travel-plans
  - GET /api/v1/travel-plans/{id}
  - PUT /api/v1/travel-plans/{id}
- 公開エンドポイントは残す (例: ヘルスチェック、静的コンテンツ)

未確定事項
- なし

次のアクション
- 決定事項を docs/auth/task.md に反映
- フロントのSDK設定とバックエンドのミドルウェア実装に着手
