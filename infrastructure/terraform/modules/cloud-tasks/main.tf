resource "google_cloud_tasks_queue" "spot_image_queue" {
  count    = var.environment == "production" ? 1 : 0
  project  = var.project_id
  location = var.location
  name     = var.queue_name

  rate_limits {
    max_dispatches_per_second = var.max_dispatches_per_second
    max_concurrent_dispatches = var.max_concurrent_dispatches
  }

  retry_config {
    max_attempts       = var.max_attempts
    min_backoff        = "${var.min_backoff_seconds}s"
    max_backoff        = "${var.max_backoff_seconds}s"
    max_doublings      = 5
    max_retry_duration = "0s"
  }
}
