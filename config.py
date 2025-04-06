import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


load_dotenv()

class Settings(BaseSettings):
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_db: int = int(os.getenv("REDIS_DB", 0))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")

    model_config = ConfigDict(
        env_file=".env",
        extra="allow"
    )

settings = Settings()

# Данные для подключения к БД и API
DB_URL = os.getenv("DB_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_HASH = os.getenv("API_HASH")
API_ID = os.getenv("API_ID")