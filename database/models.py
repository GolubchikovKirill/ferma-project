from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Text, ForeignKey
from .session import Base

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phone_number: Mapped[str] = mapped_column(String, unique=True, index=True)
    session_data: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    proxy_id: Mapped[int | None] = mapped_column(ForeignKey("proxy.id"), nullable=True)

    # Данные для работы с Telegram
    api_id: Mapped[int] = mapped_column(Integer, nullable=False)
    api_hash: Mapped[str] = mapped_column(String, nullable=False)
    session_string: Mapped[str | None] = mapped_column(Text, nullable=True)
    telegram_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    bot_token: Mapped[str | None] = mapped_column(String, nullable=True)

    tasks: Mapped[list["CommentTask"]] = relationship(back_populates="account")
    proxy: Mapped["Proxy"] = relationship(back_populates="account", uselist=False)


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(Text)

    tasks: Mapped[list["CommentTask"]] = relationship(back_populates="channel")


class CommentTask(Base):
    __tablename__ = "comment_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    comment: Mapped[str] = mapped_column(Text)
    time_to_comment: Mapped[int] = mapped_column(Integer)

    account: Mapped["Account"] = relationship(back_populates="tasks")
    channel: Mapped["Channel"] = relationship(back_populates="tasks")


class Proxy(Base):
    __tablename__ = "proxy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ip_address: Mapped[str] = mapped_column(String, unique=True, index=True)
    port: Mapped[int] = mapped_column(Integer)
    login: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)

    account: Mapped["Account"] = relationship(back_populates="proxy", uselist=False)