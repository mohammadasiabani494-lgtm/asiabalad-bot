import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# خواندن متغیرها و حذف فاصله‌ها و اینترهای اضافه
TELEGRAM_BOT_TOKEN = (os.environ.get("TELEGRAM_BOT_TOKEN") or "8794625931:AAHyIYUIHhEHHIbqZkwUuSsL0k6YJGyAp4
").strip()
GROQ_API_KEY = (os.environ.get("GROQ_API_KEY") or "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").strip()

# راه‌اندازی کلاینت هوش مصنوعی
client = Groq(api_key=GROQ_API_KEY)

# وب‌سرور برای زنده نگه داشتن سرویس روی Render
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Mahan AI is running smoothly!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

# دستور استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "سلام! 👋 من ماهان هستم، دستیار هوشمند شما.\n\n"
        "هر سوالی داری بپرس تا جواب بدم."
    )
    await update.message.reply_text(welcome_msg)

# پاسخگویی با هوش مصنوعی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are Mahan AI (ماهان), a helpful, polite, and intelligent AI assistant. Always reply in Persian unless the user speaks another language."
                },
                {"role": "user", "content": user_text}
            ],
        )
        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("متاسفانه در پردازش پیام مشکلی پیش آمد. لطفا دوباره تلاش کنید.")

def main():
    # اجرای وب‌سرور در پس‌زمینه
    t = threading.Thread(target=run_health_server, daemon=True)
    t.start()

    # ساخت و اجرای ربات تلگرام
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Mahan AI is starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
        
