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
    # إرسال نص خام (Plain Text ) لضمان الوصول 100%
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": msg,
        "disable_web_page_preview": False # للسماح بظهور معاينة بسيطة للرابط
    }
    try:
        r = requests.post(url, json=payload)
        print(f"Result: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

async def main():
    print("🚀 بدء استخراج وتحليل الـ 20 منتج ترند...")
    
    trends = [
        "مبخرة إلكترونية", "ساعة ذكية الترا", "منظم مكياج", "مكواة بخار", "جهاز مساج",
        "خلاط محمول", "إضاءة قيمنق", "كاميرا مراقبة", "سماعات بلوتوث", "ماكينة حلاقة",
        "ميزان ذكي", "حقيبة ضد السرقة", "قلاية هوائية", "مطحنة قهوة", "حامل جوال",
        "تنظيف البشرة", "مصباح ذكي", "أدوات عناية", "منقي هواء", "وسادة طبية"
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
            
            # نص بسيط جداً بدون أي رموز HTML لضمان الوصول
            makhazen_link = f"https://m5azn.com/product?search={product.replace(' ', '%20' )}"
            
            report = f"""
📦 منتج ترند ({i+1}/20)
- المنتج: {product}
- الحالة: {analysis.get('trend_status', 'بداية الترند')}
- السعر المقترح: {analysis.get('suggested_price', 'حسب السوق')}

🎯 سكريبت تيك توك:
{analysis.get('ad_script', 'وصف جذاب')[:150]}...

🔗 رابط مخازن:
{makhazen_link}
----------------------------"""
            
            send_telegram(report)
            print(f"Sent product {i+1}")
            await asyncio.sleep(4) # تأخير كافي جداً لتجنب الحظر
                
        except Exception as e:
            print(f"Error analyzing {product}: {e}")

    print("✅ اكتمل إرسال التقرير الكامل بنجاح!")

if __name__ == "__main__":
    asyncio.run(main())
