from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="POSTGRES_",
        extra="allow"
)   
    
    DB: str
    USER: str
    PASSWORD: str
    PORT: int
    HOST: str
    
    TEST_DB: str

    @computed_field
    def DATABASE_URL(self) -> str:
        db_url = f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"
        return db_url

    @computed_field
    def TEST_DATABASE_URL(self) -> str:
        test_db_url = f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.TEST_DB}"
        return test_db_url
    
    
settings = PostgresSettings()

