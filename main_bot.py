import os, requests, time, asyncio
from datetime import datetime
import google.generativeai as genai
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# تحميل الإعدادات من GitHub Secrets
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# إعداد جميناي
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def send_telegram_pdf(file_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': CHAT_ID, 'caption': caption[:1000]}
            r = requests.post(url, files=files, data=data)
            print(f"Telegram response: {r.text}")
    except Exception as e:
        print(f"Error sending: {e}")

def create_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.add_font('Amiri', '', 'Amiri-Regular.ttf')
        pdf.set_font('Amiri', '', 14)
    except:
        pdf.set_font('Arial', '', 12)
    
    for line in text.split('\n'):
        # معالجة العربي
        reshaped = reshape(line)
        bidi_line = get_display(reshaped)
        pdf.multi_cell(0, 10, bidi_line, align='R')
    pdf.output(filename)

async def main():
    print("🚀 جاري العمل يا ياسر...")
    trends = ["مبخرة إلكترونية", "ساعة ذكية", "منظم مكياج", "خلاط محمول"]
    
    report = f"تقرير ترندات السعودية - {datetime.now().strftime('%Y-%m-%d')}\n"
    report += "="*30 + "\n\n"

    for product in trends:
        try:
            prompt = f"حلل منتج {product} للسوق السعودي: السعر المتوقع، الربح، وسيناريو إعلان تيك توك."
            response = model.generate_content(prompt)
            report += f"📦 المنتج: {product}\n{response.text}\n"
            report += f"🔗 رابط: https://m5azn.com/product?search={product}\n"
            report += "-"*20 + "\n\n"
            print(f"✅ تم تحليل {product}")
        except Exception as e:
            print(f"Error: {e}")

    file_name = "Saudi_Trend.pdf"
    create_pdf(report, file_name)
    send_telegram_pdf(file_name, "✅ أبشر يا ياسر! تقرير الـ PDF صار جاهز عندك.")

if __name__ == "__main__":
    asyncio.run(main())
