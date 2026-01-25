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
  is_production = local.workspace == "production"
  is_development = !local.is_production
  
  env_config = {
    development = {
      project_id = var.dev_project_id != "" ? var.dev_project_id : "PLEASE-SET-DEV-PROJECT-ID"
      region     = var.region
      zone       = var.zone
    }
    production = {
      project_id = var.prod_project_id != "" ? var.prod_project_id : "PLEASE-SET-PROD-PROJECT-ID"
      region     = var.region
      zone       = var.zone
    }
  }
  
  # 現在のワークスペースの設定を取得
  # production以外は全てdevelopment設定を使用
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
  domain       = var.production_domain
  labels       = local.common_labels
}