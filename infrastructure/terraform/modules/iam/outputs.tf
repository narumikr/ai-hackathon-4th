# IAMモジュールの出力値

output "backend_service_account_email" {
  description = "バックエンド用サービスアカウントのメールアドレス"
  value       = var.environment == "production" ? google_service_account.backend[0].email : null
}

output "backend_service_account_name" {
  description = "バックエンド用サービスアカウントの完全名"
  value       = var.environment == "production" ? google_service_account.backend[0].name : null
}

output "frontend_service_account_email" {
  description = "フロントエンド用サービスアカウントのメールアドレス"
  value       = var.environment == "production" ? google_service_account.frontend[0].email : null
}

output "frontend_service_account_name" {
  description = "フロントエンド用サービスアカウントの完全名"
  value       = var.environment == "production" ? google_service_account.frontend[0].name : null
}
