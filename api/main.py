from typing import Optional

import uvicorn
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models import Account, Proxy, CommentTask, Channel
from database.session import get_db
from service.openai_utils import generate_name, generate_comment
from service.pyrogram_service import start_commenting_loop


class AccountCreate(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15, pattern=r'^\+?[0-9]+$')
    api_id: int
    api_hash: str
    session_string: Optional[str] = None
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    bot_token: Optional[str] = None

    class Config:
        orm_mode = True


class TaskCreate(BaseModel):
    account_id: int
    channel_id: int
    post_text: str
    time_to_comment: int


class ProxyAssignment(BaseModel):
    proxy_id: int


class ChannelCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProxyCreate(BaseModel):
    ip_address: str
    port: int
    login: Optional[str] = None
    password: Optional[str] = None


app = FastAPI(title="Backend")


@app.post("/accounts/")
async def create_account(account_data: AccountCreate, db: AsyncSession = Depends(get_db)):
    query = select(Account).filter(Account.phone_number == account_data.phone_number)
    result = await db.execute(query)
    existing_account = result.scalar_one_or_none()

    if existing_account:
        return {"message": f"Account with phone number {account_data.phone_number} already exists!"}

    first_name, last_name = await generate_name()

    new_account = Account(
        phone_number=account_data.phone_number,
        api_id=account_data.api_id,
        api_hash=account_data.api_hash,
        session_string=account_data.session_string,
        telegram_id=account_data.telegram_id,
        username=account_data.username or f"{first_name}_{last_name}",
        bot_token=account_data.bot_token
    )

    db.add(new_account)
    await db.commit()
    return {"message": "Account created successfully!"}


@app.post("/tasks/")
async def create_task(task_data: TaskCreate, db: AsyncSession = Depends(get_db)):
    query = select(Account).filter(Account.id == task_data.account_id)
    result = await db.execute(query)
    account = result.scalar_one_or_none()

    if not account:
        return {"message": "Account not found!"}

    query = select(Channel).filter(Channel.id == task_data.channel_id)
    result = await db.execute(query)
    channel = result.scalar_one_or_none()

    if not channel:
        return {"message": "Channel not found!"}

    generated_comment = await generate_comment(task_data.post_text)

    new_task = CommentTask(
        account_id=task_data.account_id,
        channel_id=task_data.channel_id,
        comment=generated_comment,
        time_to_comment=task_data.time_to_comment
    )
    db.add(new_task)
    await db.commit()

    return {"message": "Comment task created successfully!"}


@app.get("/start_commenting/")
async def start_commenting(db: AsyncSession = Depends(get_db)):
    """Запускает процесс комментирования"""
    await start_commenting_loop(db)
    return {"message": "Commenting started successfully!"}


@app.put("/assign_proxy/{account_id}")
async def assign_proxy(account_id: int, proxy_data: ProxyAssignment, db: AsyncSession = Depends(get_db)):
    account = await db.get(Account, account_id)
    proxy = await db.get(Proxy, proxy_data.proxy_id)

    if not account or not proxy:
        return {"message": "Account or Proxy not found!"}

    account.proxy = proxy
    await db.commit()
    return {"message": "Proxy assigned successfully!"}


@app.post("/channels/")
async def create_channel(channel_data: ChannelCreate, db: AsyncSession = Depends(get_db)):
    query = select(Channel).filter(Channel.name == channel_data.name)
    result = await db.execute(query)
    existing_channel = result.scalar_one_or_none()

    if existing_channel:
        return {"message": f"Channel {channel_data.name} already exists!"}

    new_channel = Channel(name=channel_data.name, description=channel_data.description)
    db.add(new_channel)
    await db.commit()
    return {"message": "Channel created successfully!"}


@app.post("/proxies/")
async def create_proxy(proxy_data: ProxyCreate, db: AsyncSession = Depends(get_db)):
    query = select(Proxy).filter(Proxy.ip_address == proxy_data.ip_address, Proxy.port == proxy_data.port)
    result = await db.execute(query)
    existing_proxy = result.scalar_one_or_none()

    if existing_proxy:
        return {"message": f"Proxy {proxy_data.ip_address}:{proxy_data.port} already exists!"}

    new_proxy = Proxy(
        ip_address=proxy_data.ip_address,
        port=proxy_data.port,
        login=proxy_data.login,
        password=proxy_data.password
    )

    db.add(new_proxy)
    await db.commit()
    return {"message": "Proxy created successfully!"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)