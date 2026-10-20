output "alb_dns_name" {
  description = "Public DNS name of the Bookmark ALB"
  value       = aws_lb.alb.dns_name
}