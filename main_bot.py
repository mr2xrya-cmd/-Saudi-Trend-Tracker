import os, requests, json, time, asyncio
from datetime import datetime
from openai import OpenAI
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# الإعدادات من GitHub Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI(api_key=GEMINI_API_KEY)

def send_telegram_file(file_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    if len(caption) > 1000: caption = caption[:950] + "..."
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            r = requests.post(url, files=files, data=data)
            res = r.json()
            if r.status_code == 200 and res.get("ok"):
                print("✅ تم إرسال الـ PDF بنجاح!")
            else:
                print(f"❌ فشل: {res.get('description')}")
    except Exception as e:
        print(f"Error: {e}")

def generate_pdf(report_content, filename):
    pdf = FPDF()
    pdf.add_page()
    
    # ملاحظة: التيليجرام والـ PDF يحتاجون خط يدعم العربي
    # إذا ما عندك ملف خط، النص بيطلع رموز. تأكد ترفع ملف خط (مثلاً Amiri-Regular.ttf) لمستودعك
    try:
        pdf.add_font('ArabicFont', '', 'Amiri-Regular.ttf')
        pdf.set_font('ArabicFont', '', 14)
    except:
        pdf.set_font('Arial', '', 12) # كحل احتياطي

    for line in report_content.split('\n'):
        # معالجة النص العربي ليظهر بشكل صحيح
        reshaped_text = reshape(line)
        bidi_text = get_display(reshaped_text)
        pdf.multi_cell(0, 10, bidi_text, align='R')
    
    pdf.output(filename)

async def main():
    print("🚀 جاري تجهيز تقرير الـ PDF الاحترافي...")
    trends = ["مبخرة إلكترونية", "ساعة ذكية الترا", "منظم مكياج", "مكواة بخار", "جهاز مساج"] # جرب بـ 5 أولاً
    
    report_text = f"تقرير ترندات السعودية - {datetime.now().strftime('%Y-%m-%d')}\n"
    report_text += "="*30 + "\n\n"

    for i, product in enumerate(trends):
        prompt = f"Analyze product '{product}' for Saudi market. Short detail."
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            analysis = response.choices[0].message.content
            report_text += f"📦 {product}\n{analysis}\n\n"
            print(f"✅ تم تحليل {product}")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error: {e}")

    file_name = "Saudi_Trend_Report.pdf"
    generate_pdf(report_text, file_name)
    send_telegram_file(file_name, "✅ أبشر يا ياسر، هذا تقرير الـ PDF جاهز!")

if __name__ == "__main__":
    asyncio.run(main())
