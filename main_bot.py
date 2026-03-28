import os, requests, time, asyncio
from datetime import datetime
import google.generativeai as genai # رجعنا للمكتبة المستقرة
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# الأسرار
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# إعداد جميناي بطريقة تضمن الوصول للموديل المستقر
genai.configure(api_key=GEMINI_KEY)
# استخدمنا الاسم المختصر والأكثر استقراراً
model = genai.GenerativeModel('gemini-1.5-flash')

def send_telegram_pdf(file_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': CHAT_ID, 'caption': caption[:1000]}
            r = requests.post(url, files=files, data=data)
            print(f"✅ رد تيليجرام: {r.status_code}")
    except Exception as e:
        print(f"❌ خطأ إرسال: {e}")

def create_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.add_font('Amiri', '', 'Amiri-Regular.ttf')
        pdf.set_font('Amiri', '', 12)
    except:
        pdf.set_font('Arial', '', 10)
    
    for line in text.split('\n'):
        if not line.strip():
            pdf.ln(5)
            continue
        # تنظيف النص من الرموز اللي تخرب الـ PDF
        clean_line = line.replace('*', '').replace('#', '').replace('-', ' ')
        try:
            reshaped = reshape(clean_line)
            bidi_line = get_display(reshaped)
            pdf.multi_cell(180, 8, bidi_line, align='R')
        except:
            continue
    pdf.output(filename)

async def main():
    print("🚀 محاولة أخيرة وقوية يا ياسر...")
    trends = ["مبخرة إلكترونية", "ساعة ذكية", "كاميرا مراقبة"]
    
    report = f"تقرير ترندات السعودية - {datetime.now().strftime('%Y-%m-%d')}\n"
    report += "="*30 + "\n\n"

    for product in trends:
        try:
            print(f"🔍 تحليل: {product}...")
            # الطلب بصيغة المكتبة المستقرة
            response = model.generate_content(f"حلل منتج {product} للسوق السعودي: السعر، الربح، وفكرة إعلان.")
            
            if response.text:
                report += f"📦 {product}\n{response.text}\n"
                report += f"🔗 رابط: https://m5azn.com/product?search={product.replace(' ', '%20')}\n"
                report += "-"*20 + "\n\n"
                print(f"✅ تم تحليل {product}")
            
            await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ خطأ في {product}: {e}")

    print("\n--- التقرير النهائي ---")
    if len(report) > 100:
        file_name = "Saudi_Trend.pdf"
        create_pdf(report, file_name)
        send_telegram_pdf(file_name, "✅ أبشر يا ياسر! التقرير وصلك بالنسخة المستقرة.")
    else:
        print("❌ فشل في توليد التقرير، تأكد من الـ API Key.")

if __name__ == "__main__":
    asyncio.run(main())
