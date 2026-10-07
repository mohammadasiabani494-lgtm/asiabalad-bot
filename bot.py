import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# توکن جدید تلگرام
TELEGRAM_BOT_TOKEN = "8794625931:AAE5qSsEuJqiZBj5rfVwrCqhqhxEy8t2Z1Zg"

# کلید هوش مصنوعی گروک
GROQ_API_KEY = "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"

# سرور داخلی برای فعال نگه داشتن سرویس در Render
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Mahan AI is Live!".encode("utf-8"))

    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

# پیام شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام! 👋 من ماهان هستم، دستیار هوشمند شما.\n\n"
        "هر سوال یا درخواستی داری برام بفرست تا کمکت کنم!"
    )
    if update.message:
        await update.message.reply_text(welcome_text)

# پردازش و پاسخ هوشمند به پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": "You are Mahan AI (ماهان), a friendly and intelligent Persian AI assistant. Always reply politely, naturally and fluently in Persian."
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ]
        )
        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        print(f"Groq API Error: {e}")
        await update.message.reply_text("متأسفانه در حال حاضر خطایی رخ داده است. لطفاً کمی بعد دوباره پیام دهید.")

def main():
    # فعال‌سازی سرور در پس‌زمینه برای Render
    web_thread = threading.Thread(target=run_health_server, daemon=True)
    web_thread.start()

    print("Starting Mahan AI...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Mahan AI is online and listening...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
