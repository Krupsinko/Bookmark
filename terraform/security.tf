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



resource "aws_security_group" "ecs" {
  name        = "bookmark-ecs-sg"
  description = "Security group for Bookmark ECS tasks"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "bookmark-ecs-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "ecs_allow_traffic_from_alb" {
  security_group_id            = aws_security_group.ecs.id
  referenced_security_group_id = aws_security_group.alb.id

  ip_protocol = "TCP"
  to_port     = 8000
  from_port   = 8000
}

resource "aws_vpc_security_group_egress_rule" "ecs_all" {
  security_group_id = aws_security_group.ecs.id

  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"
}


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


resource "aws_security_group" "alb" {
  name        = "bookmark-alb"
  description = "Security group for Bookmark ALB"
  vpc_id      = aws_vpc.main.id
}

resource "aws_vpc_security_group_ingress_rule" "alb_allow_all_trafic_ipv4" {
  security_group_id = aws_security_group.alb.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
}
resource "aws_vpc_security_group_egress_rule" "alb_allow_traffic_to_ecs" {
  security_group_id            = aws_security_group.alb.id
  referenced_security_group_id = aws_security_group.ecs.id
  ip_protocol                  = "tcp"
  from_port                    = 8000
  to_port                      = 8000
}
