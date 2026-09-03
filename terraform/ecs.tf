# ECS SERVICE FOR API
resource "aws_ecs_service" "api" {
  name            = "bookmark-api"
  cluster         = aws_ecs_cluster.bookmark.id
  task_definition = aws_ecs_task_definition.api.arn

  desired_count = 1
  launch_type   = "FARGATE"

  network_configuration {
    subnets = [
      aws_subnet.private_a.id,
      aws_subnet.private_b.id
    ]

    security_groups = [
      aws_security_group.ecs.id
    ]

    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.alb_target_group.arn
    container_name   = "api"
    container_port   = 8000
  }
}
# TASK DEFINITION FOR API
resource "aws_ecs_task_definition" "api" {
  family = "bookmark-api"

  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  cpu    = "256"
  memory = "512"

  execution_role_arn = aws_iam_role.ecs_execution.arn

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = "${aws_ecr_repository.api.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "REDIS_HOST"
          value = aws_elasticache_replication_group.redis.primary_endpoint_address
        },
        {
          name  = "DB_HOST"
          value = aws_db_instance.bookmark.address
        },
        {
          name  = "DB_PORT"
          value = tostring(aws_db_instance.bookmark.port)
        },
        {
          name  = "DB_NAME"
          value = aws_db_instance.bookmark.db_name
        },
        {
          name  = "ALGORITHM"
          value = "HS256"
        }
      ]

      secrets = [
        {
          name      = "DB_USER"
          valueFrom = "${aws_db_instance.bookmark.master_user_secret[0].secret_arn}:username::"
        },
        {
          name      = "DB_PASSWORD"
          valueFrom = "${aws_db_instance.bookmark.master_user_secret[0].secret_arn}:password::"
        },
        {
          name     = "SECRET_KEY"
          valueFrom = aws_secretsmanager_secret.jwt_secret.arn
        }
      ]

    }
  ])

  tags = {
    Name = "bookmark-api"
  }
}




# ECS SERVICE FOR CELERY
resource "aws_ecs_service" "celery" {
  name            = "bookmark-celery"
  cluster         = aws_ecs_cluster.bookmark.id
  task_definition = aws_ecs_task_definition.celery.arn

  desired_count = 1
  launch_type   = "FARGATE"

  network_configuration {
    subnets = [
      aws_subnet.private_a.id,
      aws_subnet.private_b.id
    ]

    security_groups = [
      aws_security_group.ecs.id
    ]

    assign_public_ip = false
  }
}
# TASK DEFINITION FOR CELERY
resource "aws_ecs_task_definition" "celery" {
  family = "bookmark-celery"

  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  cpu    = "256"
  memory = "512"

  execution_role_arn = aws_iam_role.ecs_execution.arn
  task_role_arn      = aws_iam_role.celery.arn

  container_definitions = jsonencode([
    {
      name      = "celery"
      image     = "${aws_ecr_repository.api.repository_url}:latest"
      essential = true

      command = [
        "celery",
        "-A",
        "worker.celery_worker:celery_app",
        "worker",
        "--loglevel=info"
      ]

      environment = [
        {
          name  = "REDIS_HOST"
          value = aws_elasticache_replication_group.redis.primary_endpoint_address
        },
        {
          name  = "S3_BUCKET_NAME"
          value = aws_s3_bucket.screenshots.bucket
        }
      ]

    }
  ])

  tags = {
    Name = "bookmark-celery"
  }
}




# ECS SECURITY GROUP
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
  ip_protocol                  = "TCP"
  from_port                    = 8000
  to_port                      = 8000
}
resource "aws_vpc_security_group_egress_rule" "ecs_all" {
  security_group_id = aws_security_group.ecs.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}




# JWT SECRET KEY
ephemeral "random_password" "jwt_secret" {
  length  = 64
  special = false
}
resource "aws_secretsmanager_secret" "jwt_secret" {
  name = "bookmark-jwt-secret"
}
resource "aws_secretsmanager_secret_version" "jwt_secret" {
  secret_id                = aws_secretsmanager_secret.jwt_secret.id
  secret_string_wo         = ephemeral.random_password.jwt_secret.result
  secret_string_wo_version = 1
}





# Other
resource "aws_ecs_cluster" "bookmark" {
  name = "bookmark-cluster"

  tags = {
    Name = "bookmark-cluster"
  }
}
resource "aws_ecr_repository" "api" {
  name = "bookmark-api"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "bookmark-api"
  }
}