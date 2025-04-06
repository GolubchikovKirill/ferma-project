import asyncio
import random
from pathlib import Path
from loguru import logger
from pyrogram import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Account, Channel
from service.redis_service import check_rate_limit
from config import API_ID, API_HASH


TDATA_PATH = Path("tdata")


def build_socks5_proxy(account: Account) -> dict:
    """
    Формирует прокси-конфигурацию для Pyrogram клиента (SOCKS5).
    """
    if not account.proxy:
        logger.debug(f"[proxy] Прокси не указан для аккаунта {account.id}")
        return {}

    return {
        "proxy": {
            "scheme": "socks5",
            "hostname": account.proxy.ip_address,
            "port": account.proxy.port,
            "username": account.proxy.login,
            "password": account.proxy.password
        }
    }


async def is_session_valid(client: Client) -> bool:
    try:
        await client.connect()
        await client.get_me()
        return True
    except Exception as e:
        logger.warning(f"[!] Сессия невалидна: {e}")
        return False
    finally:
        await client.disconnect()


async def get_pyrogram_clients(db: AsyncSession) -> dict[int, Client]:
    """
    Получает клиентов Pyrogram на основе активных аккаунтов в базе данных.
    """
    result = await db.execute(select(Account).where(Account.is_active == True))
    accounts = result.scalars().all()

    clients = {}

    for account in accounts:
        session_folder = TDATA_PATH / account.session_data
        session_file = session_folder / f"{account.session_data}.session"

        if not session_file.exists():
            logger.warning(f"[!] .session файл не найден для аккаунта {account.id}: {session_file}")
            continue

        proxy_params = build_socks5_proxy(account)

        try:
            client = Client(
                name=account.session_data,
                workdir=session_folder,
                api_id=API_ID,
                api_hash=API_HASH,
                **proxy_params
            )

            if await is_session_valid(client):
                clients[account.id] = client
                logger.success(f"[✓] Клиент инициализирован: {account.username} (ID: {account.id})")
            else:
                logger.warning(f"[!] Невалидная сессия: {account.session_data}")

        except Exception as e:
            logger.error(f"[!] Ошибка создания клиента {account.id}: {e}")

    return clients


async def comment_on_post(client: Client, channel_name: str, post_id: int, comment_text: str) -> bool:
    try:
        await client.start()
        post = await client.get_messages(channel_name, message_ids=post_id)
        await post.reply(comment_text)
        logger.info(f"[✓] Комментарий отправлен в {channel_name} к посту {post_id}")
        return True
    except Exception as e:
        logger.error(f"[!] Ошибка при комментировании: {e}")
        return False
    finally:
        await client.disconnect()


async def start_commenting_loop(db: AsyncSession):
    """
    Основной цикл: получает клиентов, выбирает посты, оставляет комментарии.
    """
    while True:
        clients = await get_pyrogram_clients(db)

        if not clients:
            logger.warning("[!] Нет активных клиентов. Ждём 60 сек...")
            await asyncio.sleep(60)
            continue

        result = await db.execute(select(Channel))
        channels = result.scalars().all()

        for account_id, client in clients.items():
            if not await check_rate_limit(account_id):
                logger.info(f"[rate-limit] Пропущен аккаунт {account_id}")
                continue

            channel = random.choice(channels)

            try:
                posts = []
                async for post in client.get_chat_history(channel.name, limit=10):
                    posts.append(post.id)

                for idx, post_id in enumerate(posts):
                    if idx % 2 == 1:
                        comment_text = f"Комментарий к посту {post_id}"
                        success = await comment_on_post(client, channel.name, post_id, comment_text)
                        if success:
                            logger.success(f"[✓] Комментарий отправлен от аккаунта {account_id}")
                            await asyncio.sleep(random.randint(5, 15))

            except Exception as e:
                logger.error(f"[!] Ошибка аккаунта {account_id}: {e}")

        logger.info("[~] Итерация завершена. Пауза 60 сек...")
        await asyncio.sleep(60)