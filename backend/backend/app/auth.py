from fastapi import Header, HTTPException

def require_api_token(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "unauthorized")
    from .config import settings
    token = authorization.split(" ", 1)[1]
    if token != settings.api_token:
        raise HTTPException(403, "forbidden")
