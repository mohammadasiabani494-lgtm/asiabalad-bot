import os
import time
import requests
import urllib.parse
from groq import Groq

# توکن بات روبیکا
RUBIKA_TOKEN = "CGCCBA0PMUFVZQEUMUMEYZLMGIXCMLOSXNMDYSDGPGIPBKTKEOKSSGLIZEXPTRHM"

# اتصال به هوش مصنوعی Groq
groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY", "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")
)

SYSTEM_PROMPT = """شما دستیار هوشمند آسیابلد (AsiaBalad) هستید.
سازنده شما محمدامین آسیابانی است. همیشه با افتخار سازنده خود را معرفی کنید."""

def send_message(chat_id, text):
    url = f"https://botapi.rubika.ir/v01/{RUBIKA_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending message: {e}")

def send_image(chat_id, image_url, caption=""):
    url = f"https://botapi.rubika.ir/v01/{RUBIKA_TOKEN}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": image_url, "caption": caption}
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Error sending photo: {e}")

def get_updates(offset=None):
    url = f"https://botapi.rubika.ir/v01/{RUBIKA_TOKEN}/getUpdates"
    payload = {"limit": 10}
    if offset:
        payload["offset"] = offset
    try:
        res = requests.post(url, json=payload, timeout=20)
        if res.status_code == 200:
            return res.json().get("data", [])
    except Exception as e:
        print(f"Polling error: {e}")
    return []

def process_message(chat_id, text):
    if not text:
        return

    # پیام خوش‌آمدگویی
    if text.strip() in ["/start", "شروع", "سلام"]:
        msg = (
            "سلام! من آسیابلد هستم 🤖\n"
            "ساخته شده توسط محمدامین آسیابانی.\n\n"
            "هر سوالی داری بپرس یا بنویس: «عکس یک عقاب برام بکش» تا برات طراحی کنم!"
        )
        send_message(chat_id, msg)
        return

    # طراحی عکس در صورت درخواست
    keywords = ["عکس", "تصویر", "طراحی", "نقاشی", "بکش"]
    if any(k in text for k in keywords) and ("یک" in text or "رو" in text or "کن" in text or "بکش" in text):
        send_message(chat_id, "🎨 آسیابلد در حال طراحی عکس شماست... لطفاً چند لحظه صبر کنید.")
        encoded_prompt = urllib.parse.quote(text)
        img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        send_image(chat_id, img_url, caption=f"🖼 تصویر ساخته شده برای: {text}\nسازنده: محمدامین آسیابانی")
        return

    # هوش مصنوعی متنی با Groq
    try:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
        )
        answer = completion.choices[0].message.content
        send_message(chat_id, answer)
    except Exception as e:
        send_message(chat_id, f"خطا: {e}")

def main():
    print("AsiaBalad Rubika is running...")
    last_update_id = None
    while True:
        updates = get_updates(offset=last_update_id)
        for update in updates:
            last_update_id = update.get("update_id", 0) + 1
            msg = update.get("message", {})
            chat_id = msg.get("chat_id")
            text = msg.get("text")
            if chat_id and text:
                process_message(chat_id, text)
        time.sleep(1)

if __name__ == "__main__":
    main()
