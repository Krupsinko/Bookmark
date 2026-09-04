resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/bookmark-api"
  retention_in_days = 1

  tags = {
    Name = "bookmark-api-logs"
  }
}

resource "aws_cloudwatch_log_group" "celery" {
  name              = "/ecs/bookmark-celery"
  retention_in_days = 1

  tags = {
    Name = "bookmark-celery-logs"
  }
}