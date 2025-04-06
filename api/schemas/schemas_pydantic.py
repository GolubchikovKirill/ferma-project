from pydantic import BaseModel
from typing import Optional


class AccountCreate(BaseModel):
    session_data: str
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

class GenerateCommentRequest(BaseModel):
    post_text: str
    user_prompt: Optional[str] = None