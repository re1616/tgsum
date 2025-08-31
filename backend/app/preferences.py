from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .db import SessionLocal
from .models import User

router = APIRouter(prefix="/prefs", tags=["prefs"])

async def get_db():
    async with SessionLocal() as s:
        yield s

@router.post("/set")
async def set_prefs(user_id: int, tz: str | None = None, digest_hour: int | None = None,
                    max_items: int | None = None, min_score: float | None = None,
                    topics: str | None = None, exclude_channels: str | None = None,
                    languages: str | None = None, quiet_hours: str | None = None,
                    db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(User).where(User.id == user_id))
    u = q.scalar_one()
    if tz is not None: u.tz = tz
    if digest_hour is not None: u.digest_hour = digest_hour
    if max_items is not None: u.max_items = max_items
    if min_score is not None: u.min_score = min_score
    if topics is not None: u.topics = topics
    if exclude_channels is not None: u.exclude_channels = exclude_channels
    if languages is not None: u.languages = languages
    if quiet_hours is not None: u.quiet_hours = quiet_hours
    await db.commit()
    return {"ok": True}
