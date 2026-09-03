import boto3
from celery import Celery

from app.config import AwsSetting, RedisSettings

aws_settings = AwsSetting()
redis_settings = RedisSettings()

redis_host = redis_settings.REDIS_HOST
s3_bucket_name = aws_settings.S3_BUCKET_NAME

s3 = boto3.client("s3")
celery_app = Celery(
    "Bookmark", 
    broker=f"redis://{redis_host}:6379/0", 
    backend=f"redis://{redis_host}:6379/1"
)

