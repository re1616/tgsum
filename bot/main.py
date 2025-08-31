import os, asyncio, httpx
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

API = os.getenv("BACKEND_URL", "http://api:8000")
API_TOKEN = os.getenv("API_TOKEN")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправьте код привязки в формате: /link ABCD1234")

async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Код отсутствует. Пример: /link ABCD1234")
        return
    code = context.args[0].strip().upper()
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(f"{API}/tg/chat-link-by-code", params={"code": code, "chat_id": str(update.effective_chat.id)},
                         headers={"Authorization": f"Bearer {API_TOKEN}"})
        if r.status_code == 200:
            await update.message.reply_text("Чат привязан. Дайджест будет доставляться ежедневно.")
        else:
            await update.message.reply_text(f"Ошибка привязки: {r.text}")

async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Настройки выполняются в веб-интерфейсе: https://"+os.getenv("DOMAIN","")+"?user_id=<ID>")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("link", link))
    app.add_handler(CommandHandler("settings", settings_cmd))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
