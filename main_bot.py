import os, requests, time, asyncio
from datetime import datetime
from google import genai
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# الأسرار
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = genai.Client(api_key=GEMINI_KEY)

def send_telegram_pdf(file_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': CHAT_ID, 'caption': caption[:1000]}
            r = requests.post(url, files=files, data=data)
            print(f"✅ تيليجرام: {r.status_code}")
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
            # تحديد عرض الخلية بـ 180 لتفادي خطأ المساحة
            pdf.multi_cell(180, 8, bidi_line, align='R')
        except:
            continue
    pdf.output(filename)

async def main():
    print("🚀 محاولة أخيرة وقوية يا ياسر...")
    trends = ["مبخرة إلكترونية", "ساعة ذكية"]
    report = f"تقرير ترندات السعودية - {datetime.now().strftime('%Y-%m-%d')}\n\n"

    for product in trends:
        try:
            print(f"🔍 تحليل: {product}...")
            # جربنا نغير الموديل لـ gemini-1.5-pro إذا فلاش معاند
            response = client.models.generate_content(
                model='gemini-1.5-flash', 
                contents=f"حلل منتج {product} للسوق السعودي: السعر، الربح، وفكرة إعلان."
            )
            if response.text:
                report += f"📦 {product}\n{response.text}\n---\n"
                print(f"✅ تم تحليل {product}")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ خطأ في {product}: {e}")

    if len(report) > 50:
        create_pdf(report, "Saudi_Trend.pdf")
        send_telegram_pdf("Saudi_Trend.pdf", "✅ أبشر يا ياسر، التقرير وصل!")
    else:
        print("❌ التقرير فاضي، شيك على الـ API Key")

if __name__ == "__main__":
    asyncio.run(main())
