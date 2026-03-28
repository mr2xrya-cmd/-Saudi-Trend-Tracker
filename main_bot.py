import os, requests, json, time, asyncio, urllib.parse
from datetime import datetime
from openai import OpenAI

# تحميل الإعدادات من GitHub Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    # سنستخدم HTML ولكن بحذر شديد جداً مع الروابط المشفره
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": msg, 
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload)
        print(f"Status: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    print("🚀 بدء استخراج التقرير الاحترافي والمضمون...")
    
    trends = ["مبخرة إلكترونية", "ساعة ذكية الترا", "منظم مكياج", "مكواة بخار", "جهاز مساج"]

    for i, product in enumerate(trends):
        prompt = f"حلل منتج '{product}' للسوق السعودي: حالة الترند، السعر المقترح، الربح المتوقع، سكريبت تيك توك. أجب بصيغة JSON."
        
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            analysis = json.loads(response.choices[0].message.content)
            
            # السر هنا: تشفير الرابط العربي ليقبله تيليجرام 100%
            # نحول "مبخرة" إلى "%D9%85%D8%A8%D8%AE%D8%B1%D8%A9" ليفهمها المتصفح وتيليجرام
            encoded_query = urllib.parse.quote(product)
            makhazen_link = f"https://m5azn.com/product?search={encoded_query}"
            
            # بناء التقرير بكل التفاصيل وبأمان تام
            report = f"📦 <b>منتج ترند ({i+1}/20)</b>\n"
            report += f"🔥 <b>المنتج:</b> {product}\n"
            report += f"📈 <b>الحالة:</b> {analysis.get('trend_status', 'ترند صاعد')}\n"
            report += f"💰 <b>السعر المقترح:</b> {analysis.get('suggested_price', '150 ريال')}\n"
            report += f"💵 <b>الربح المتوقع:</b> {analysis.get('expected_profit', '50 ريال')}\n"
            report += f"🎬 <b>سكريبت:</b> {analysis.get('ad_script', 'وصف جذاب')[:100]}...\n\n"
            report += f"🔗 <a href='{makhazen_link}'>اضغط هنا لرابط مخازن</a>\n"
            report += "----------------------------"
            
            send_telegram(report)
            print(f"✅ تم إرسال {product}")
            await asyncio.sleep(5) # تأخير كافي للأمان
                
        except Exception as e:
            print(f"Error analyzing {product}: {e}")

    print("✅ اكتمل الإرسال بنجاح!")

if __name__ == "__main__":
    asyncio.run(main())
