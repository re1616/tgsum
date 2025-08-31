import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import zoneinfo
from .db import SessionLocal
from .models import User, Digest
from .telegram_ingest import ingest_user
from .ranking import rank_user_messages
from .digest import build_digest
from .delivery import deliver_telegram
import logging
log = logging.getLogger(__name__)

async def _run_for_user(user: User):
    async with SessionLocal() as db:
        await ingest_user(db, user.id, hours=24)
        await rank_user_messages(db, user.id)
        d, body = await build_digest(db, user.id, user.max_items, user.min_score)
        if d and body and user.bot_chat_id:
            ok = await deliver_telegram(user.bot_chat_id, body)
            if ok:
                from sqlalchemy import update
                await db.execute(update(Digest).where(Digest.id == d.id).values(delivered=True))
                await db.commit()

async def hourly_job():
    async with SessionLocal() as db:
        q = await db.execute(select(User))
        users = q.scalars().all()
    tasks = []
    for u in users:
        now_local = datetime.utcnow().replace(tzinfo=zoneinfo.ZoneInfo("UTC")).astimezone(zoneinfo.ZoneInfo(u.tz))
        if now_local.hour == u.digest_hour:
            tasks.append(asyncio.create_task(_run_for_user(u)))
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

def start_scheduler():
    sch = AsyncIOScheduler(timezone="UTC")
    sch.add_job(lambda: asyncio.create_task(hourly_job()), CronTrigger(minute=0))  # каждый час
    sch.start()
