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
    # إرسال نص خام بدون أي تنسيقات لضمان الوصول
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        r = requests.post(url, json=payload )
        print(f"Result: {r.status_code}")
    except:
        print("Error sending message")

async def main():
    print("🚀 بدء استخراج أقوى 20 منتج ترند...")
    
    trends = [
        "مبخرة إلكترونية ذكية", "ساعة ذكية الترا", "منظم مكياج دوار", 
        "مكواة بخار للسفر", "جهاز مساج الرقبة", "خلاط محمول رياضي",
        "إضاءة قيمنق RGB", "كاميرا مراقبة منزلية", "سماعات بلوتوث عازلة",
        "ماكينة حلاقة احترافية", "ميزان ذكي للجسم", "حقيبة ظهر ضد السرقة",
        "قلاية هوائية رقمية", "مطحنة قهوة يدوية", "حامل جوال للسيارة",
        "جهاز تنظيف البشرة", "مصباح مكتبي ذكي", "مجموعة أدوات العناية",
        "منقي هواء صغير", "وسادة طبية للرقبة"
    ]

    for i, product in enumerate(trends):
        prompt = f"حلل منتج '{product}' للسوق السعودي: حالة الترند، السعر المقترح، وصف تسويقي سريع، وسكريبت تيك توك. أجب بصيغة JSON."
        
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            analysis = json.loads(response.choices[0].message.content)
            
            # نص بسيط جداً بدون أي رموز خاصة
            report = f"""
📦 منتج ترند ({i+1}/20)
- المنتج: {product}
- الحالة: {analysis.get('trend_status', 'بداية الترند')}
- السعر المقترح: {analysis.get('suggested_price', 'حسب السوق')}

🎯 سكريبت تيك توك:
{analysis.get('ad_script', 'وصف جذاب')}

رابط مخازن: https://m5azn.com/product?search={product}
----------------------------
            """
            send_telegram(report )
            print(f"Sent product {i+1}")
            await asyncio.sleep(3) # تأخير كافي لتجنب الحظر
            
        except Exception as e:
            print(f"Error in {product}: {e}")

    print("✅ اكتمل الإرسال!")

if __name__ == "__main__":
    asyncio.run(main())
