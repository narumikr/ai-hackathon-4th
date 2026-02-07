output "queue_name" {
  description = "Cloud Tasksキュー名"
  value       = var.environment == "production" ? var.queue_name : null
}

output "queue_id" {
  description = "Cloud TasksキューID"
  value       = var.environment == "production" ? google_cloud_tasks_queue.spot_image_queue[0].id : null
}
