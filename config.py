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


DB_URL = os.getenv("DB_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN")
YANDEX_DISK_URL = "https://cloud-api.yandex.net/v1/disk"
LOCAL_TDATA_PATH = "download/tdata"
REMOTE_TDATA_PATH = "/TDATA"
REMOTE_TDATA_USED = "/TDATAused"