import json
import redis.asyncio as redis
from config import settings
from contextlib import asynccontextmanager

# Инициализация Redis клиента с использованием настроек
redis_client = redis.from_url(
    f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
    password=settings.redis_password if settings.redis_password else None,
    decode_responses=True  # автоматически декодировать ответы в строки
)

# Context manager для работы с Redis
@asynccontextmanager
async def redis_connection():
    try:
        # Используем клиент с пулом соединений
        yield redis_client
    finally:
        # Закрытие соединения при завершении работы
        await redis_client.close()

# Функция для добавления задачи в поток Redis
async def add_to_stream(stream_name: str, message: dict):
    async with redis_connection() as client:
        await client.xadd(stream_name, message)

# Функция для получения сообщений из потока Redis
async def get_messages_from_stream(stream_name: str, count: int = 10):
    async with redis_connection() as client:
        # Получение сообщений из потока
        messages = await client.xrange(stream_name, count=count)
        return [json.loads(msg[b"message"].decode("utf-8")) for msg in messages]

# Проверка лимита частоты через Redis
async def check_rate_limit(account_id: int, limit: int = 5, window: int = 60):
    async with redis_connection() as client:
        key = f"rate_limit:{account_id}"
        # Получаем текущее значение счетчика
        count = await client.get(key)
        if count is None:
            # Если счетчик не существует, создаем его и устанавливаем TTL
            await client.setex(key, window, 1)
            return True
        elif int(count) < limit:
            # Если лимит не превышен, увеличиваем счетчик
            await client.incr(key)
            return True
        return False

# Пинг Redis
async def ping():
    async with redis_connection() as client:
        await client.ping()