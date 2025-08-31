from datetime import datetime, timezone
from math import log
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from .models import Message, User

def _norm(x: int) -> float:
    return log(1 + max(0, x), 10.0)

def _time_decay(dt: datetime, half_life_h: int = 24) -> float:
    age_h = max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0)
    return 0.5 ** (age_h / half_life_h)

def _topic_match(text: str, topics_csv: str | None) -> float:
    if not topics_csv: return 0.0
    topics = [t.strip().lower() for t in topics_csv.split(",") if t.strip()]
    tl = text.lower()
    return 0.2 if any(t in tl for t in topics) else 0.0

async def rank_user_messages(db: AsyncSession, user_id: int):
    uq = await db.execute(select(User).where(User.id == user_id))
    user = uq.scalar_one()
    q = await db.execute(select(Message).where(Message.user_id == user_id))
    msgs = q.scalars().all()
    for m in msgs:
        score = (
            0.35 * _norm(m.views) +
            0.30 * _norm(m.reactions) +
            0.20 * _norm(m.comments) +
            0.15 * _norm(m.forwards)
        )
        score *= _time_decay(m.date)
        score += _topic_match(m.text, user.topics)
        await db.execute(update(Message).where(Message.id == m.id).values(score=score))
    await db.commit()
