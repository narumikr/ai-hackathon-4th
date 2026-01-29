# Outputs for GCP Terraform Infrastructure

# ============================================================================
# 共通出力
# ============================================================================

# ワークスペース情報
output "workspace" {
  description = "現在のTerraformワークスペース"
  value       = local.workspace
}

output "project_id" {
  description = "現在の環境のGCPプロジェクトID"
  value       = local.current_env.project_id
}

# ============================================================================
# Cloud Storage
# ============================================================================

output "storage_bucket_name" {
  description = "ストレージバケット名"
  value       = local.workspace == "production" && length(module.cloud_storage) > 0 ? module.cloud_storage[0].production_bucket_name : (local.workspace == "development" && length(module.cloud_storage) > 0 ? module.cloud_storage[0].development_bucket_name : null)
}

output "storage_bucket_url" {
  description = "ストレージバケットURL"
  value       = local.workspace == "production" && length(module.cloud_storage) > 0 ? module.cloud_storage[0].production_bucket_url : (local.workspace == "development" && length(module.cloud_storage) > 0 ? module.cloud_storage[0].development_bucket_url : null)
}

# ============================================================================
# 本番環境のみの出力
# ============================================================================

# Cloud Run
output "backend_url" {
  description = "バックエンドAPIのURL"
  value       = local.workspace == "production" && length(module.cloud_run) > 0 ? module.cloud_run[0].service_url : null
}

output "backend_service_name" {
  description = "Cloud Runサービス名"
  value       = local.workspace == "production" && length(module.cloud_run) > 0 ? module.cloud_run[0].service_name : null
}

# Cloud SQL
output "database_connection_name" {
  description = "Cloud SQLの接続名"
  value       = local.workspace == "production" && length(module.cloud_sql) > 0 ? module.cloud_sql[0].instance_connection_name : null
}

output "database_host" {
  description = "Cloud SQLのパブリックIPアドレス"
  value       = local.workspace == "production" && length(module.cloud_sql) > 0 ? module.cloud_sql[0].public_ip_address : null
  sensitive   = true
}

output "database_name" {
  description = "データベース名"
  value       = local.workspace == "production" && length(module.cloud_sql) > 0 ? module.cloud_sql[0].database_name : null
}

# Artifact Registry
output "artifact_registry_url" {
  description = "Artifact RegistryのURL"
  value       = local.workspace == "production" && length(module.artifact_registry) > 0 ? module.artifact_registry[0].repository_url : null
}

# IAM
output "backend_service_account_email" {
  description = "バックエンド用サービスアカウントのメールアドレス"
  value       = local.workspace == "production" && length(module.iam) > 0 ? module.iam[0].backend_service_account_email : null
}

output "frontend_service_account_email" {
  description = "フロントエンド用サービスアカウントのメールアドレス"
  value       = local.workspace == "production" && length(module.iam) > 0 ? module.iam[0].frontend_service_account_email : null
}

# Cloud Run Frontend
output "frontend_url" {
  description = "フロントエンドアプリケーションのURL"
  value       = local.workspace == "production" && length(module.cloud_run_frontend) > 0 ? module.cloud_run_frontend[0].service_url : null
}

output "frontend_service_name" {
  description = "フロントエンドCloud Runサービス名"
  value       = local.workspace == "production" && length(module.cloud_run_frontend) > 0 ? module.cloud_run_frontend[0].service_name : null
}
