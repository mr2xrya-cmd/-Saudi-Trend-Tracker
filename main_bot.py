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
    # نرسل نصاً عادياً (Plain Text) لضمان الوصول 100% وتجنب أخطاء التنسيق
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": msg,
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload)
        print(f"Status: {r.status_code}")
    except:
        pass

async def main():
    print("🚀 بدء استخراج التقرير الشامل والمضمون...")
    
    trends = [
        "مبخرة إلكترونية", "ساعة ذكية الترا", "منظم مكياج", "مكواة بخار", "جهاز مساج",
        "خلاط محمول", "إضاءة قيمنق", "كاميرا مراقبة", "سماعات بلوتوث", "ماكينة حلاقة",
        "ميزان ذكي", "حقيبة ضد السرقة", "قلاية هوائية", "مطحنة قهوة", "حامل جوال",
        "تنظيف البشرة", "مصباح ذكي", "أدوات عناية", "منقي هواء", "وسادة طبية"
    ]

    for i, product in enumerate(trends):
        prompt = f"حلل منتج '{product}' للسوق السعودي: حالة الترند، السعر المقترح، الربح المتوقع، سكريبت تيك توك. أجب بصيغة JSON."
        
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            analysis = json.loads(response.choices[0].message.content)
            
            # رابط مباشر وبسيط بدون تشفير معقد لضمان عدم انكساره
            makhazen_link = f"https://m5azn.com/product?search={product.replace(' ', '+')}"
            
            # بناء التقرير الشامل بنص نقي (Plain Text) مضمون الوصول
            report = f"📦 منتج ترند ({i+1}/20)\n"
            report += f"🔥 المنتج: {product}\n"
            report += f"📈 الحالة: {analysis.get('trend_status', 'ترند صاعد')}\n"
            report += f"💰 السعر المقترح: {analysis.get('suggested_price', '150 ريال')}\n"
            report += f"💵 الربح المتوقع: {analysis.get('expected_profit', '50 ريال')}\n"
            report += f"🎬 سكريبت تيك توك:\n{analysis.get('ad_script', 'وصف جذاب')[:100]}...\n\n"
            report += f"🔗 رابط مخازن:\n{makhazen_link}\n"
            report += "----------------------------"
            
            send_telegram(report)
            print(f"✅ تم إرسال {product}")
            # تأخير طويل (15 ثانية) لضمان عدم الحظر ووصول الـ 20 منتجاً تباعاً
            await asyncio.sleep(15) 
                
        except Exception as e:
            print(f"Error analyzing {product}: {e}")

    print("✅ اكتمل الإرسال بنجاح!")

if __name__ == "__main__":
    asyncio.run(main())
