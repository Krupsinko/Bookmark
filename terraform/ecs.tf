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

resource "aws_ecs_task_definition" "api" {
  family = "bookmark-api"

  requires_compatibilities = ["FARGATE"]

  network_mode = "awsvpc"

  cpu    = "256"
  memory = "512"

  execution_role_arn = aws_iam_role.ecs_execution.arn

  container_definitions = jsonencode([
    {
      name  = "api"
      image = "${aws_ecr_repository.api.repository_url}:latest"

      essential = true

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
    }
  ])

  tags = {
    Name = "bookmark-api"
  }
}

resource "aws_ecs_service" "api" {
  name = "bookmark-api"

  cluster = aws_ecs_cluster.bookmark.id

  task_definition = aws_ecs_task_definition.api.arn

  desired_count = 1

  launch_type = "FARGATE"

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