# GitHub ProjectへのIssue追加

このディレクトリには、リポジトリ内の全てのIssueをGitHub Projectに追加するためのツールが含まれています。

## 方法1: 手動スクリプトを使用する（推奨）

### 前提条件

- [GitHub CLI](https://cli.github.com/)がインストールされていること
- GitHubにログインしていること（`gh auth login`）

### 使用方法

```bash
./scripts/add-issues-to-project.sh <project_number> <owner_type>
```

#### 引数

- `project_number`: プロジェクト番号（例: 1）
- `owner_type`: プロジェクトのオーナータイプ
  - `user`: ユーザープロジェクトの場合
  - `org`: 組織プロジェクトの場合

#### 例

```bash
# ユーザープロジェクト（プロジェクト番号1）に追加
./scripts/add-issues-to-project.sh 1 user

# 組織プロジェクト（プロジェクト番号1）に追加
./scripts/add-issues-to-project.sh 1 org
```

### スクリプトの動作

1. 指定されたプロジェクトのIDを取得
2. リポジトリ内の全てのIssue（PRを除く）を取得
3. 各IssueをProjectに追加
4. 結果を表示（追加数、スキップ数、エラー数）

### 特徴

- ✅ 一時ファイルを使用して効率的にIssueを処理
- ✅ 既にプロジェクトに追加されているIssueを自動的にスキップ
- ✅ 進捗状況をリアルタイムで表示
- ✅ 冪等性: 何度実行しても同じ結果

## 方法2: GitHub Actionsワークフローを使用する

### 新しいIssueを自動的に追加

新しいIssueが作成されると、自動的に指定されたプロジェクトに追加されます。

デフォルトのプロジェクトURLは環境変数`PROJECT_URL`で設定できます：
1. リポジトリの「Settings」→「Secrets and variables」→「Actions」→「Variables」
2. 「New repository variable」をクリック
3. Name: `PROJECT_URL`、Value: `https://github.com/users/USERNAME/projects/NUMBER`

### 既存の全てのIssueを追加

1. GitHubリポジトリのページで「Actions」タブに移動
2. 「Add Issues to AI Hackathon 4th Project」ワークフローを選択
3. 「Run workflow」ボタンをクリック
4. パラメータを入力：
   - **Project number**: プロジェクト番号（例: 1）
   - **Project owner type**: `user` または `org`
   - **Project owner**: プロジェクトのオーナー（空欄の場合はリポジトリオーナーを使用）
5. 「Run workflow」を実行

### ワークフローの特徴

- ✅ 新規Issue作成時の自動追加
- ✅ 既存Issue一括追加（手動実行）
- ✅ 環境変数による設定のカスタマイズ
- ✅ レート制限を考慮した処理（0.5秒の遅延）
- ✅ 進捗状況とサマリーの表示

## プロジェクト番号の確認方法

1. GitHubでプロジェクトを開く
2. URLを確認する
   - ユーザープロジェクト: `https://github.com/users/USERNAME/projects/NUMBER`
   - 組織プロジェクト: `https://github.com/orgs/ORGNAME/projects/NUMBER`
3. URLの最後の数字がプロジェクト番号です

## トラブルシューティング

### エラー: プロジェクトが見つかりません

- プロジェクト番号が正しいか確認してください
- オーナータイプ（user/org）が正しいか確認してください
- プロジェクトが存在し、アクセス権限があることを確認してください
- プロジェクトが「Public」または自分がアクセス可能な状態になっているか確認してください

### エラー: 認証エラー

- GitHub CLIでログインしているか確認してください（`gh auth status`）
- 必要に応じて再ログインしてください（`gh auth login`）
- ワークフローの場合、適切な権限が設定されているか確認してください

### すでに追加されているIssue

スクリプトとワークフローは、既にプロジェクトに追加されているIssueを自動的にスキップします。
エラーにはならず、スキップされた数が表示されます。

### パフォーマンスについて

- **スクリプト版**: 全てのIssueを一度に取得してから処理するため効率的です
- **ワークフロー版**: レート制限を考慮して0.5秒の遅延を入れています
- 大量のIssue（100個以上）がある場合は、スクリプト版の使用を推奨します

## 技術詳細

### API使用

- GitHub GraphQL APIを使用
- `addProjectV2ItemById` mutationでIssueをプロジェクトに追加
- プロジェクトIDの取得に`organization.projectV2`または`user.projectV2`クエリを使用

### エラーハンドリング

- 重複エラー（既に追加されている）を適切に処理
- 一時ファイルを使用してサブシェル問題を回避
- 処理の進捗と結果を明確に表示
