# Main Terraform Configuration for GCP Infrastructure
# 
# このファイルは、GCP上に構築する歴史学習特化型旅行AIエージェントの
# インフラストラクチャのメイン設定ファイルです。
# 
# Terraformワークスペースを使用して、開発環境と本番環境を分離します。
# - development: 開発者個人用環境（Cloud Storageバケットのみ）
# - production: 本番環境（全リソース）

# ワークスペース管理
locals {
  # 現在のワークスペース名を取得
  workspace          = terraform.workspace
  allowed_workspaces = ["development", "production"]
  is_workspace_valid = contains(local.allowed_workspaces, local.workspace)
  _workspace_guard   = local.is_workspace_valid ? true : error("Unsupported workspace: ${local.workspace}. Use development or production.")

  # 環境ごとの設定
  is_production  = local.workspace == "production"
  is_development = local.workspace == "development"

  _dev_project_id_guard  = local.is_development && var.dev_project_id == "" ? error("dev_project_id is required in development workspace.") : true
  _prod_project_id_guard = local.is_production && var.prod_project_id == "" ? error("prod_project_id is required in production workspace.") : true
  _developer_id_guard    = local.is_development && (var.developer_id == "" || !can(regex("^[a-z0-9-]+$", var.developer_id))) ? error("developer_id must be non-empty and match ^[a-z0-9-]+$ in development workspace.") : true

  env_config = {
    development = {
      project_id = var.dev_project_id
      region     = var.region
      zone       = var.zone
    }
    production = {
      project_id = var.prod_project_id
      region     = var.region
      zone       = var.zone
    }
  }

  # 現在のワークスペースの設定を取得
  # workspaceはdevelopment/productionのみ許可される
  current_env = local.is_production ? local.env_config["production"] : local.env_config["development"]

  # 共通ラベル
  common_labels = {
    environment = local.workspace
    cost_center = var.cost_center
    managed_by  = "terraform"
    project     = "historical-travel-agent"
  }
}

# Google Cloud Provider設定
provider "google" {
  project = local.current_env.project_id
  region  = local.current_env.region
  zone    = local.current_env.zone
}

# プロジェクト情報の取得
data "google_project" "current" {
  project_id = local.current_env.project_id
}


# ============================================================================
# モジュール呼び出し
# ============================================================================
# 
# 各モジュールは、環境（development/production）に応じて条件付きで作成されます。
# count = local.workspace == "production" ? 1 : 0 を使用して制御します。

# Cloud Storageモジュール
# - development: 開発者個人用バケット
# - production: アップロードファイル用バケット
module "cloud_storage" {
  source = "./modules/cloud-storage"
  count  = 1

  environment  = local.is_production ? "production" : "development"
  project_id   = local.current_env.project_id
  region       = local.current_env.region
  developer_id = var.developer_id
  labels       = local.common_labels
}

# Artifact Registryモジュール
# - production: Dockerイメージ用リポジトリ
module "artifact_registry" {
  source = "./modules/artifact-registry"
  count  = 1

  environment    = local.is_production ? "production" : "development"
  project_id     = local.current_env.project_id
  project_number = data.google_project.current.number
  region         = local.current_env.region
  labels         = local.common_labels
}

# Secret Managerモジュール
# - production: データベースパスワードなどの機密情報
module "secret_manager" {
  source = "./modules/secret-manager"
  count  = 1

  environment = local.is_production ? "production" : "development"
  project_id  = local.current_env.project_id
  labels      = local.common_labels
}

# Cloud SQLモジュール
# - production: PostgreSQLデータベース
module "cloud_sql" {
  source = "./modules/cloud-sql"
  count  = 1

  environment = local.is_production ? "production" : "development"
  project_id  = local.current_env.project_id
  region      = local.current_env.region
  db_password = local.is_production ? module.secret_manager[0].db_password : ""
  labels      = local.common_labels

  # Secret Managerモジュールに依存
  depends_on = [module.secret_manager]
}

# IAMモジュール
# - production: サービスアカウントと権限管理
module "iam" {
  source = "./modules/iam"
  count  = 1

  environment                     = local.is_production ? "production" : "development"
  project_id                      = local.current_env.project_id
  project_number                  = data.google_project.current.number
  region                          = local.current_env.region
  storage_bucket_name             = local.is_production ? module.cloud_storage[0].bucket_name : ""
  db_password_secret_id           = local.is_production ? module.secret_manager[0].db_password_secret_id : ""
  artifact_registry_repository_id = local.is_production ? module.artifact_registry[0].repository_id : ""

  # 他のモジュールに依存
  depends_on = [
    module.cloud_storage,
    module.secret_manager,
    module.artifact_registry
  ]
}

# Cloud Runモジュール
# - production: FastAPIバックエンドアプリケーション
module "cloud_run" {
  source = "./modules/cloud-run"
  count  = 1

  environment           = local.is_production ? "production" : "development"
  project_id            = local.current_env.project_id
  region                = local.current_env.region
  container_image       = local.is_production ? "${local.current_env.region}-docker.pkg.dev/${local.current_env.project_id}/${module.artifact_registry[0].repository_id}/backend:latest" : ""
  storage_bucket_name   = local.is_production ? module.cloud_storage[0].bucket_name : ""
  database_host         = local.is_production ? module.cloud_sql[0].public_ip_address : ""
  database_name         = local.is_production ? module.cloud_sql[0].database_name : ""
  database_user         = local.is_production ? module.cloud_sql[0].database_user : ""
  db_password_secret_id = local.is_production ? module.secret_manager[0].db_password_secret_id : ""
  service_account_email = local.is_production ? module.iam[0].backend_service_account_email : ""
  labels                = local.common_labels

  # 他のモジュールに依存
  depends_on = [
    module.cloud_storage,
    module.cloud_sql,
    module.secret_manager,
    module.artifact_registry,
    module.iam
  ]
}

# Cloud Run Frontendモジュール
# - production: Next.jsフロントエンドアプリケーション
module "cloud_run_frontend" {
  source = "./modules/cloud-run-frontend"
  count  = 1

  environment           = local.is_production ? "production" : "development"
  project_id            = local.current_env.project_id
  region                = local.current_env.region
  container_image       = local.is_production ? "${local.current_env.region}-docker.pkg.dev/${local.current_env.project_id}/${module.artifact_registry[0].repository_id}/frontend:latest" : ""
  backend_service_url   = local.is_production ? module.cloud_run[0].service_url : ""
  service_account_email = local.is_production ? module.iam[0].frontend_service_account_email : ""
  labels                = local.common_labels

  # 他のモジュールに依存
  depends_on = [
    module.artifact_registry,
    module.iam,
    module.cloud_run
  ]
}
