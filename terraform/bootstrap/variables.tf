variable "github_repository" {
  description = "Owner/repository"
  type        = string
}

variable "github_branch" {
  description = "GitHub branch from which push is allowed"
  type        = string
  default     = "main"
}

variable "aws_region" {
  description = "AWS region for provider"
  type        = string
}