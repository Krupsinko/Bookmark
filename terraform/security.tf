# ECS CELERY WORKER IAM ROLE/POLICY
resource "aws_iam_role" "celery" {
  name = "bookmark-celery-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}
resource "aws_iam_policy" "celery_s3" {
  name = "bookmark-celery-s3"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "s3:PutObject"
        ]

        Resource = "${aws_s3_bucket.screenshots.arn}/*"
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "celery_s3" {
  role       = aws_iam_role.celery.name
  policy_arn = aws_iam_policy.celery_s3.arn
}




# ECS EXECUTION ROLE
resource "aws_iam_role" "ecs_execution" {
  name = "bookmark-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }

      Action = "sts:AssumeRole"
    }]
  })
}
resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role = aws_iam_role.ecs_execution.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
