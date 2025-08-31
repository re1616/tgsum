from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from jinja2 import Template
from .models import Message, Digest, DigestItem, User
from .summarizer import summarize

DIGEST_TMPL = Template(
"""Дайджест за {{date}}:
{% for it in items -%}
— {{it.title}} (score={{'%.2f'%it.score}})
{{it.summary}}
Источник: https://t.me/c/{{it.channel_id}}/{{it.msg_id}}
{% endfor -%}
""")

async def build_digest(db: AsyncSession, user_id: int, max_items: int, min_score: float):
    uq = await db.execute(select(User).where(User.id == user_id))
    user = uq.scalar_one()
    now = datetime.now(timezone.utc)
    day_key = now.date().isoformat()

    # не дублировать дайджест в сутки
    dq = await db.execute(select(Digest).where(and_(Digest.user_id == user_id)))
    existing = dq.scalars().all()
    if any(d.date.date().isoformat() == day_key for d in existing):
        return None, None

    since = now - timedelta(hours=24)
    q2 = await db.execute(
        select(Message).where(
            Message.user_id == user_id,
            Message.date >= since,
            Message.score >= min_score
        ).order_by(Message.score.desc())
    )
    msgs = q2.scalars().all()

    # исключения каналов
    if user.exclude_channels:
        excl = set(int(x.strip()) for x in user.exclude_channels.split(",") if x.strip().isdigit())
        msgs = [m for m in msgs if m.channel_id not in excl]

    items = []
    for m in msgs[:max_items]:
        title = (m.text.strip().split("\n", 1)[0] or "Пост").strip()[:80]
        summary = await summarize(m.text if len(m.text) > 400 else title)
        items.append({
            "channel_id": m.channel_id,
            "msg_id": m.msg_id,
            "title": title,
            "summary": summary,
            "score": m.score
        })
    if not items:
        return None, None

    body = DIGEST_TMPL.render(date=now.date().isoformat(), items=items)
    d = Digest(user_id=user_id, date=now, delivered=False)
    from sqlalchemy import insert
    # фиксируем дайджест и пункты
    from .db import SessionLocal
    db.add(d); await db.flush()
    for it in items:
        db.add(DigestItem(
            digest_id=d.id, channel_id=it["channel_id"], msg_id=it["msg_id"],
            title=it["title"], summary=it["summary"], score=it["score"]
        ))
    await db.commit()
    return d, body
