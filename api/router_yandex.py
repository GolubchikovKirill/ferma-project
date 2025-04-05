import os
from schemas.schemas_pydantic import AccountRequest
from fastapi import APIRouter, HTTPException
from service.yandex_disk_service import upload_tdata_for_account, download_tdata_for_account, \
    ensure_tdata_folder_exists, get_session_path

router = APIRouter(prefix="", tags=["Яндекс.Диск"])

# Проверка существования tdata папки (если необходимо)
async def lifespan():
    """ Инициализация папки tdata при запуске. """
    ensure_tdata_folder_exists()
    yield  # Завершение приложения


# Загружает tdata на Яндекс.Диск
@router.post(
    "/upload_tdata/",
    tags=["Яндекс.Диск"],
    summary="Загрузка tdata на Яндекс.Диск"
)
async def upload_tdata(account_request: AccountRequest):
    try:
        upload_tdata_for_account(account_request.account_id)
        return {"message": f"Tdata для аккаунта {account_request.account_id} успешно загружено."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Скачивает tdata с Яндекс.Диска
@router.post(
    "/download_tdata/",
    tags=["Яндекс.Диск"],
    summary="Скачивание tdata с Яндекс.Диска"
)
async def download_tdata(account_request: AccountRequest):
    try:
        download_tdata_for_account(account_request.account_id)
        return {"message": f"Tdata для аккаунта {account_request.account_id} успешно скачано."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Проверка наличия tdata
@router.get(
    "/check_tdata/{account_id}",
    tags=["Яндекс.Диск"],
    summary="Проверка наличия tdata"
)
async def check_tdata(account_id: int):
    session_path = get_session_path(account_id)  # Используем функцию для получения пути

    if os.path.exists(session_path):
        return {"message": f"Tdata для аккаунта {account_id} существует."}
    else:
        return {"message": f"Tdata для аккаунта {account_id} не найдено."}