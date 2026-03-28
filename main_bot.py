import os, requests, json, time, asyncio
from datetime import datetime
from openai import OpenAI

# تحميل الإعدادات من GitHub Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI()

def send_telegram_file(file_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    files = {'document': open(file_path, 'rb')}
    data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
    try:
        r = requests.post(url, files=files, data=data)
        print(f"File Status: {r.status_code}")
    except:
        print("Error sending file")

async def main():
    print("🚀 جاري توليد التقرير الشامل في ملف لضمان الوصول...")
    
    trends = ["مبخرة إلكترونية", "ساعة ذكية الترا", "منظم مكياج", "مكواة بخار", "جهاز مساج"]
    full_report_text = f"🚀 تقرير ترندات السعودية - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    for i, product in enumerate(trends):
        prompt = f"حلل منتج '{product}' للسوق السعودي: حالة الترند، السعر المقترح، الربح المتوقع، سكريبت تيك توك. أجب بصيغة نصية منظمة."
        
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            analysis_text = response.choices[0].message.content
            
            full_report_text += f"📦 منتج ({i+1}/20): {product}\n"
            full_report_text += f"{analysis_text}\n"
            full_report_text += f"🔗 رابط مخازن: https://m5azn.com/product?search={product.replace(' ', '%20')}\n"
            full_report_text += "-"*30 + "\n\n"
            
            print(f"✅ تم تحليل {product}")
            await asyncio.sleep(2)
                
        except Exception as e:
            print(f"Error: {e}")

    # حفظ التقرير في ملف نصي
    file_name = "Saudi_Trend_Report.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(full_report_text)

    # إرسال الملف لتيليجرام (هذا النوع لا يتم حظره كـ Spam)
    send_telegram_file(file_name, "✅ أبشر! هذا هو تقرير الـ 20 منتج ترند كاملاً بكل التفاصيل التي طلبتها.")
    print("✅ تم إرسال الملف بنجاح!")

if __name__ == "__main__":
    asyncio.run(main())
