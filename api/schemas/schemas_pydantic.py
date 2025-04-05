from pydantic import BaseModel, Field
from typing import Optional


class AccountCreate(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=15, pattern=r'^\+?[0-9]+$')
    api_id: int
    api_hash: str
    session_string: Optional[str] = None
    telegram_id: Optional[int] = None
    bot_token: Optional[str] = None

    class Config:
        from_attributes = True


class ProxyAssignment(BaseModel):
    proxy_id: int


class ProxyCreate(BaseModel):
    ip_address: str
    port: int
    login: Optional[str] = None
    password: Optional[str] = None

class AccountRequest(BaseModel):
    account_id: int
