# Outputs for GCP Terraform Infrastructure

# Cloud Storageバケット名
output "storage_bucket_name" {
  description = "ストレージバケット名"
  value       = local.workspace == "production" && length(module.cloud_storage) > 0 ? module.cloud_storage[0].production_bucket_name : (local.workspace == "development" && length(module.cloud_storage) > 0 ? module.cloud_storage[0].development_bucket_name : null)
}

output "storage_bucket_url" {
  description = "ストレージバケットURL"
  value       = local.workspace == "production" && length(module.cloud_storage) > 0 ? module.cloud_storage[0].production_bucket_url : (local.workspace == "development" && length(module.cloud_storage) > 0 ? module.cloud_storage[0].development_bucket_url : null)
}

# ワークスペース情報
output "workspace" {
  description = "現在のTerraformワークスペース"
  value       = local.workspace
}

output "project_id" {
  description = "現在の環境のGCPプロジェクトID"
  value       = local.current_env.project_id
}

# 以下は未実装モジュールのため、コメントアウト
# 実装後にコメントを解除してください

# # Cloud Run URL
# output "backend_url" {
#   description = "バックエンドAPIのURL"
#   value       = local.workspace == "production" && length(module.cloud_run) > 0 ? module.cloud_run[0].service_url : null
# }

# # Cloud SQL接続情報
# output "database_connection_name" {
#   description = "Cloud SQLの接続名"
#   value       = local.workspace == "production" && length(module.cloud_sql) > 0 ? module.cloud_sql[0].connection_name : null
# }

# output "database_public_ip" {
#   description = "Cloud SQLのパブリックIPアドレス"
#   value       = local.workspace == "production" && length(module.cloud_sql) > 0 ? module.cloud_sql[0].public_ip_address : null
# }

# # Artifact Registry URL
# output "artifact_registry_url" {
#   description = "Artifact RegistryのURL"
#   value       = local.workspace == "production" && length(module.artifact_registry) > 0 ? module.artifact_registry[0].repository_url : null
# }

# # サービスアカウントメール
# output "backend_service_account_email" {
#   description = "バックエンド用サービスアカウントのメールアドレス"
#   value       = local.workspace == "production" && length(module.iam) > 0 ? module.iam[0].backend_service_account_email : null
# }

# output "github_actions_service_account_email" {
#   description = "GitHub Actions用サービスアカウントのメールアドレス"
#   value       = local.workspace == "production" && length(module.iam) > 0 ? module.iam[0].github_actions_service_account_email : null
# }

# output "firebase_deployer_service_account_email" {
#   description = "Firebase Hosting用サービスアカウントのメールアドレス"
#   value       = local.workspace == "production" && length(module.iam) > 0 ? module.iam[0].firebase_deployer_service_account_email : null
# }
