import os
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# وب‌سرور داخلی برای روشن نگه داشتن ربات در رندر
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"AsiaBalad is Online!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

TELEGRAM_TOKEN = "8963617563:AAHmo9GVuHoUjK1qU0TDOxn_1NBzB0zLFcI"

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY", "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")
)

SYSTEM_PROMPT = """شما دستیار هوشمند آسیابلد (AsiaBalad) هستید.
سازنده شما محمدامین آسیابانی است. همیشه با افتخار سازنده خود را معرفی کنید."""

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! من آسیابلد هستم 🤖 ساخته شده توسط محمدامین آسیابانی.\n\n"
        "✨ هر سوالی داری بپرس، یا اگر می‌خوای عکس طراحی کنم، بگو «عکس یک ... برام بکش» یا بنویس:\n"
        "`/image متن تصویر`"
    )

# دستور ساخت مستقیم عکس با دستور /image
async def generate_image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("لطفاً توصیف عکسی که می‌خوای رو بنویس. مثلاً:\n/image یک ماشین مسابقه‌ای فضایی")
        return
    
    prompt = " ".join(context.args)
    await generate_and_send_photo(update, prompt)

# تابع تولید و ارسال عکس
async def generate_and_send_photo(update: Update, prompt_text: str):
    await update.message.reply_text("🎨 در حال طراحی عکس توسط آسیابلد... لطفاً چند لحظه صبر کنید.")
    try:
        encoded_prompt = urllib.parse.quote(prompt_text)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        await update.message.reply_photo(photo=image_url, caption=f"🖼 تصویر ساخته شده برای: {prompt_text}\n\nطراحی شده توسط دستیار آسیابلد (محمدامین آسیابانی)")
    except Exception as e:
        await update.message.reply_text(f"متاسفانه در تولید تصویر خطایی رخ داد: {e}")

# مدیریت پیام‌های متنی و تشخیص درخواست تصویر
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    lower_text = user_text.lower()

    # اگر کاربر درخواست تصویر کرد
    keywords = ["عکس", "تصویر", "نقاشی", "طراحی کن", "بکش", "طراحی عکس"]
    if any(k in user_text for k in keywords) and ("یک" in user_text or "رو" in user_text or "کن" in user_text or "بکش" in user_text or "طراحی" in user_text):
        await generate_and_send_photo(update, user_text)
        return

    # در غیر این صورت، پاسخ متنی هوشمند با Groq
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ]
        )
        await update.message.reply_text(completion.choices[0].message.content)
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        await update.message.reply_text(f"خطا: {e}")

def main():
    threading.Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("image", generate_image_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
        
