from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, Text, ForeignKey
from .session import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    phone_number: Mapped[str] = mapped_column(unique=True, index=True)
    session_data: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    proxy_id: Mapped[int | None] = mapped_column(ForeignKey("proxy.id"), nullable=True)

    # Данные для работы с Telegram(разбить на две таблицы??)
    api_id: Mapped[int] = mapped_column(nullable=False)
    api_hash: Mapped[str] = mapped_column(nullable=False)
    session_string: Mapped[str | None] = mapped_column(Text, nullable=True)
    telegram_id: Mapped[int | None] = mapped_column(unique=True, nullable=True)
    username: Mapped[str | None] = mapped_column(nullable=True)
    bot_token: Mapped[str | None] = mapped_column(nullable=True)

    tasks: Mapped[list["CommentTask"]] = relationship(back_populates="account")
    proxy: Mapped["Proxy"] = relationship(back_populates="account", uselist=False)



class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(Text)
    tasks: Mapped[list["CommentTask"]] = relationship(back_populates="channel")


class CommentTask(Base):
    __tablename__ = "comment_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    comment: Mapped[str] = mapped_column(Text)
    time_to_comment: Mapped[int]

    account: Mapped["Account"] = relationship(back_populates="tasks")
    channel: Mapped["Channel"] = relationship(back_populates="tasks")


class Proxy(Base):
    __tablename__ = "proxy"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ip_address: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    port: Mapped[int]
    login: Mapped[str]
    password: Mapped[str]

    account: Mapped["Account"] = relationship(back_populates="proxy", uselist=False)
