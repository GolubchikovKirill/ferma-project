import asyncio
import random
import os
from pyrogram import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Account, Channel
from service.openai_service import generate_comment
from service.yandex_disk_service import download_tdata_for_account, TDATA_LOCAL_PATH
from service.redis_service import check_rate_limit


async def get_pyrogram_clients(db: AsyncSession):
    """ Получение активных аккаунтов и создание Pyrogram клиентов с учётом tdata и прокси """
    query = select(Account).filter(Account.is_active == True)
    result = await db.execute(query)
    accounts = result.scalars().all()

    clients = {}
    for account in accounts:
        # Путь к tdata сессии для каждого аккаунта
        session_path = os.path.join(TDATA_LOCAL_PATH, f"tdata_{account.id}")  # Путь будет динамически генерироваться

        # Проверяем, существует ли локальный файл tdata
        if not os.path.exists(session_path):
            download_tdata_for_account(account.id)  # Если tdata нет, загружаем его

        # Проверяем, есть ли у аккаунта прокси
        proxy = account.proxy
        proxy_params = {}

        if proxy:
            proxy_params = {
                "proxy": {
                    "scheme": "socks5",  # Используем SOCKS5
                    "host": proxy.ip_address,
                    "port": proxy.port,
                    "username": proxy.login,
                    "password": proxy.password
                }
            }

        # Создаем клиента Pyrogram с учётом tdata и прокси
        clients[account.id] = Client(
            session_path,  # Используем путь к tdata сессии
            api_id=account.api_id,  # api_id нужен для работы с API
            api_hash=account.api_hash,  # api_hash для работы с API
            **proxy_params  # Передаем параметры прокси
        )

    return clients


async def comment_on_latest_post(client, channel_name, comment_text):
    """ Оставить комментарий под последним постом в канале """
    await client.start()
    try:
        posts = await client.get_chat_history(channel_name, limit=1)
        if posts:
            latest_post = posts[0].message_id
            await client.send_message(channel_name, comment_text, reply_to_message_id=latest_post)
            print(f"Commented on post {latest_post} in {channel_name}")
        else:
            print(f"No posts found in {channel_name}")
    except Exception as e:
        print(f"Error commenting in {channel_name}: {e}")
    finally:
        await client.stop()


async def start_commenting_loop(db: AsyncSession):
    """ Запускает процесс комментирования с учетом цикличности каналов и задержки """
    clients = await get_pyrogram_clients(db)

    # Получаем список всех каналов
    query = select(Channel)
    result = await db.execute(query)
    channels = result.scalars().all()

    if not channels:
        print("No channels found.")
        return

    # Словарь для отслеживания, какие каналы уже прокомментированы каждым аккаунтом
    commented_channels = {account_id: set() for account_id in clients.keys()}

    # Цикл комментирования
    while True:
        for account_id, client in clients.items():
            # Проверка на rate limit
            if not await check_rate_limit(account_id):
                print(f"Rate limit exceeded for account {account_id}, skipping...")
                continue

            # Получаем каналы, которые еще не были прокомментированы данным аккаунтом
            not_commented_channels = [channel for channel in channels if
                                      channel.id not in commented_channels[account_id]]

            if not_commented_channels:
                # Выбираем случайный канал, который еще не был прокомментирован этим аккаунтом
                selected_channel = random.choice(not_commented_channels)
                comment_text = await generate_comment("Текст последнего поста")  # Генерация комментария (заглушка)
                await comment_on_latest_post(client, selected_channel.name, comment_text)

                # Помечаем канал как прокомментированный для этого аккаунта
                commented_channels[account_id].add(selected_channel.id)
                print(f"Account {account_id} commented on {selected_channel.name}")

            # Если все каналы прокомментированы, начинаем заново
            if len(commented_channels[account_id]) == len(channels):
                commented_channels[account_id].clear()  # Очищаем список, чтобы начать с первого канала
                print(f"Account {account_id} has commented on all channels. Restarting loop.")

            # Задержка перед следующим комментарием
            await asyncio.sleep(10)