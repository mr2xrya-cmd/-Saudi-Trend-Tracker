import os, requests, json, time, asyncio
from datetime import datetime
from openai import OpenAI

# تحميل الإعدادات من GitHub Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        r = requests.post(url, json=payload)
        print(f"Result: {r.status_code}")
    except:
        pass

async def main():
    print("🚀 بدء استخراج التحليلات الذكية...")
    
    trends = ["مبخرة إلكترونية", "ساعة ذكية الترا", "منظم مكياج", "مكواة بخار", "جهاز مساج"]

    for i, product in enumerate(trends):
        prompt = f"حلل منتج '{product}' للسوق السعودي: حالة الترند، السعر المقترح، وصف تسويقي سريع. أجب بصيغة JSON."
        
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            analysis = json.loads(response.choices[0].message.content)
            
            # نص نقي جداً بدون روابط أو رموز خاصة لضمان العبور
            report = f"📦 منتج رقم {i+1}\n"
            report += f"المنتج: {product}\n"
            report += f"الحالة: {analysis.get('trend_status', 'ترند صاعد')}\n"
            report += f"السعر المقترح: {analysis.get('suggested_price', '150 ريال')}\n"
            report += f"نصيحة: {analysis.get('ad_script', 'منتج مربح جداً')[:50]}"
            
            send_telegram(report)
            print(f"تم إرسال {product}")
            await asyncio.sleep(5) # تأخير طويل للأمان
                
        except Exception as e:
            print(f"Error: {e}")

    print("✅ اكتمل الإرسال!")

if __name__ == "__main__":
    asyncio.run(main())
