#!/bin/bash

# スクリプト: すべてのIssueをGitHub Projectに追加する
# 使用方法:
#   ./scripts/add-issues-to-project.sh <project_number> <owner_type>
#
# 引数:
#   project_number: プロジェクト番号 (例: 1)
#   owner_type: プロジェクトのオーナータイプ ("user" または "org")
#
# 例:
#   ./scripts/add-issues-to-project.sh 1 user
#   ./scripts/add-issues-to-project.sh 1 org
#
# 前提条件:
#   - GitHub CLIがインストールされていること
#   - gh auth loginでGitHubにログインしていること

set -e

# 引数のチェック
if [ $# -lt 2 ]; then
    echo "使用方法: $0 <project_number> <owner_type>"
    echo "  project_number: プロジェクト番号 (例: 1)"
    echo "  owner_type: 'user' または 'org'"
    echo ""
    echo "例:"
    echo "  $0 1 user"
    echo "  $0 1 org"
    exit 1
fi

PROJECT_NUMBER=$1
OWNER_TYPE=$2

# リポジトリ情報の取得
REPO_FULL=$(gh repo view --json nameWithOwner -q .nameWithOwner)
OWNER=$(echo "$REPO_FULL" | cut -d'/' -f1)
REPO_NAME=$(echo "$REPO_FULL" | cut -d'/' -f2)

echo "================================"
echo "Issue追加スクリプト"
echo "================================"
echo "リポジトリ: $REPO_FULL"
echo "オーナー: $OWNER"
echo "プロジェクト番号: $PROJECT_NUMBER"
echo "オーナータイプ: $OWNER_TYPE"
echo "================================"
echo ""

# プロジェクトIDの取得
echo "プロジェクトIDを取得中..."
if [ "$OWNER_TYPE" = "org" ]; then
    PROJECT_ID=$(gh api graphql -f query="
      query {
        organization(login: \"$OWNER\") {
          projectV2(number: $PROJECT_NUMBER) {
            id
            title
          }
        }
      }" --jq '.data.organization.projectV2.id')
    PROJECT_TITLE=$(gh api graphql -f query="
      query {
        organization(login: \"$OWNER\") {
          projectV2(number: $PROJECT_NUMBER) {
            id
            title
          }
        }
      }" --jq '.data.organization.projectV2.title')
else
    PROJECT_ID=$(gh api graphql -f query="
      query {
        user(login: \"$OWNER\") {
          projectV2(number: $PROJECT_NUMBER) {
            id
            title
          }
        }
      }" --jq '.data.user.projectV2.id')
    PROJECT_TITLE=$(gh api graphql -f query="
      query {
        user(login: \"$OWNER\") {
          projectV2(number: $PROJECT_NUMBER) {
            id
            title
          }
        }
      }" --jq '.data.user.projectV2.title')
fi

if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "null" ]; then
    echo "エラー: プロジェクトが見つかりません。"
    echo "プロジェクト番号とオーナータイプを確認してください。"
    exit 1
fi

echo "プロジェクトID: $PROJECT_ID"
echo "プロジェクト名: $PROJECT_TITLE"
echo ""

# 全てのIssueを取得
echo "全てのIssueを取得中..."
# 一時ファイルにIssue情報を保存して再利用
TEMP_ISSUES=$(mktemp)
gh api "repos/$REPO_FULL/issues?state=all&per_page=100" --paginate --jq '.[] | select(.pull_request == null) | {number: .number, node_id: .node_id, title: .title}' > "$TEMP_ISSUES"
ISSUE_COUNT=$(wc -l < "$TEMP_ISSUES")
echo "見つかったIssue数: $ISSUE_COUNT"
echo ""

if [ "$ISSUE_COUNT" -eq 0 ]; then
    echo "Issueが見つかりませんでした。"
    rm -f "$TEMP_ISSUES"
    exit 0
fi

# 各IssueをProjectに追加
echo "Issueをプロジェクトに追加中..."
# 一時ファイルでカウンターを管理
TEMP_COUNTS=$(mktemp)
echo "0 0 0" > "$TEMP_COUNTS"

while read -r line; do
    ISSUE_NUMBER=$(echo "$line" | jq -r .number)
    ISSUE_NODE_ID=$(echo "$line" | jq -r .node_id)
    ISSUE_TITLE=$(echo "$line" | jq -r .title)
    
    if [ -z "$ISSUE_NODE_ID" ] || [ "$ISSUE_NODE_ID" = "null" ]; then
        continue
    fi
    
    echo -n "Issue #$ISSUE_NUMBER: $(echo "$ISSUE_TITLE" | cut -c1-50)... "
    
    RESULT=$(gh api graphql -f query="
      mutation {
        addProjectV2ItemById(input: {projectId: \"$PROJECT_ID\", contentId: \"$ISSUE_NODE_ID\"}) {
          item {
            id
          }
        }
      }" 2>&1) || true
    
    # カウンターを読み込み
    read -r ADDED_COUNT SKIPPED_COUNT ERROR_COUNT < "$TEMP_COUNTS"
    
    if echo "$RESULT" | grep -q '"item"'; then
        echo "✓ 追加しました"
        ADDED_COUNT=$((ADDED_COUNT + 1))
    elif echo "$RESULT" | grep -q "already exists"; then
        echo "- すでに追加されています"
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
    else
        echo "✗ エラー"
        ERROR_COUNT=$((ERROR_COUNT + 1))
    fi
    
    # カウンターを保存
    echo "$ADDED_COUNT $SKIPPED_COUNT $ERROR_COUNT" > "$TEMP_COUNTS"
done < "$TEMP_ISSUES"

# 最終的なカウンターを読み込み
read -r ADDED_COUNT SKIPPED_COUNT ERROR_COUNT < "$TEMP_COUNTS"

# 一時ファイルの削除
rm -f "$TEMP_ISSUES" "$TEMP_COUNTS"

echo ""
echo "================================"
echo "完了！"
echo "================================"
echo "追加されたIssue: $ADDED_COUNT"
echo "スキップされたIssue: $SKIPPED_COUNT"
echo "エラー: $ERROR_COUNT"
echo "================================"
