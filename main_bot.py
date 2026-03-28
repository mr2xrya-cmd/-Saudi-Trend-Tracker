import os, requests, json, time, asyncio
from datetime import datetime
from openai import OpenAI
from fpdf import FPDF

# إعدادات الوصول
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI()

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Saudi Trend Tracker - Daily Report', 0, 1, 'C')
        self.ln(5)

def send_telegram_pdf(file_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': "✅ أبشر! تقرير الـ 20 منتج ترند كاملاً بكل التفاصيل (PDF)"}
        r = requests.post(url, files=files, data=data)
        print(f"Telegram Response: {r.status_code}")

async def main():
    print("🚀 جاري تجهيز تقرير PDF الاحترافي الشامل...")
    trends = [
        "مبخرة إلكترونية", "ساعة ذكية الترا", "منظم مكياج", "مكواة بخار", "جهاز مساج",
        "خلاط محمول", "إضاءة قيمنق", "كاميرا مراقبة", "سماعات بلوتوث", "ماكينة حلاقة",
        "ميزان ذكي", "حقيبة ضد السرقة", "قلاية هوائية", "مطحنة قهوة", "حامل جوال",
        "تنظيف البشرة", "مصباح ذكي", "أدوات عناية", "منقي هواء", "وسادة طبية"
    ]
    
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    for i, product in enumerate(trends):
        prompt = f"Analyze '{product}' for Saudi market: Trend Status, Suggested Price, Expected Profit, and TikTok Ad Script. Keep it professional."
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            analysis = response.choices[0].message.content
            
            # كتابة البيانات في الـ PDF
            pdf.set_text_color(0, 102, 204) # لون أزرق للعنوان
            pdf.multi_cell(0, 10, txt=f"Product {i+1}: {product}", border=0)
            pdf.set_text_color(0, 0, 0) # لون أسود للتحليل
            pdf.multi_cell(0, 8, txt=f"Analysis:\n{analysis}", border=0)
            pdf.set_text_color(255, 0, 0) # لون أحمر للرابط
            pdf.multi_cell(0, 8, txt=f"Link: https://m5azn.com/product?search={product.replace(' ', '%20')}", border=0)
            pdf.ln(5)
            pdf.cell(0, 0, '', 'T') # خط فاصل
            pdf.ln(5)
            
            print(f"✅ Analyzed {product}")
            await asyncio.sleep(1) # تأخير بسيط للأمان
        except Exception as e:
            print(f"Error in {product}: {e}")

    # حفظ الملف والتأكد من إغلاقه قبل الإرسال
    pdf_file = "Saudi_Trend_Report.pdf"
    pdf.output(pdf_file)
    print("💾 PDF Saved successfully.")
    
    # إرسال الملف لتيليجرام
    send_telegram_pdf(pdf_file)
    print("✅ PDF Sent to Telegram!")

if __name__ == "__main__":
    asyncio.run(main())
