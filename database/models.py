from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    session_data = Column(Text)
    is_active = Column(Boolean, default=True)
    proxy_id = Column(Integer, ForeignKey("proxy.id"), nullable=True)  # Связь с Proxy

    # Добавленные поля для работы с Telegram
    api_id = Column(Integer, nullable=False)
    api_hash = Column(String, nullable=False)
    session_string = Column(Text, nullable=True)  # Строка сессии для Pyrogram
    telegram_id = Column(Integer, unique=True, nullable=True)
    username = Column(String, nullable=True)  # Имя пользователя Telegram (опционально)
    bot_token = Column(String, nullable=True)  # Токен бота

    tasks = relationship("CommentTask", back_populates="account")
    proxy = relationship("Proxy", back_populates="account")  # Добавлена связь


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)

    tasks = relationship("CommentTask", back_populates="channel")


class CommentTask(Base):
    __tablename__ = 'comment_tasks'

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    channel_id = Column(Integer, ForeignKey('channels.id'))
    comment = Column(Text)
    time_to_comment = Column(Integer)

    account = relationship("Account", back_populates="tasks")
    channel = relationship("Channel", back_populates="tasks")


class Proxy(Base):
    __tablename__ = 'proxy'

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True)
    port = Column(Integer)
    login = Column(String)
    password = Column(String)

    account = relationship("Account", back_populates="proxy", uselist=False)  # Один аккаунт - один прокси