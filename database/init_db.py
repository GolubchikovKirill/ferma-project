""" Создание таблиц в БД """
import asyncio
from database.session import engine
from database.models import Base


async def init_db():
    async with engine.begin() as conn:
        print("Удаляем старые таблицы (с каскадным удалением зависимостей)...")
        await conn.run_sync(lambda sync_conn: Base.metadata.drop_all(sync_conn, checkfirst=True))

        print("Создаем новые таблицы...")
        await conn.run_sync(Base.metadata.create_all)

        print("База данных успешно инициализирована!")


if __name__ == "__main__":
    asyncio.run(init_db())