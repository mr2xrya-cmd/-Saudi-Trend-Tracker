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
    # استخدام HTML لجعل الروابط أنيقة (مثلاً: <a href='url'>نص</a> )
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": msg, 
        "parse_mode": "HTML",
        "disable_web_page_preview": True # لتقليل حجم الرسالة وضمان وصولها
    }
    try:
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            print(f"Error: {r.text}")
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

    current_batch_msg = ""
    for i, product in enumerate(trends):
        prompt = f"حلل منتج '{product}' للسوق السعودي: حالة الترند، السعر المقترح، وصف تسويقي سريع، وسكريبت تيك توك. أجب بصيغة JSON."
        
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            analysis = json.loads(response.choices[0].message.content)
            
            # بناء نص المنتج بتنسيق HTML أنيق وروابط مخفية
            makhazen_link = f"https://m5azn.com/product?search={product.replace(' ', '%20' )}"
            
            product_info = f"""
📦 <b>منتج ترند ({i+1}/20)</b>
🔥 <b>المنتج:</b> {product}
📈 <b>الحالة:</b> {analysis.get('trend_status', 'بداية الترند')}
💰 <b>السعر المقترح:</b> {analysis.get('suggested_price', 'حسب السوق')}
🎯 <b>سكريبت:</b> {analysis.get('ad_script', 'وصف جذاب')[:100]}...
🔗 <a href='{makhazen_link}'>اضغط هنا لرابط مخازن</a>
----------------------------"""
            
            current_batch_msg += product_info
            
            # إرسال رسالة كل 5 منتجات لضمان عدم الحظر وسهولة القراءة
            if (i + 1) % 5 == 0:
                send_telegram(f"🚀 <b>تقرير المنتجات الترند (الجزء { (i+1)//5 }/4)</b>\n" + current_batch_msg)
                current_batch_msg = "" # تصفير الرسالة للدفعة القادمة
                await asyncio.sleep(5) # تأخير كافي بين الدفعات
                
        except Exception as e:
            print(f"Error analyzing {product}: {e}")

    print("✅ اكتمل إرسال التقرير الكامل بنجاح!")

if __name__ == "__main__":
    asyncio.run(main())
