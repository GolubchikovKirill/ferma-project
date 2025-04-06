import io
import os
import zipfile
import requests
import urllib.parse

from sqlalchemy import select

from config import (
    YANDEX_DISK_TOKEN,
    YANDEX_DISK_URL,
    LOCAL_TDATA_PATH,
    REMOTE_TDATA_PATH,
    REMOTE_TDATA_USED
)
from database.models import Account
from database.session import AsyncSessionLocal


def check_remote_folder(folder: str) -> bool:
    """Проверяет существование папки на Яндекс.Диске"""
    headers = {'Authorization': f'OAuth {YANDEX_DISK_TOKEN}'}
    encoded_path = urllib.parse.quote(folder)
    response = requests.get(
        f"{YANDEX_DISK_URL}/resources?path={encoded_path}",
        headers=headers
    )
    return response.status_code == 200


def ensure_remote_folders():
    """Создает необходимые папки на Яндекс.Диске"""
    for folder in [REMOTE_TDATA_PATH, REMOTE_TDATA_USED]:
        if not check_remote_folder(folder):
            response = requests.put(
                f"{YANDEX_DISK_URL}/resources?path={urllib.parse.quote(folder)}",
                headers={'Authorization': f'OAuth {YANDEX_DISK_TOKEN}'}
            )
            if response.status_code != 201:
                print(f"Ошибка при создании папки {folder}: {response.text}")


def get_available_archives() -> list:
    """Возвращает список доступных архивов tdata"""
    headers = {'Authorization': f'OAuth {YANDEX_DISK_TOKEN}'}
    response = requests.get(
        f"{YANDEX_DISK_URL}/resources?path={urllib.parse.quote(REMOTE_TDATA_PATH)}",
        headers=headers
    )
    return [
        item["name"]
        for item in response.json().get("_embedded", {}).get("items", [])
        if item["type"] == "file" and item["name"].endswith(".zip")
    ]


def download_and_process_archive(archive_name: str) -> str:
    """Скачивает и обрабатывает архив"""
    # Скачивание файла
    download_url = f"{YANDEX_DISK_URL}/resources/download?path={urllib.parse.quote(f'{REMOTE_TDATA_PATH}/{archive_name}')}"
    response = requests.get(download_url, headers={'Authorization': f'OAuth {YANDEX_DISK_TOKEN}'})
    file_content = requests.get(response.json()['href']).content

    # Извлечение номера аккаунта из имени файла
    account_id = os.path.splitext(archive_name)[0]
    extract_path = os.path.join(LOCAL_TDATA_PATH, f"tdata_{account_id}")

    # Распаковка
    try:
        with zipfile.ZipFile(io.BytesIO(file_content)) as zip_ref:
            zip_ref.extractall(extract_path)
    except zipfile.BadZipFile:
        print(f"Ошибка: архив {archive_name} повреждён!")
        return None

    # Перемещение архива
    requests.post(
        f"{YANDEX_DISK_URL}/resources/move",
        params={
            'from': urllib.parse.quote(f"{REMOTE_TDATA_PATH}/{archive_name}"),
            'path': urllib.parse.quote(f"{REMOTE_TDATA_USED}/{archive_name}")
        },
        headers={'Authorization': f'OAuth {YANDEX_DISK_TOKEN}'}
    )

    return account_id


async def process_new_tdata():
    """Основной процесс обработки новых tdata"""
    ensure_remote_folders()
    archives = get_available_archives()

    async with AsyncSessionLocal() as session:
        for archive in archives:
            account_id = download_and_process_archive(archive)

            # Проверка на существование аккаунта в базе данных
            existing_account = await session.execute(
                select(Account).filter(Account.id == int(account_id))
            )
            if not existing_account.scalar():
                # Создание записи в БД
                account = Account(
                    id=int(account_id),
                    username=f"account_{account_id}",
                    is_active=True
                )
                session.add(account)

        await session.commit()