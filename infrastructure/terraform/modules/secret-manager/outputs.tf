# Secret Managerモジュールの出力値

output "db_password_secret_id" {
  description = "データベースパスワードのシークレットID"
  value       = var.environment == "production" ? google_secret_manager_secret.db_password[0].secret_id : null
}

output "db_password_secret_name" {
  description = "データベースパスワードのシークレット完全名"
  value       = var.environment == "production" ? google_secret_manager_secret.db_password[0].name : null
}

output "db_password" {
  description = "生成されたデータベースパスワード（Terraform内部でのみ使用）"
  value       = var.environment == "production" ? random_password.db_password[0].result : null
  sensitive   = true
}
