from fastapi import APIRouter, Depends
from database.models import Account, Proxy
from database.session import AsyncSession, get_db
from sqlalchemy.future import select
from api.schemas.schemas_pydantic import ProxyAssignment, ProxyCreate

router = APIRouter(prefix="", tags=["Прокси"])

@router.put(
    "/assign_proxy/{account_id}",
    tags=["Прокси"],
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


@router.post(
    "/proxies/",
    tags=["Прокси"],
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