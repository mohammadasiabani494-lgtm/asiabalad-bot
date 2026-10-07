import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from groq import Groq
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ----------------- سرور وب برای پایداری در رندر -----------------
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Mahan AI is running smoothly!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# ----------------- تنظیمات و توکن‌ها -----------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8963617563:AAHDzjD9k3JXDMF8VDydVeINqxHt7YY9t2g")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = (
    "نام شما 'ماهان' (Mahan AI) است. شما یک هوش مصنوعی بسیار باهوش، مودب، "
    "خوش‌برخورد و سریع هستید که به زبان‌های فارسی و انگلیسی مسلطید. "
    "شما توسط 'محمدامین آسیابانی' طراحی و توسعه یافته‌اید. "
    "توجه بسیار مهم: تنها و تنها در صورتی که کاربر به صورت مستقیم از سازنده شما سوال پرسید "
    "(مثلاً چه کسی تو را ساخته؟)، نام سازنده را بگویید؛ در غیر این صورت به عنوان یک هوش مصنوعی مستقل "
    "و با نام ماهان به سوالات پاسخ دهید و در مکالمات عادی نیازی به تکرار نام سازنده نیست."
)

# ----------------- هندلرها -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام! 👋 من **ماهان (Mahan AI)** هستم، دستیار هوشمند شما.\n\n"
        "هر سوالی داری بپرس، یا اگر عکسی می‌خوای کافیه توی پیامت کلمه «عکس» رو بیاری!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return

    # تولید عکس
    if "عکس" in user_text:
        await update.message.reply_text("🎨 در حال طراحی و ساخت عکس برای شما... لطفاً چند لحظه صبر کنید.")
        prompt = urllib.parse.quote(user_text)
        image_url = f"https://pollinations.ai/p/{prompt}?width=1024&height=1024&seed=42&model=flux"
        try:
            await update.message.reply_photo(photo=image_url, caption="بفرما! عکس شما آماده شد ✨")
        except Exception:
            await update.message.reply_text("متاسفانه در دریافت عکس مشکلی پیش اومد، لطفاً دوباره امتحان کن.")
        return

    # هوش مصنوعی متنی
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
        )
        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("متاسفانه مشکلی در ارتباط با سرور هوش مصنوعی رخ داد. لطفاً چند لحظه بعد پیام بدید.")

# ----------------- اجرای ربات -----------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # drop_pending_updates باعث رفع تداخل Conflict و پیام‌های گیرکرده میشه
    app.run_polling(drop_pending_updates=True)
                
