from typing import Optional

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, Field

from database.models import Account, Proxy, Channel
from database.session import get_db
from service.openai_utils import generate_name
from service.pyrogram_service import start_commenting_loop


# Модели для создания данных
class AccountCreate(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15, pattern=r'^\+?[0-9]+$')
    api_id: int
    api_hash: str
    session_string: Optional[str] = None
    telegram_id: Optional[int] = None
    bot_token: Optional[str] = None

    class Config:
        from_attributes = True


class ProxyAssignment(BaseModel):
    proxy_id: int


class ProxyCreate(BaseModel):
    ip_address: str
    port: int
    login: Optional[str] = None
    password: Optional[str] = None


app = FastAPI(title="Telegram Account Manager")

# Инициализация шаблонов
templates = Jinja2Templates(directory="templates")

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")


# Главная страница
@app.get(
    "/",
    response_class=HTMLResponse,
    tags="Шаблоны",
    summary="Главная страница")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Создание аккаунта
@app.post(
    "/accounts/",
    tags="Аккаунты",
    summary="Создание аккаунта"
)
async def create_account(account_data: AccountCreate, db: AsyncSession = Depends(get_db)):
    query = select(Account).filter(Account.phone_number == account_data.phone_number)
    result = await db.execute(query)
    existing_account = result.scalar_one_or_none()

    if existing_account:
        return {"message": f"Account with phone number {account_data.phone_number} already exists!"}

    # Генерация имени и фамилии через OpenAI
    first_name, last_name = await generate_name()

    # Если имя или фамилия не были сгенерированы, используем дефолтное значение
    username = f"{first_name}_{last_name}"

    new_account = Account(
        phone_number=account_data.phone_number,
        api_id=account_data.api_id,
        api_hash=account_data.api_hash,
        session_string=account_data.session_string,
        telegram_id=account_data.telegram_id,
        username=username,
        bot_token=account_data.bot_token
    )

    db.add(new_account)
    await db.commit()
    return {"message": "Account created successfully!"}


# Запуск процесса комментирования
@app.get(
    "/start_commenting/",
    tags="Основная логика",
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


# Присваивание прокси аккаунту
@app.put(
    "/assign_proxy/{account_id}",
    tags="Прокси",
    summary="Присваивание прокси аккаунту"
)
async def assign_proxy(account_id: int, proxy_data: ProxyAssignment, db: AsyncSession = Depends(get_db)):
    account = await db.get(Account, account_id)
    proxy = await db.get(Proxy, proxy_data.proxy_id)

    if not account or not proxy:
        return {"message": "Account or Proxy not found!"}

    account.proxy = proxy
    await db.commit()
    return {"message": "Proxy assigned successfully!"}


# Добавление канала
@app.post(
    "/channels/",
    tags="Каналы",
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


# Удаление канала
@app.delete(
    "/channels/{channel_id}",
    tags="Каналы",
    summary="Удаление канала"
)
async def delete_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    channel = await db.get(Channel, channel_id)

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    await db.delete(channel)
    await db.commit()
    return {"message": "Channel deleted successfully!"}


# Получение полного списка каналов
@app.get(
    "/channels/all",
    tags="Каналы",
    summary="Получение полного списка каналов"
)
async def get_all_channels(db: AsyncSession = Depends(get_db)):
    query = select(Channel)
    result = await db.execute(query)
    channels = result.scalars().all()
    return {"channels": [channel.name for channel in channels]}


# Добавление прокси
@app.post(
    "/proxies/",
    tags="Прокси",
    summary="Добавление прокси"
)
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


# Отображение списка аккаунтов
@app.get(
    "/accounts/",
    response_class=HTMLResponse,
    tags="Шаблоны",
    summary="Отображение списка аккаунтов"
)
async def show_accounts(request: Request, db: AsyncSession = Depends(get_db)):
    query = select(Account)
    result = await db.execute(query)
    accounts = result.scalars().all()

    return templates.TemplateResponse("accounts.html", {"request": request, "accounts": accounts})


# Отображение списка каналов
@app.get(
    "/channels/",
    response_class=HTMLResponse,
    tags="Шаблоны",
    summary="Отображение списка каналов"
)
async def show_channels(request: Request, db: AsyncSession = Depends(get_db)):
    query = select(Channel)
    result = await db.execute(query)
    channels = result.scalars().all()

    return templates.TemplateResponse("channels.html", {"request": request, "channels": channels})


# Отображение списка прокси
@app.get(
    "/proxies/",
    response_class=HTMLResponse,
    tags="Шаблоны",
    summary="Отображение списка прокси"
)
async def show_proxies(request: Request, db: AsyncSession = Depends(get_db)):
    query = select(Proxy)
    result = await db.execute(query)
    proxies = result.scalars().all()

    return templates.TemplateResponse("proxies.html", {"request": request, "proxies": proxies})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
