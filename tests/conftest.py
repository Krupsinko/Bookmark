import os

TEST_SETTINGS = {
    "DB_NAME": "test",
    "DB_USER": "test",
    "DB_PASSWORD": "test",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "SECRET_KEY": "test-secret-key",
    "ALGORITHM": "HS256",
    "REDIS_HOST": "localhost",
    "S3_BUCKET_NAME": "test-screenshots",
    "AWS_ACCESS_KEY_ID": "test",
    "AWS_SECRET_ACCESS_KEY": "test",
    "AWS_DEFAULT_REGION": "eu-central-1",
}

for name, value in TEST_SETTINGS.items():
    if not os.environ.get(name):
        os.environ[name] = value
