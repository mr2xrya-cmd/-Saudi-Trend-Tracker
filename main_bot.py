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
# استخدمنا الاسم الأساسي للموديل
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
        print(f"❌ خطأ إرسال تيليجرام: {e}")

def create_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    
    try:
        pdf.add_font('Amiri', '', 'Amiri-Regular.ttf')
        pdf.set_font('Amiri', '', 12) # صغرنا الخط شوي عشان المساحة
    except:
        print("⚠️ ملف الخط Amiri-Regular.ttf غير موجود في المستودع!")
        pdf.set_font('Arial', '', 10)
    
    for line in text.split('\n'):
        if not line.strip():
            pdf.ln(5)
            continue
        
        # تنظيف النص من النجوم والمربعات اللي يحطها جميناي وتخرب التنسيق
        clean_line = line.replace('*', '').replace('#', '').replace('-', ' ')
        
        try:
            reshaped = reshape(clean_line)
            bidi_line = get_display(reshaped)
            pdf.multi_cell(180, 8, bidi_line, align='R')
        except Exception as e:
            print(f"⚠️ فشل كتابة سطر في PDF: {e}")
            continue

    pdf.output(filename)

async def main():
    print("🚀 يبدو أننا بدأنا العمل يا ياسر...")
    # جربنا بمنتجين فقط للتأكد من السرعة والوصول
    trends = ["مبخرة إلكترونية", "ساعة ذكية"] 
    
    report = f"تقرير ترندات السعودية - {datetime.now().strftime('%Y-%m-%d')}\n"
    report += "="*30 + "\n\n"

    for product in trends:
        try:
            print(f"🔍 جاري تحليل: {product}...")
            prompt = f"حلل منتج {product} للسوق السعودي باختصار: السعر، الربح المتوقع، وفكرة إعلان."
            response = model.generate_content(prompt)
            
            if response.text:
                report += f"📦 {product}\n{response.text}\n"
                report += "-"*20 + "\n\n"
                print(f"✅ تم الحصول على نص لـ {product}")
            else:
                print(f"⚠️ رد فارغ من الذكاء الاصطناعي لـ {product}")
                
            await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ خطأ في API جميناي لـ {product}: {e}")

    # ميزة رهيبة: بنطبع التقرير في الـ Logs عشان تشوفه لو الـ PDF فشل
    print("\n--- محتوى التقرير النهائي ---")
    print(report)
    print("---------------------------\n")

    if len(report) > 100: # تأكد إن فيه محتوى حقيقي
        file_name = "Saudi_Trend.pdf"
        create_pdf(report, file_name)
        send_telegram_pdf(file_name, f"✅ أبشر يا ياسر! تقرير الـ PDF لـ {len(trends)} منتجات.")
    else:
        print("❌ التقرير فارغ جداً، لن يتم إنشاء ملف PDF.")

if __name__ == "__main__":
    asyncio.run(main())
