import os, requests

def send_simple_test():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    msg = "🚀 تجربة نظام الترندات: إذا وصلت هذه الرسالة فالاتصال سليم!"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": msg}
    
    print(f"جاري الإرسال إلى {chat_id}..." )
    r = requests.post(url, json=payload)
    print(f"النتيجة: {r.status_code} - {r.text}")

if __name__ == "__main__":
    send_simple_test()
