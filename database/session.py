from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import DB_URL


engine = create_async_engine(DB_URL, echo=True)


# Создаем асинхронную сессию
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Функция для получения сессии
async def get_db():
    async with async_session() as session:
        yield session