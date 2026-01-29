# Cloud SQLモジュールの出力値

output "instance_name" {
  description = "Cloud SQLインスタンス名"
  value       = var.environment == "production" ? google_sql_database_instance.main[0].name : null
}

output "instance_connection_name" {
  description = "Cloud SQL接続名（project:region:instance形式）"
  value       = var.environment == "production" ? google_sql_database_instance.main[0].connection_name : null
}

output "public_ip_address" {
  description = "Cloud SQLのパブリックIPアドレス"
  value       = var.environment == "production" ? google_sql_database_instance.main[0].public_ip_address : null
}

output "database_name" {
  description = "データベース名"
  value       = var.environment == "production" ? google_sql_database.main[0].name : null
}

output "database_user" {
  description = "データベースユーザー名"
  value       = var.environment == "production" ? google_sql_user.backend[0].name : null
}
