from fastapi import APIRouter, Depends
from sqlalchemy.future import select

from database.models import Account
from schemas.schemas_pydantic import AccountCreate
from database.session import AsyncSession, get_db
from service.openai_service import generate_name

router = APIRouter(prefix="", tags=["Аккаунты"])


@router.post(
    "/accounts/",
    tags=["Аккаунты"],
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
