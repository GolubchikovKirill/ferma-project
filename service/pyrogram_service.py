import asyncio
import random
import os
from pyrogram import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from config import LOCAL_TDATA_PATH
from database.models import Account, Channel
from service.redis_service import check_rate_limit


async def get_pyrogram_clients(db: AsyncSession):
    """Инициализация клиентов на основе аккаунтов из БД"""
    result = await db.execute(select(Account).filter(Account.is_active == True))
    accounts = result.scalars().all()

    clients = {}
    for account in accounts:
        session_path = os.path.join(LOCAL_TDATA_PATH, f"tdata_{account.id}")

        if not os.path.exists(session_path):
            continue  # Пропускаем несуществующие сессии

        proxy_params = {}
        if account.proxy:
            proxy_params = {
                "proxy": {
                    "scheme": "socks5",
                    "hostname": account.proxy.ip_address,
                    "port": account.proxy.port,
                    "username": account.proxy.login,
                    "password": account.proxy.password
                }
            }

        clients[account.id] = Client(
            name=str(account.id),
            workdir=session_path,
            api_id=account.api_id,
            api_hash=account.api_hash,
            **proxy_params
        )

    return clients


async def comment_on_latest_post(client: Client, channel_name: str, comment_text: str):
    """Комментирование последнего поста"""
    await client.start()
    try:
        async for post in client.get_chat_history(channel_name, limit=1):
            await post.reply(comment_text)
            return True
    except Exception as e:
        print(f"Ошибка комментирования: {e}")
        return False
    finally:
        await client.stop()


async def start_commenting_loop(db: AsyncSession):
    """Основной цикл комментирования"""
    clients = await get_pyrogram_clients(db)
    channels = (await db.execute(select(Channel))).scalars().all()

    while True:
        for account_id, client in clients.items():
            if not await check_rate_limit(account_id):
                continue

            channel = random.choice(channels)
            comment_text = f"Сгенерированный комментарий для {channel.name}"

            if await comment_on_latest_post(client, channel.name, comment_text):
                print(f"Аккаунт {account_id} прокомментировал {channel.name}")

            await asyncio.sleep(random.randint(10, 30))