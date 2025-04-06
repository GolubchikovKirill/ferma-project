import os
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.future import select
from database.models import Channel, Proxy, Account
from database.session import get_db, AsyncSession

router = APIRouter(prefix="", tags=["Шаблоны"])

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get(
    "/",
    response_class=HTMLResponse,
    tags=["Шаблоны"],
    summary="Главная страница"
)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get(
    "/accounts/",
    response_class=HTMLResponse,
    tags=["Шаблоны"],
    summary="Отображение списка аккаунтов"
)
async def show_accounts(request: Request, db: AsyncSession = Depends(get_db)):
    query = select(Account)
    result = await db.execute(query)
    accounts = result.scalars().all()

    return templates.TemplateResponse("accounts.html", {"request": request, "accounts": accounts})


@router.get(
    "/channels/",
    response_class=HTMLResponse,
    tags=["Шаблоны"],
    summary="Отображение списка каналов"
)
async def show_channels(request: Request, db: AsyncSession = Depends(get_db)):
    query = select(Channel)
    result = await db.execute(query)
    channels = result.scalars().all()

    return templates.TemplateResponse("channels.html", {"request": request, "channels": channels})


@router.get(
    "/proxies/",
    response_class=HTMLResponse,
    tags=["Шаблоны"],
    summary="Отображение списка прокси"
)
async def show_proxies(request: Request, db: AsyncSession = Depends(get_db)):
    query = select(Proxy)
    result = await db.execute(query)
    proxies = result.scalars().all()

    return templates.TemplateResponse("proxies.html", {"request": request, "proxies": proxies})
