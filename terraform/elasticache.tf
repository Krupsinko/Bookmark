resource "aws_elasticache_replication_group" "redis" {
  replication_group_id = "bookmark-redis"
  description          = "Redis for Bookmark Celery"

  engine             = "redis"
  node_type          = "cache.t4g.micro"
  num_cache_clusters = 1

  port = 6379

  subnet_group_name  = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]

  automatic_failover_enabled = false
  multi_az_enabled           = false

  tags = {
    Name = "bookmark-redis"
  }
}



# REDIS SECURITY GROUP
resource "aws_security_group" "redis" {
  name        = "bookmark-redis-sg"
  description = "Security group for Bookmark Redis"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "bookmark-redis-sg"
  }

}
resource "aws_vpc_security_group_ingress_rule" "redis_allow_traffic_from_ecs" {
  security_group_id            = aws_security_group.redis.id
  referenced_security_group_id = aws_security_group.ecs.id
  ip_protocol                  = "TCP"
  from_port                    = 6379
  to_port                      = 6379
}

# REDIS SUBNET GROUP
resource "aws_elasticache_subnet_group" "redis" {
  name = "bookmark-redis-subnet-group"

  subnet_ids = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id
  ]

}

