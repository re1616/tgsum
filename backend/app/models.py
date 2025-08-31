from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True)
    tz: Mapped[str] = mapped_column(String(64), default="Europe/Helsinki")
    digest_hour: Mapped[int] = mapped_column(Integer, default=8)
    max_items: Mapped[int] = mapped_column(Integer, default=15)
    min_score: Mapped[float] = mapped_column(Float, default=0.4)
    bot_chat_id: Mapped[str | None] = mapped_column(String(64), unique=True)
    link_code: Mapped[str | None] = mapped_column(String(16), index=True, unique=True)
    topics: Mapped[str | None] = mapped_column(Text)             # CSV ключевые слова
    exclude_channels: Mapped[str | None] = mapped_column(Text)   # CSV channel_id
    languages: Mapped[str | None] = mapped_column(String(64))    # CSV ISO639-1
    quiet_hours: Mapped[str | None] = mapped_column(String(32))  # "22-7"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session: Mapped["TGSession"] = relationship("TGSession", back_populates="user", uselist=False, cascade="all,delete")

class TGSession(Base):
    __tablename__ = "tg_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    session_encrypted: Mapped[str] = mapped_column(Text)
    user: Mapped[User] = relationship("User", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    channel_id: Mapped[int] = mapped_column(Integer, index=True)
    msg_id: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    text: Mapped[str] = mapped_column(Text)
    views: Mapped[int] = mapped_column(Integer, default=0)
    forwards: Mapped[int] = mapped_column(Integer, default=0)
    reactions: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    lang: Mapped[str | None] = mapped_column(String(8))
    score: Mapped[float] = mapped_column(Float, default=0.0)

class Digest(Base):
    __tablename__ = "digests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)

class DigestItem(Base):
    __tablename__ = "digest_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    digest_id: Mapped[int] = mapped_column(Integer, index=True)
    channel_id: Mapped[int] = mapped_column(Integer)
    msg_id: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(256))
    summary: Mapped[str] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float, index=True)
