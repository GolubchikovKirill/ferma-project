from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from database.models import Account
from database.session import AsyncSession, get_db
from service.pyrogram_service import start_commenting_loop
from service.openai_service import generate_comment

router = APIRouter(prefix="", tags=["Основная логика"])

@router.get(
    "/start_commenting/",
    tags=["Основная логика"],
    summary="Запуск процесса комментирования"
)
async def start_commenting(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    logs = []

    try:
        query = select(Account).filter(Account.is_active == True)
        result = await db.execute(query)
        accounts = result.scalars().all()

        if not accounts:
            logs.append("No active accounts found.")
            return JSONResponse(content={"success": False, "message": "No active accounts found.", "logs": logs})

        background_tasks.add_task(start_commenting_loop, db)
        logs.append("Commenting process started successfully.")
        return JSONResponse(content={"success": True, "message": "Commenting process started!", "logs": logs})

    except Exception as e:
        logs.append(f"Error: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": "An error occurred while starting the commenting process.",
                     "logs": logs})

@router.post(
    "/generate_comment/",
    tags=["Основная логика"],
    summary="Генерация комментария"
)
async def generate_comment_endpoint(post_text: str, user_prompt: Optional[str] = None):
    """Генерация комментария на основе текста поста и выбранного или кастомного промпта"""
    try:
        comment = await generate_comment(post_text, user_prompt)
        return JSONResponse(content={"success": True, "comment": comment})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while generating the comment: {str(e)}")