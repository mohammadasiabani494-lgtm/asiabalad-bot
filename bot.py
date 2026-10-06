import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from groq import Groq
import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "GAPGPTMASKTOKENivz4n4jzsu8X0X")
GROQ_API_KEY = os.environ.get("GROQ_KEY", "GAPGPTMASKTOKENivz4n4jzsu8X1X")

client = Groq(api_key=GROQ_API_KEY)
user_histories = {}

# دستورالعمل هوش مصنوعی و معرفی سازنده
SYSTEM_PROMPT = """
You are 'AsiaBalad' (آسیابلد), a polite, highly intelligent, and helpful AI assistant.
You are fluent in both Persian and English. Always reply in the same language the user speaks.

CRITICAL INSTRUCTION ABOUT CREATOR:
Your creator, developer, and owner is 'محمدامین آسیابانی' (Mohammad Amin Asiabani). 
If anyone asks who created you, who your developer/boss/programmer/owner is (e.g. "سازندت کیه؟", "کی تو رو ساخته؟", "who made you?"):
You MUST proudly state that you were created and developed by 'محمدامین آسیابانی' (Mohammad Amin Asiabani).
"""

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! من آسیابلد (AsiaBalad) هستم 🤖\n"
        "ساخته‌شده توسط محمدامین آسیابانی 👑\n\n"
        "هر سؤالی داری به فارسی یا انگلیسی بپرس تا جوابت رو بدم!\n\n"
        "Hello! I am AsiaBalad 🤖\n"
        "Created by Mohammad Amin Asiabani 👑\n"
        "Feel free to ask me anything in Persian or English!"
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
