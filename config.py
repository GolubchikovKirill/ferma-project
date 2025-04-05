import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_db: int = int(os.getenv("REDIS_DB", 0))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")  # Если Redis защищен паролем

    class Config:
        env_file = ".env"


settings = Settings()

load_dotenv()

DB_URL = os.getenv("DB_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YANDEX_DISK_URL = os.getenv("YANDEX_DISK_URL")
YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN")