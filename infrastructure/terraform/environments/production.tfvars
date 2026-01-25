# Production Environment Variables
# 
# 本番環境用の設定ファイルです。
# 実際の値は環境変数やシークレット管理ツールから取得することを推奨します。

# 本番環境のGCPプロジェクトID
prod_project_id = "YOUR-PROD-PROJECT-ID"

# 本番ドメイン
production_domain = "your-domain.com"

# GitHub設定
github_repository             = "your-org/your-repo"
github_workload_identity_pool = "github-pool"

# 以下の変数は本番環境では使用されませんが、変数定義のため空文字を設定
dev_project_id = ""
developer_id   = ""
