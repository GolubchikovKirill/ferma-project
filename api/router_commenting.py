from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.future import select

from database.models import Account
from database.session import AsyncSession, get_db
from service.pyrogram_service import start_commenting_loop

router = APIRouter(prefix="", tags=["Основная логика"])

@router.get(
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