import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import init_db
from .telegram_auth import router as tg_router
from .preferences import router as prefs_router
from .scheduler import start_scheduler
from .logging_conf import setup_logging
from .web import router as web_router

setup_logging()
app = FastAPI(title="telegram-digest-mvp", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"https://{settings.api_host}"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(tg_router)
app.include_router(prefs_router)
app.include_router(web_router)

@app.get("/healthz")
async def healthz(): return {"ok": True}

@app.get("/readyz")
async def readyz(): return {"ok": True}

@app.on_event("startup")
async def on_startup():
    await init_db()
    start_scheduler()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.api_host, port=settings.api_port, workers=1)
