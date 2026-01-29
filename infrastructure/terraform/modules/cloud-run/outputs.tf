# Cloud Runモジュールの出力値

output "service_name" {
  description = "Cloud Runサービス名"
  value       = var.environment == "production" ? google_cloud_run_service.backend[0].name : null
}

output "service_url" {
  description = "Cloud RunサービスのURL"
  value       = var.environment == "production" ? google_cloud_run_service.backend[0].status[0].url : null
}

output "service_id" {
  description = "Cloud RunサービスID"
  value       = var.environment == "production" ? google_cloud_run_service.backend[0].id : null
}
