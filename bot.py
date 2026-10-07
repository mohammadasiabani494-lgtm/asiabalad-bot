import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# سرور وب برای روشن ماندن در رندر
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من آسیابلد هستم 🤖 ساخته شده توسط محمدامین آسیابانی. هر سوالی داری بپرس!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": update.message.text}
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
