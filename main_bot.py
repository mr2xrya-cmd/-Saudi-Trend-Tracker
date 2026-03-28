import os, requests, time, asyncio
from datetime import datetime
from google import genai # المكتبة الجديدة
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# الأسرار من GitHub
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# إعداد العميل بالنسخة الجديدة
client = genai.Client(api_key=GEMINI_KEY)

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
        clean_line = line.replace('*', '').replace('#', '')
        try:
            reshaped = reshape(clean_line)
            bidi_line = get_display(reshaped)
            pdf.multi_cell(180, 8, bidi_line, align='R')
        except:
            continue
    pdf.output(filename)

async def main():
    print("🚀 انطلقنا بالتحديث الجديد يا ياسر...")
    trends = ["مبخرة إلكترونية", "ساعة ذكية", "كاميرا مراقبة"]
    
    report = f"تقرير ترندات السعودية - {datetime.now().strftime('%Y-%m-%d')}\n"
    report += "="*30 + "\n\n"

    for product in trends:
        try:
            print(f"🔍 تحليل: {product}...")
            # الطريقة الجديدة لطلب المحتوى
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=f"حلل منتج {product} للسوق السعودي باختصار: السعر، الربح، وفكرة إعلان."
            )
            
            if response.text:
                report += f"📦 {product}\n{response.text}\n"
                report += "-"*20 + "\n\n"
                print(f"✅ تم تحليل {product}")
            
            await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ خطأ في {product}: {e}")

    print("\n--- التقرير جاهز للإرسال ---")
    if len(report) > 100:
        file_name = "Saudi_Trend.pdf"
        create_pdf(report, file_name)
        send_telegram_pdf(file_name, "✅ التقرير وصلك بالتحديث الجديد!")
    else:
        print("❌ فشل توليد محتوى التقرير.")

if __name__ == "__main__":
    asyncio.run(main())
