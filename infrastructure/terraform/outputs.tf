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