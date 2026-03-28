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
    # استخدام تنسيق HTML بدلاً من Markdown لضمان عدم حدوث أخطاء في الرموز
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}
    requests.post(url, json=payload )

async def main():
    print("🚀 بدء استخراج أقوى 20 منتج ترند في السعودية...")
    
    # قائمة المنتجات (سيتم تحليلها بالذكاء الاصطناعي)
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
            
            report = f"""
📦 <b>منتج ترند ({i+1}/20)</b>
🔥 <b>المنتج:</b> {product}
📈 <b>الحالة:</b> {analysis.get('trend_status', 'بداية الترند')}
💰 <b>السعر المقترح:</b> {analysis.get('suggested_price', 'حسب السوق')}

🎯 <b>سكريبت سريع (تيك توك):</b>
{analysis.get('ad_script', 'وصف تسويقي جذاب')}

🔗 <a href="https://m5azn.com/product?search={product}">رابط المنتج في مخازن</a>
----------------------------
            """
            send_telegram(report )
            print(f"✅ تم إرسال المنتج {i+1}")
            await asyncio.sleep(2) # تأخير بسيط لتجنب حظر تيليجرام للرسائل السريعة
            
        except Exception as e:
            print(f"❌ خطأ في المنتج {product}: {e}")

    print("✅ اكتمل إرسال التقرير بنجاح!")

if __name__ == "__main__":
    asyncio.run(main())
