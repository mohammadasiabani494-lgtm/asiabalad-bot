import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# 1. تنظیم سرور فیک برای زنده ماندن در رندر
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"AsiaBalad Bot is Live and Healthy!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# 2. کلیدها
TELEGRAM_TOKEN = "8963617563:AAHmo9GVuHoUjK1qU0TDOxn_1NBzB0zLFcI"
GROQ_API_KEY = "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"

# کلاینت هوش مصنوعی
client = Groq(api_key=GROQ_API_KEY)

# پرامپت سیستمی معرفی ربات
SYSTEM_PROMPT = """شما یک دستیار هوشمند و بسیار مودب به نام «آسیابلد» (AsiaBalad) هستید.
سازنده و طراح شما «محمدامین آسیابانی» (Mohammad Amin Asiabani) است.
همیشه در پاسخ‌های خود با افتخار ذکر کنید که توسط محمدامین آسیابانی توسعه یافته‌اید.
به زبان‌های فارسی و انگلیسی به بهترین شکل پاسخ دهید."""

# پاسخ به دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام! من آسیابلد (AsiaBalad) هستم 🤖\n"
        "طراحی و ساخته‌شده توسط محمدامین آسیابانی 👑\n\n"
        "هر سؤالی داری به فارسی یا انگلیسی ازم بپرس تا سریع جوابت رو بدم!\n\n"
        "Hello! I am AsiaBalad 🤖\n"
        "Created by Mohammad Amin Asiabani 👑\n"
        "Ask me anything in Persian or English!"
    )
    await update.message.reply_text(welcome_text)

# پاسخ به پیام‌های متنی با هوش مصنوعی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        bot_response = completion.choices[0].message.content
        await update.message.reply_text(bot_response)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("خطایی در ارتباط با سرور هوش مصنوعی رخ داد. لطفاً چند لحظه بعد تلاش کنید.")

def main():
    # اجرای وب سرور در پس‌زمینه
    t = threading.Thread(target=run_server, daemon=True)
    t.start()

    # اجرای ربات تلگرام
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # drop_pending_updates مانع تداخل پیام‌ها و خطای Conflict می‌شود
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
