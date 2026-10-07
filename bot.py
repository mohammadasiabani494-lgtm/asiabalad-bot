import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# توکن‌ها (با حذف فاصله و اینتر اضافه)
TELEGRAM_BOT_TOKEN = (
    os.environ.get("TELEGRAM_BOT_TOKEN")
    or "8794625931:AAHyIYUIHhEHHIbqZkwUuSsL0k6YJGyAp4"
).strip()

GROQ_API_KEY = (
    os.environ.get("GROQ_API_KEY")
    or "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"
).strip()

# وب‌سرور برای زنده نگه‌داشتن سرویس روی Render
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Mahan AI is running smoothly!".encode("utf-8"))

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

# دستور استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام! 👋 من ماهان هستم، دستیار هوشمند شما.\n\n"
        "هر سوال یا کمکی خواستی، برام پیام بفرست تا جوابت رو بدم!"
    )
    await update.message.reply_text(welcome_text)

# پاسخگویی هوشمند با مدل Groq
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Mahan AI (ماهان), an intelligent, polite, and friendly assistant. "
                        "Always reply in fluent Persian unless asked otherwise."
                    )
                },
                {"role": "user", "content": user_text}
            ],
        )
        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        print(f"Groq API Error: {e}")
        await update.message.reply_text("متأسفانه مشکلی در ارتباط با سرور پیش آمد. لطفاً دوباره تلاش کنید.")

def main():
    # سرور وب در ترد جداگانه
    web_thread = threading.Thread(target=run_health_server, daemon=True)
    web_thread.start()

    # راه‌اندازی ربات
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Mahan AI is online and listening...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
                         
