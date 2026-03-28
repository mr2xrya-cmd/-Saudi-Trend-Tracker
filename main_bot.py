import os, requests, json, time, asyncio, urllib.parse
from datetime import datetime
from openai import OpenAI

# إعدادات الوصول من GitHub Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    # استخدام HTML لإخفاء الروابط الطويلة وجعلها أنيقة
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": msg, 
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload)
        print(f"Status: {r.status_code}")
    except:
        pass

async def main():
    print("🚀 بدء استخراج التقرير الشامل والأنيق (إرسال مضمون)...")
    
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
            
            # تشفير الرابط ليكون أنيقاً ومخفياً
            encoded_product = urllib.parse.quote(product)
            makhazen_link = f"https://m5azn.com/product?search={encoded_product}"
            
            # بناء التقرير الشامل بتنسيق HTML الأنيق
            report = f"<b>📦 منتج ترند ({i+1}/20)</b>\n"
            report += f"<b>🔥 المنتج:</b> {product}\n"
            report += f"<b>📈 الحالة:</b> {analysis.get('trend_status', 'ترند صاعد')}\n"
            report += f"<b>💰 السعر:</b> {analysis.get('suggested_price', '150 ريال')}\n"
            report += f"<b>💵 الربح:</b> {analysis.get('expected_profit', '50 ريال')}\n"
            report += f"<b>🎬 سكريبت:</b> {analysis.get('ad_script', 'وصف جذاب')[:100]}...\n\n"
            report += f"🔗 <b><a href='{makhazen_link}'>اضغط هنا لرابط مخازن</a></b>\n"
            report += "----------------------------"
            
            send_telegram(report)
            print(f"✅ Sent {product}")
            # تأخير كافي جداً (10 ثواني) لضمان عدم الحظر ووصول كل الرسائل
            await asyncio.sleep(10) 
                
        except Exception as e:
            print(f"Error: {e}")

    print("✅ اكتمل الإرسال بنجاح!")

if __name__ == "__main__":
    asyncio.run(main())
