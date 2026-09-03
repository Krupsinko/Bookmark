from celery import Celery

from app.config import RedisSettings

redis_settings = RedisSettings()
redis_host = redis_settings.REDIS_HOST

celery_app = Celery(
    "Bookmark", 
    broker=f"redis://{redis_host}:6379/0", 
    backend=f"redis://{redis_host}:6379/1"
)

