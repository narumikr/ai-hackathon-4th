# Development Environment Variables Template
# 
# このファイルをコピーして個人用の開発環境設定を作成してください:
#   cp development-template.tfvars development-YOUR-NAME.tfvars
# 
# 注意: development-*.tfvars ファイルは .gitignore に追加されており、
#       個人の設定情報がGitにコミットされることはありません。

# 開発環境のGCPプロジェクトID
dev_project_id = "your-dev-project-id"

# 開発者の識別子（英数字とハイフンのみ、小文字推奨）
# この値はCloud Storageバケット名に使用されます
# 例: "alice", "bob", "dev-team-member-1"
developer_id = "your-name"

# 以下の変数は開発環境では使用されませんが、変数定義のため空文字を設定
prod_project_id               = ""
production_domain             = ""
github_repository             = ""
github_workload_identity_pool = ""
