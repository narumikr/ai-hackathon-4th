# CI/CD ワークフロー設計書

## 目的

PRが作成・更新された際に、コードの品質を自動的にチェックして、問題のあるコードがマージされることを防ぐ。

## 検知内容

### Stage 1: Lint Check
- **コードスタイル違反**: 統一されたフォーマットルールに従っているか
- **型エラー**: TypeScript/Pythonの型チェック
- **構文エラー**: 基本的な文法ミス
- **未使用変数・import**: 不要なコードの検出

### Stage 2: Code Quality Check  
- **テスト失敗**: 既存機能が壊れていないか
- **ビルドエラー**: 本番環境でデプロイ可能か
- **カバレッジ低下**: テストが十分に書かれているか

## 実行タイミング

- PR作成時
- PR更新時（新しいコミットがプッシュされた時）
- PRが再オープンされた時

## 実行フロー

```
PR作成/更新
    ↓
Stage 1: コードスタイル・型チェック
    ↓ (成功時のみ)
Stage 2: テスト・ビルドチェック
    ↓ (成功時のみ)
✅ PR Ready for Review
```

**失敗時**: その時点でパイプライン停止、後続ステージはスキップ

## 使用コマンド

| ステージ | 実行コマンド | 内容 |
|---------|-------------|------|
| Stage 1 | `just check-quality` | lint, format, typecheck |
| Stage 2 | `just test-backend-cov` | バックエンドテスト（カバレッジ付き） |
| Stage 2 | `just test-frontend` | フロントエンドテスト |
| Stage 2 | `just build-frontend` | フロントエンドビルド |

## ローカルでの事前確認

CI/CDと同じコマンドでローカルチェック可能：

```bash
# 依存関係インストール
just install-all

# Stage 1相当
just check-quality

# Stage 2相当
just test-backend-cov
just test-frontend  
just build-frontend
```

## トラブルシューティング

### Stage 1で失敗した場合
```bash
just check-quality  # エラー内容を確認
just lint-backend-fix  # 自動修正（バックエンド）
just lint-frontend-fix # 自動修正（フロントエンド）
```

### Stage 2で失敗した場合
```bash
just test-backend-cov  # バックエンドテスト確認
just test-frontend     # フロントエンドテスト確認
just build-frontend    # ビルド確認
```

## 設定ファイル

- `.github/workflows/01-lint-check.yml` - Stage 1実行
- `.github/workflows/02-quality-check.yml` - Stage 2実行  
- `.github/workflows/pipeline-status.yml` - 全体状況レポート
- `justfile` - 実際のコマンド定義