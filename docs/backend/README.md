# バックエンドAPI仕様書

## 概要

Historical Travel Agent APIの仕様書です

## 仕様書の閲覧

### ローカル開発環境

開発サーバー起動後、以下のURLで閲覧できます

```bash
just dev-backend
```

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 静的ファイル

- [OpenAPI仕様書（JSON）](./openapi.json)

## 仕様書の更新

APIエンドポイントやスキーマを変更した後、以下のコマンドで仕様書を更新します

```bash
just docs-generate-openapi
```

## Git管理

生成された`openapi.json`はGit管理下に置かれています

これにより以下が可能になります：

- API仕様の変更履歴を追跡できる
- PRレビュー時にAPI変更を可視化できる
- ドキュメントとコードの同期を保証できる
