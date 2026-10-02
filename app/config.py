from pydantic_settings import BaseSettings
from sqlalchemy import URL


class DatabaseSettings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: str
    DB_HOST: str

    @property
    def DATABASE_URL(self) -> URL:
        url_object = URL.create(
            "postgresql+asyncpg",
            database=self.DB_NAME,
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            port=self.DB_PORT,
            host=self.DB_HOST
        )
        return url_object


class EncryptSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str


class AwsSetting(BaseSettings):
    S3_BUCKET_NAME: str


class RedisSettings(BaseSettings):
    REDIS_HOST: str
