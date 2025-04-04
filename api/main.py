import os

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models import Account
from database.session import get_db
from service.pyrogram_service import start_commenting_loop
from api import routers

app = FastAPI(title="Telegram Account Manager")
for router in routers:
    app.include_router(router)

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Запуск процесса комментирования
@app.get(
    "/start_commenting/",
    tags=["Основная логика"],
    summary="Запуск процесса комментирования"
)
async def start_commenting(db: AsyncSession = Depends(get_db)):
    logs = []

    try:
        # Получаем список активных аккаунтов
        query = select(Account).filter(Account.is_active == True)
        result = await db.execute(query)
        accounts = result.scalars().all()

        if not accounts:
            logs.append("No active accounts found.")
            return JSONResponse(content={"success": False, "message": "No active accounts found.", "logs": logs})

        # Запуск цикла комментирования
        await start_commenting_loop(db)

        logs.append("Commenting process started successfully.")
        return JSONResponse(content={"success": True, "message": "Commenting process started!", "logs": logs})

    except Exception as e:
        logs.append(f"Error: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": "An error occurred while starting the commenting process.",
                     "logs": logs})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
