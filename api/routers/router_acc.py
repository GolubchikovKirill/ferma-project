from fastapi import APIRouter, Depends
from sqlalchemy.future import select

from database.models import Account
from api.schemas.schemas_pydantic import AccountCreate
from database.session import AsyncSession, get_db
from service.openai_service import generate_name

router = APIRouter(prefix="", tags=["Аккаунты"])

@router.post(
    "/accounts/",
    tags=["Аккаунты"],
    summary="Создание аккаунта"
)
async def create_account(account_data: AccountCreate, db: AsyncSession = Depends(get_db)):
    # Мы больше не ищем по phone_number, так как его нет в модели
    query = select(Account).filter(Account.session_data == account_data.session_data)  # Предположим, что session_data уникально
    result = await db.execute(query)
    existing_account = result.scalar_one_or_none()

    if existing_account:
        return {"message": "Account with this session data already exists!"}

    # Генерация имени и фамилии через OpenAI
    first_name, last_name = await generate_name()

    # Если имя или фамилия не были сгенерированы, используем дефолтное значение
    username = f"{first_name}_{last_name}"

    # Теперь создаем новый аккаунт с использованием username
    new_account = Account(
        session_data=account_data.session_data,  # Используем session_data как уникальный идентификатор
        is_active=True,  # Аккаунт по умолчанию активен
        proxy_id=None,   # Если нет прокси, можно передать None
        username=username  # Добавляем сгенерированное имя пользователя
    )

    db.add(new_account)
    await db.commit()
    return {"message": "Account created successfully!"}