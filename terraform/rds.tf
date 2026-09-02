# DB INSTANCE
resource "aws_db_instance" "bookmark" {
  identifier = "bookmark-db"

  engine         = "postgres"
  engine_version = "17"

  instance_class = "db.t4g.micro"

  allocated_storage = 20
  storage_type      = "gp3"

  db_name  = "bookmark"
  username = "bookmark"

  manage_master_user_password = true

  db_subnet_group_name = aws_db_subnet_group.bookmark.name
  vpc_security_group_ids = [
    aws_security_group.rds.id
  ]

  publicly_accessible = false

  skip_final_snapshot = true

  tags = {
    Name = "bookmark-db"
  }
}


resource "aws_db_subnet_group" "bookmark" {
  name = "bookmark-db-subnet-group"

  subnet_ids = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id
  ]

  tags = {
    Name = "bookmark-db-subnet-group"
  }
}


# RDS SECURITY GROUP
resource "aws_security_group" "rds" {
  name        = "bookmark-rds-sg"
  description = "Security group for Bookmark RDS"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "bookmark-rds-sg"
  }
}
resource "aws_vpc_security_group_ingress_rule" "rds_postgres" {
  security_group_id            = aws_security_group.rds.id
  referenced_security_group_id = aws_security_group.ecs.id

  ip_protocol = "tcp"
  from_port   = 5432
  to_port     = 5432
}



