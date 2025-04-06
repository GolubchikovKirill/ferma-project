from fastapi import APIRouter, Form, HTTPException, Depends
from sqlalchemy.future import select
from typing import Optional
from database.models import Channel
from database.session import AsyncSession, get_db

router = APIRouter(prefix="", tags=["Каналы"])

@router.post(
    "/channels/",
    tags=["Каналы"],
    summary="Добавление канала"
)
async def create_channel(
        name: str = Form(...),
        description: Optional[str] = Form(None),
        db: AsyncSession = Depends(get_db)
):
    try:
        query = select(Channel).filter(Channel.name == name)
        result = await db.execute(query)
        existing_channel = result.scalar_one_or_none()

        if existing_channel:
            raise HTTPException(status_code=400, detail=f"Channel {name} already exists!")

        new_channel = Channel(name=name, description=description)
        db.add(new_channel)
        await db.commit()
        return {"message": "Channel created successfully!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete(
    "/channels/{channel_id}",
    tags=["Каналы"],
    summary="Удаление канала"
)
async def delete_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    channel = await db.get(Channel, channel_id)

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    await db.delete(channel)
    await db.commit()
    return {"message": "Channel deleted successfully!"}


@router.get(
    "/channels/all",
    tags=["Каналы"],
    summary="Получение полного списка каналов"
)
async def get_all_channels(db: AsyncSession = Depends(get_db)):
    query = select(Channel)
    result = await db.execute(query)
    channels = result.scalars().all()
    return {"channels": [channel.name for channel in channels]}