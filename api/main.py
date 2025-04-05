import uvicorn
from fastapi import FastAPI
from api import routers
from fastapi.staticfiles import StaticFiles
import os
from service import redis_service


# Использование lifespan для управления жизненным циклом приложения
async def lifespan(_):
    # Инициализация при старте приложения
    try:
        await redis_service.ping()
        print("Redis подключен успешно")
    except Exception as e:
        print(f"Ошибка подключения к Redis: {e}")

    yield  # Это место, где FastAPI будет работать

    # Завершение при остановке приложения
    await redis_service.close()


app = FastAPI(
    title="Telegram Account Manager",
    lifespan=lifespan
)


for router in routers:
    app.include_router(router)

# Статика на уровне приложения
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)