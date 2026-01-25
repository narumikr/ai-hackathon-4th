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
  workspace = terraform.workspace
  
  # 環境ごとの設定
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
  current_env = local.env_config[local.workspace]
  
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
  
  environment  = local.workspace
  project_id   = local.current_env.project_id
  region       = local.current_env.region
  developer_id = var.developer_id
  domain       = var.production_domain
  labels       = local.common_labels
}

# Artifact Registryモジュール（本番環境のみ）
# - Dockerイメージレジストリ
# module "artifact_registry" {
#   source = "./modules/artifact-registry"
#   count  = local.workspace == "production" ? 1 : 0
#   
#   project_id = local.current_env.project_id
#   region     = local.current_env.region
#   labels     = local.common_labels
# }

# Secret Managerモジュール（本番環境のみ）
# - データベースパスワード管理
# module "secret_manager" {
#   source = "./modules/secret-manager"
#   count  = local.workspace == "production" ? 1 : 0
#   
#   project_id  = local.current_env.project_id
#   environment = local.workspace
# }

# Cloud SQLモジュール（本番環境のみ）
# - PostgreSQL 16データベース
# module "cloud_sql" {
#   source = "./modules/cloud-sql"
#   count  = local.workspace == "production" ? 1 : 0
#   
#   project_id    = local.current_env.project_id
#   region        = local.current_env.region
#   environment   = local.workspace
#   db_password   = local.workspace == "production" ? module.secret_manager[0].db_password : ""
#   labels        = local.common_labels
# }

# IAMモジュール（本番環境のみ）
# - サービスアカウントと権限管理
# module "iam" {
#   source = "./modules/iam"
#   count  = local.workspace == "production" ? 1 : 0
#   
#   project_id                    = local.current_env.project_id
#   project_number                = data.google_project.current.number
#   environment                   = local.workspace
#   storage_bucket_name           = local.workspace == "production" ? module.cloud_storage[0].production_bucket_name : ""
#   secret_id                     = local.workspace == "production" ? module.secret_manager[0].db_password_secret_id : ""
#   artifact_registry_repository  = local.workspace == "production" ? module.artifact_registry[0].repository_name : ""
#   artifact_registry_location    = local.current_env.region
#   github_repository             = var.github_repository
#   github_workload_identity_pool = var.github_workload_identity_pool
# }

# Cloud Runモジュール（本番環境のみ）
# - バックエンドAPIサービス
# module "cloud_run" {
#   source = "./modules/cloud-run"
#   count  = local.workspace == "production" ? 1 : 0
#   
#   project_id              = local.current_env.project_id
#   region                  = local.current_env.region
#   environment             = local.workspace
#   service_account_email   = local.workspace == "production" ? module.iam[0].backend_service_account_email : ""
#   storage_bucket_name     = local.workspace == "production" ? module.cloud_storage[0].production_bucket_name : ""
#   database_host           = local.workspace == "production" ? module.cloud_sql[0].public_ip_address : ""
#   database_name           = local.workspace == "production" ? module.cloud_sql[0].database_name : ""
#   database_user           = local.workspace == "production" ? module.cloud_sql[0].database_user : ""
#   secret_id               = local.workspace == "production" ? module.secret_manager[0].db_password_secret_id : ""
#   artifact_registry_url   = local.workspace == "production" ? module.artifact_registry[0].repository_url : ""
#   labels                  = local.common_labels
# }
