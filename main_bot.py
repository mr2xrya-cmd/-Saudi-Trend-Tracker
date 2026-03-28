import os, requests, time, asyncio
from datetime import datetime
import google.generativeai as genai
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# الإعدادات
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

genai.configure(api_key=GEMINI_KEY)
# جربنا نغير الموديل لنسخة أضمن
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def send_telegram_pdf(file_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': CHAT_ID, 'caption': caption[:1000]}
            r = requests.post(url, files=files, data=data)
            print(f"✅ رد تيليجرام: {r.status_code}")
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")

def create_pdf(text, filename):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    try:
        pdf.add_font('Amiri', '', 'Amiri-Regular.ttf')
        pdf.set_font('Amiri', '', 14)
    except:
        print("⚠️ ملف الخط ناقص! ارفع Amiri-Regular.ttf للمستودع")
        pdf.set_font('Arial', '', 12)
    
    for line in text.split('\n'):
        if not line.strip(): 
            pdf.ln(5)
            continue
        
        # تنظيف وتحويل النص العربي
        try:
            reshaped = reshape(line)
            bidi_line = get_display(reshaped)
            # استخدمنا عرض محدد (190) بدل (0) لتفادي مشكلة المساحة
            pdf.multi_cell(190, 10, bidi_line, align='R')
        except:
            continue # تخطي السطر لو فيه مشكلة

    pdf.output(filename)

async def main():
    print("🚀 جاري التحليل يا ياسر...")
    trends = ["مبخرة إلكترونية", "ساعة ذكية", "منظم مكياج"] # جرب بـ 3 أولاً للتأكد
    
    report = f"تقرير ترندات السعودية - {datetime.now().strftime('%Y-%m-%d')}\n"
    report += "="*30 + "\n\n"

    for product in trends:
        try:
            prompt = f"حلل منتج {product} للسوق السعودي: السعر، الربح، وفكرة إعلان."
            response = model.generate_content(prompt)
            report += f"📦 {product}\n{response.text}\n"
            report += "-"*20 + "\n\n"
            print(f"✅ خلصنا {product}")
            await asyncio.sleep(2) # راحة بسيطة للمحرّك
        except Exception as e:
            print(f"❌ خطأ في {product}: {e}")

    file_name = "Saudi_Trend.pdf"
    create_pdf(report, file_name)
    send_telegram_pdf(file_name, "✅ أبشر يا ياسر! هذا التقرير الجديد وصل.")

if __name__ == "__main__":
    asyncio.run(main())
