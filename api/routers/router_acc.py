from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from service.openai_service import generate_name
from service.yandex_disk_service import process_new_tdata
from database.models import Account
from database.session import AsyncSession, get_db
import logging

router = APIRouter(prefix="", tags=["Аккаунты и Яндекс.Диск"])
logger = logging.getLogger(__name__)

@router.post(
    "/accounts/sync-tdata",
    tags=["Аккаунты и Яндекс.Диск"],
    summary="Загрузка TData из Яндекс.Диска и создание аккаунтов"
)
async def sync_tdata_and_create_accounts(db: AsyncSession = Depends(get_db)):
    try:
        created_folders = await process_new_tdata(db)

        if not created_folders:
            return {"status": "success", "message": "No new TData folders found"}

        for folder_name in created_folders:
            account = (await db.execute(
                select(Account).filter(Account.username == folder_name)
            )).scalar_one()

            if not account.first_name or not account.last_name:
                first_name, last_name = await generate_name()
                account.first_name = first_name
                account.last_name = last_name
                db.add(account)

        await db.commit()
        return {"status": "success", "created_accounts": len(created_folders)}

    except Exception as e:
        logger.error(f"Error during sync: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))