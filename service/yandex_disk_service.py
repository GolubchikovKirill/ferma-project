import os
import zipfile
import requests
from config import YANDEX_DISK_TOKEN, YANDEX_DISK_URL

TDATA_LOCAL_PATH = '/TDATA'


def upload_tdata_for_account(account_id: int):
    """ Загружает tdata на Яндекс.Диск для указанного аккаунта """
    local_session_path = get_session_path(account_id)
    remote_session_path = f"/TDATA/{account_id}/tdata.zip"
    upload_to_yandex_disk(local_session_path, remote_session_path)


def download_tdata_for_account(account_id: int):
    """ Скачивает tdata для аккаунта с Яндекс.Диска """
    remote_session_path = f"/TDATA/{account_id}/tdata.zip"
    local_session_path = get_session_path(account_id)

    # Проверяем, существует ли файл локально
    if not os.path.exists(local_session_path):
        download_from_yandex_disk(remote_session_path, local_session_path)

        # Распаковка
        if os.path.exists(local_session_path):
            extract_path = os.path.join(TDATA_LOCAL_PATH, f"tdata_{account_id}")
            if not os.path.exists(extract_path):
                os.makedirs(extract_path)

            with zipfile.ZipFile(local_session_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            print(f"Архив {local_session_path} успешно распакован в {extract_path}")
            os.remove(local_session_path)  # Удаляем архив после распаковки
        else:
            print(f"Ошибка: zip-файл {local_session_path} не найден после скачивания")
    else:
        print(f"Файл сессии для аккаунта {account_id} уже существует локально.")


def upload_to_yandex_disk(local_path: str, remote_path: str):
    """ Загружает файл на Яндекс.Диск """
    headers = {'Authorization': f'OAuth {YANDEX_DISK_TOKEN}'}

    # Получаем ссылку на загрузку
    upload_url = f'{YANDEX_DISK_URL}/upload?path={remote_path}&overwrite=true'
    response = requests.get(upload_url, headers=headers)

    if response.status_code != 200:
        print(f"Ошибка получения ссылки для загрузки: {response.json()}")
        return

    upload_link = response.json()['href']

    # Загружаем файл
    with open(local_path, 'rb') as f:
        upload_response = requests.put(upload_link, files={'file': f})

    if upload_response.status_code == 201:
        print(f"Файл {local_path} успешно загружен на Яндекс.Диск по пути {remote_path}")
    else:
        print(f"Ошибка загрузки файла: {upload_response.json()}")


def download_from_yandex_disk(remote_path: str, local_path: str):
    """ Скачивает файл с Яндекс.Диска """
    headers = {'Authorization': f'OAuth {YANDEX_DISK_TOKEN}'}

    # Получаем ссылку на скачивание
    download_url = f'{YANDEX_DISK_URL}/download?path={remote_path}'
    response = requests.get(download_url, headers=headers)

    if response.status_code != 200:
        print(f"Ошибка получения ссылки для скачивания: {response.json()}")
        return

    download_link = response.json()['href']

    # Загружаем файл
    download_response = requests.get(download_link)

    if download_response.status_code == 200:
        with open(local_path, 'wb') as f:
            f.write(download_response.content)
        print(f"Файл {remote_path} успешно скачан с Яндекс.Диска на {local_path}")
    else:
        print(f"Ошибка скачивания файла: {download_response.json()}")


def ensure_tdata_folder_exists():
    """ Проверяем, существует ли локальная папка для tdata. Если нет, создаем её. """
    if not os.path.exists(TDATA_LOCAL_PATH):
        os.makedirs(TDATA_LOCAL_PATH)
        print(f"Создана папка для tdata: {TDATA_LOCAL_PATH}")
    else:
        print(f"Папка для tdata уже существует: {TDATA_LOCAL_PATH}")


def get_session_path(account_id: int):
    """ Генерирует путь к файлу сессии для аккаунта. """
    return os.path.join(TDATA_LOCAL_PATH, f"session_{account_id}")