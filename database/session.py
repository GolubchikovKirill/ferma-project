from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import DB_URL


engine = create_async_engine(DB_URL, echo=True)


AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass

# Асинхронный генератор сессии для FastAPI
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session