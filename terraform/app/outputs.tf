output "alb_dns_name" {
  description = "Public DNS name of the Bookmark ALB"
  value       = aws_lb.alb.dns_name
}

output "ecr_repository_url" {
  description = "URL of the Bookmark ECR repository"
  value       = aws_ecr_repository.api.repository_url
}

output "s3_bucket_name" {
  description = "S3 bucket used for screenshots"
  value       = aws_s3_bucket.screenshots.bucket
}