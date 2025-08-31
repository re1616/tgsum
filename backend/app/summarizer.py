import os, httpx

def summarize_fallback(text: str, max_chars: int = 400) -> str:
    t = " ".join(text.strip().split())
    return t[:max_chars] + ("…" if len(t) > max_chars else "")

async def summarize(text: str) -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return summarize_fallback(text)
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "Суммаризуй фактически и кратко, без выдумок."},
                        {"role": "user", "content": f"Сократи текст в 2-5 предложений:\n{text[:8000]}"},
                    ],
                    "max_tokens": 180,
                    "temperature": 0.2,
                },
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        pass
    return summarize_fallback(text)
