from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from .db import SessionLocal
from .models import User, Digest, DigestItem

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

async def get_db():
    async with SessionLocal() as s:
        yield s

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, user_id: int | None = None, db: AsyncSession = Depends(get_db)):
    u = None
    if user_id:
        q = await db.execute(select(User).where(User.id == user_id))
        u = q.scalar_one_or_none()
    dq = await db.execute(select(Digest).order_by(desc(Digest.date)).limit(1))
    d = dq.scalar_one_or_none()
    items = []
    if d:
        iq = await db.execute(select(DigestItem).where(DigestItem.digest_id == d.id).order_by(desc(DigestItem.score)))
        items = iq.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "user": u, "digest": d, "items": items})

@router.get("/settings", response_class=HTMLResponse)
async def settings_get(request: Request, user_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(User).where(User.id == user_id))
    u = q.scalar_one()
    return templates.TemplateResponse("settings.html", {"request": request, "u": u})

@router.post("/settings")
async def settings_post(request: Request, user_id: int = Form(...), tz: str = Form(...), digest_hour: int = Form(...),
                        max_items: int = Form(...), min_score: float = Form(...),
                        topics: str = Form(""), exclude_channels: str = Form(""),
                        languages: str = Form(""), quiet_hours: str = Form(""),
                        db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(User).where(User.id == user_id))
    u = q.scalar_one()
    u.tz, u.digest_hour, u.max_items, u.min_score = tz, digest_hour, max_items, min_score
    u.topics, u.exclude_channels, u.languages, u.quiet_hours = topics, exclude_channels, languages, quiet_hours
    await db.commit()
    return RedirectResponse(url=f"/settings?user_id={user_id}", status_code=302)
