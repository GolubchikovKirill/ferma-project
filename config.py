import os
from dotenv import load_dotenv


load_dotenv()

DB_URL = os.getenv("DB_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YANDEX_DISK_URL = os.getenv("YANDEX_DISK_URL")
YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN")
