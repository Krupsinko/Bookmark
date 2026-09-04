# ALB
resource "aws_lb" "alb" {
  name               = "bookmark-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets = [aws_subnet.public_a.id,
             aws_subnet.public_b.id
  ]

  enable_deletion_protection = false

  tags = {
    Environment = "dev"
  }
}

# TARGET GROUP
resource "aws_lb_target_group" "alb_target_group" {
  name        = "ecs-alb-tg"
  port        = 8000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.main.id

  health_check {
    path                = "/health"
    protocol            = "HTTP"
    port                = "traffic-port"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
  }
}

# LISTENER
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.alb.arn

  port     = 80
  protocol = "HTTP"

  default_action {
    type = "forward"

    target_group_arn = aws_lb_target_group.alb_target_group.arn
  }
}

# ALB SECURITY GROUP
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