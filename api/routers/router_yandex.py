from fastapi import APIRouter, HTTPException
from service.yandex_disk_service import process_new_tdata

router = APIRouter(prefix="/yandex", tags=["Яндекс.Диск"])

@router.post("/sync-tdata", summary="Синхронизация новых tdata с Яндекс.Диска")
async def sync_tdata_endpoint():
    try:
        await process_new_tdata()
        return {"status": "success", "message": "TData synchronized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))