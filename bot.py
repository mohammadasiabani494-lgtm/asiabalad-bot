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

# ----------------- سرور وب داخلی برای زنده ماندن در رندر -----------------
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Mahan AI Bot is alive and running!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_fake_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# ----------------- توکن‌ها و کلیدها -----------------
# دریافت توکن تلگرام از تنظیمات رندر یا مقدار پیش‌فرض مستقیم
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8963617563:AAHmo9GVuHoUjK1qU0TD0xn_1NBzB0zLFcI")

# دریافت کلید Groq از تنظیمات رندر یا مقدار پیش‌فرض مستقیم
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

groq_client = Groq(api_key=GROQ_API_KEY)

# پرامپت هویتی ماهان AI بدون تکرار بی‌مورد نام
SYSTEM_PROMPT = (
    "نام تو «ماهان» (Mahan AI) است؛ یک دستیار هوشمند، بسیار مودب، کاربلد و مسلط به زبان‌های فارسی و انگلیسی. "
    "سازنده و توسعه‌دهنده تو «محمدامین آسیابانی» است. "
    "قانون مهم: در مکالمات و پاسخ‌های روزمره به هیچ وجه نام سازنده را مدام تکرار نکن. "
    "تنها در صورتی که کاربر صریحاً پرسید سازنده یا برنامه‌نویس تو کیست، با احترام بگو که ساخته محمدامین آسیابانی هستی. "
    "در غیر این صورت، مستقیماً و با احترام به پرسش کاربر پاسخ بده."
)

# ----------------- هندلرهای تلگرام -----------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سلام! من ماهان (Mahan AI) هستم؛ دستیار هوشمند تو.\n"
        "هر سوالی داری بپرس یا برای طراحی تصویر بنویس:\n"
        "`/image متن تصویر مورد نظر`"
    )
    await update.message.reply_text(welcome_text)

async def generate_image(update: Update, prompt: str):
    await update.message.reply_text("در حال طراحی و ایجاد تصویر، لطفاً چند لحظه صبر کن...")
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
    
    try:
        await update.message.reply_photo(photo=image_url, caption=f"🎨 نتیجه طراحی برای: {prompt}")
    except Exception as e:
        await update.message.reply_text(f"خطا در ارسال تصویر: {e}")

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("لطفاً بعد از دستور /image توضیح عکس را بنویس.\nمثال: `/image یک ماشین اسپرت در شب`")
        return
    prompt = " ".join(context.args)
    await generate_image(update, prompt)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return

    # تشخیص درخواست طراحی عکس
    image_keywords = ["عکس", "تصویر", "بکش", "طراحی کن", "نقاشی"]
    if any(keyword in user_text for keyword in image_keywords) and len(user_text.split()) > 1:
        clean_prompt = user_text
        for kw in ["یک", "عکس", "تصویر", "از", "برام", "رو", "بکش", "طراحی کن", "لطفا"]:
            clean_prompt = clean_prompt.replace(kw, "")
        clean_prompt = clean_prompt.strip()
        if clean_prompt:
            await generate_image(update, clean_prompt)
            return

    # پاسخ متنی با مدل Groq
    try:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
        )
        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"خطا در پاسخگویی: {e}")

# ----------------- اجرای ربات -----------------
def main():
    threading.Thread(target=run_fake_server, daemon=True).start()

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("image", image_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Mahan AI is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
