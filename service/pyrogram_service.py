from pyrogram import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models import Account, Channel
from service.openai_utils import generate_comment


# Функция для получения сессий Pyrogram для всех аккаунтов
async def get_pyrogram_clients(db: AsyncSession):
    query = select(Account).filter(Account.is_active == True)
    result = await db.execute(query)
    accounts = result.scalars().all()

    clients = {}
    for account in accounts:
        session_name = account.phone_number  # Используем номер телефона как уникальный session_name
        clients[account.id] = Client(
            session_name,
            api_id=account.api_id,
            api_hash=account.api_hash,
            session_string=account.session_string
        )

    return clients


# Функция для написания комментариев под последним постом
async def comment_on_latest_post(client, channel_name, comment_text):
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


# Фоновая функция для комментирования по команде
async def start_commenting_loop(db: AsyncSession):
    clients = await get_pyrogram_clients(db)

    # Получаем список каналов
    query = select(Channel)
    result = await db.execute(query)
    channels = result.scalars().all()

    for channel in channels:
        active_clients = list(clients.values())[:2]  # Берем 2 аккаунта
        if not active_clients:
            print(f"No active clients for {channel.name}")
            continue

        for client in active_clients:
            comment_text = await generate_comment("Текст последнего поста")  # Заглушка
            await comment_on_latest_post(client, channel.name, comment_text)