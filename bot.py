import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from groq import Groq
import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "GAPGPTMASKTOKENy831o6gthdkX0X")
GROQ_API_KEY = os.environ.get("GROQ_KEY", "GAPGPTMASKTOKENy831o6gthdkX1X")

client = Groq(api_key=GAPGPTMASKTOKENy831o6gthdkX2X
user_histories = {}

SYSTEM_PROMPT = "You are 'AsiaBalad' (آسیابلد), a helpful, polite and smart AI assistant. Fluent in Persian and English. Answer naturally in the same language the user writes in. If asked who you are, say you are AsiaBalad AI bot."

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من آسیابلد هستم 🤖\nهر سؤالی داری به فارسی یا انگلیسی بپرس!\n\nHello! I am AsiaBalad 🤖\nAsk me anything in Persian or English!")

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
        await update.message.reply_text("خطایی پیش آمد، دوباره امتحان کن / An error occurred, please try again.")

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
print("AsiaBalad is RUNNING...")
app.run_polling()
