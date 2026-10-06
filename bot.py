import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from groq import Groq

# وب‌سرور سبک برای راضی نگه داشتن سرور Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"AsiaBalad is alive and running!")

def run_fake_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

# کلیدها و توکن‌ها
TELEGRAM_BOT_TOKEN = "8963617563:AAHmo9GVuHoUjK1qU0TDOxn_1NBzB0zLFcI"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)
user_histories = {}

SYSTEM_PROMPT = """
You are 'AsiaBalad' (آسیابلد), a polite, highly intelligent, friendly, and knowledgeable AI assistant.
You are fluent in both Persian and English. Always reply in the same language the user speaks to you.

CRITICAL INSTRUCTION ABOUT CREATOR:
Your creator, developer, programmer, and owner is 'محمدامین آسیابانی' (Mohammad Amin Asiabani). 
If anyone asks who created you, who made you, who is your developer, boss, or owner (in Persian: "سازندت کیه؟", "کی تو رو ساخته؟", "برنامه‌نویس تو کیه؟" or in English: "who created you?", "who is your developer?"):
You MUST proudly state that you were created and developed by 'محمدامین آسیابانی' (Mohammad Amin Asiabani).
"""

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! من آسیابلد (AsiaBalad) هستم 🤖\n"
        "طراحی و ساخته‌شده توسط محمدامین آسیابانی 👑\n\n"
        "هر سؤالی داری به فارسی یا انگلیسی ازم بپرس تا سریع جوابت رو بدم!\n\n"
        "Hello! I am AsiaBalad 🤖\n"
        "Created by Mohammad Amin Asiabani 👑\n"
        "Ask me anything in Persian or English!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text
    if not user_text:
        return
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    if chat_id not in user_histories:
        user_histories[chat_id] = []
    user_histories[chat_id].append({"role": "user", "content": user_text})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_histories[chat_id][-6:]

    try:
        answer = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
        ).choices[0].message.content
        user_histories[chat_id].append({"role": "assistant", "content": answer})
        await update.message.reply_text(answer)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("خطایی رخ داد، لطفاً دوباره پیام بدید.")

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

print("AsiaBalad is RUNNING...")
app.run_polling()
