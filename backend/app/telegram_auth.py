import secrets, string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from telethon import TelegramClient
from telethon.sessions import StringSession
from .db import SessionLocal
from .config import settings
from .models import User, TGSession
from .security import encrypt_str, decrypt_str
from .auth import require_api_token

router = APIRouter(prefix="/tg", tags=["telegram"])

async def get_db():
    async with SessionLocal() as s:
        yield s

def _code(n=8):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))

@router.post("/login/start")
async def login_start(phone: str, db: AsyncSession = Depends(get_db)):
    client = TelegramClient(StringSession(), settings.telegram_api_id, settings.telegram_api_hash)
    await client.connect()
    try:
        sent = await client.send_code_request(phone)
    finally:
        await client.disconnect()
    q = await db.execute(select(User).where(User.phone == phone))
    user = q.scalar_one_or_none()
    if not user:
        user = User(phone=phone, link_code=_code())
        db.add(user); await db.flush()
    await db.commit()
    return {"phone": phone, "phone_code_hash": sent.phone_code_hash, "link_code": user.link_code, "user_id": user.id}

@router.post("/login/confirm")
async def login_confirm(phone: str, code: str, phone_code_hash: str, password: str | None = None, db: AsyncSession = Depends(get_db)):
    client = TelegramClient(StringSession(), settings.telegram_api_id, settings.telegram_api_hash)
    await client.connect()
    try:
        if password:
            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash, password=password)
        else:
            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        session_str = client.session.save()
    except Exception as e:
        raise HTTPException(400, f"auth_failed: {e}")
    finally:
        await client.disconnect()

    q = await db.execute(select(User).where(User.phone == phone))
    user = q.scalar_one()
    q2 = await db.execute(select(TGSession).where(TGSession.user_id == user.id))
    tgs = q2.scalar_one_or_none()
    enc = encrypt_str(session_str)
    if tgs:
        tgs.session_encrypted = enc
    else:
        db.add(TGSession(user_id=user.id, session_encrypted=enc))
    if not user.link_code:
        user.link_code = _code()
    await db.commit()
    return {"ok": True, "user_id": user.id, "link_code": user.link_code}

@router.post("/chat-link-by-code", dependencies=[Depends(require_api_token)])
async def chat_link_by_code(code: str, chat_id: str, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(User).where(User.link_code == code))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "code_not_found")
    user.bot_chat_id = chat_id
    user.link_code = None
    await db.commit()
    return {"ok": True, "user_id": user.id, "chat_id": chat_id}
