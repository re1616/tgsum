from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import PeerChannel
from .models import User, TGSession, Message
from .security import decrypt_str

async def ingest_user(db: AsyncSession, user_id: int, hours: int = 24):
    q = await db.execute(select(TGSession).where(TGSession.user_id == user_id))
    tgs = q.scalar_one_or_none()
    if not tgs: return 0
    session = StringSession(decrypt_str(tgs.session_encrypted))
    client = TelegramClient(session, api_id=None, api_hash=None)
    await client.connect()
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    count = 0
    try:
        async for d in client.iter_dialogs():
            if not getattr(d.entity, "broadcast", False):
                continue
            channel = d.entity
            async for m in client.iter_messages(PeerChannel(channel.id), limit=200):
                mdt = m.date.replace(tzinfo=timezone.utc)
                if mdt < since: break
                text = m.message or ""
                views = getattr(m, "views", 0) or 0
                forwards = getattr(m, "forwards", 0) or 0
                rx = 0
                if getattr(m, "reactions", None) and getattr(m.reactions, "results", None):
                    rx = sum((getattr(r, "count", 0) or 0) for r in m.reactions.results)
                comments = 0
                if getattr(m, "replies", None) and getattr(m.replies, "replies", None):
                    comments = m.replies.replies or 0
                db.add(Message(
                    user_id=user_id, channel_id=channel.id, msg_id=m.id,
                    date=mdt, text=text, views=views, forwards=forwards, reactions=rx,
                    comments=comments, lang=None
                ))
                count += 1
        await db.commit()
    finally:
        await client.disconnect()
    await db.execute(delete(Message).where(Message.user_id == user_id, Message.date < since - timedelta(days=2)))
    await db.commit()
    return count
