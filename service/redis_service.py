import json
import redis.asyncio as redis
from config import settings

# Инициализация Redis клиента с использованием настроек из config.py
redis_client = redis.from_url(
    f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
    password=settings.redis_password if settings.redis_password else None
)

# Функция для добавления задачи в поток Redis
async def add_to_stream(stream_name: str, message: dict):
    await redis_client.xadd(stream_name, message)

# Функция для получения сообщений из потока Redis
async def get_messages_from_stream(stream_name: str, count: int = 10):
    messages = await redis_client.xrange(stream_name, count=count)
    return [json.loads(msg[b"message"].decode("utf-8")) for msg in messages]

# Проверка лимита частоты через Redis
async def check_rate_limit(account_id: int, limit: int = 5, window: int = 60):
    key = f"rate_limit:{account_id}"
    count = await redis_client.get(key)
    if count is None:
        await redis_client.setex(key, window, 1)
        return True
    elif int(count) < limit:
        await redis_client.incr(key)
        return True
    return False

# Пинг Redis
async def ping():
    await redis_client.ping()

# Закрытие соединения с Redis
async def close():
    await redis_client.close()