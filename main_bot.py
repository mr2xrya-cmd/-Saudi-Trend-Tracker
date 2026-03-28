import os, requests, json, time, asyncio
from datetime import datetime
from openai import OpenAI
from fpdf import FPDF

# تحميل الإعدادات من GitHub Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI()

def send_telegram_pdf(file_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': "✅ تقرير الـ 20 منتج ترند جاهز للعرض (PDF)"}
        requests.post(url, files=files, data=data)

async def main():
    print("🚀 جاري تجهيز تقرير PDF الاحترافي...")
    trends = ["مبخرة إلكترونية", "ساعة ذكية الترا", "منظم مكياج", "مكواة بخار", "جهاز مساج", "خلاط محمول", "إضاءة قيمنق", "كاميرا مراقبة"]
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Saudi Trend Report", ln=True, align='C')
    pdf.ln(10)

    for i, product in enumerate(trends):
        prompt = f"حلل منتج '{product}' للسوق السعودي: حالة الترند، السعر المقترح، الربح المتوقع. أجب باختصار."
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            analysis = response.choices[0].message.content
            
            pdf.multi_cell(0, 10, txt=f"{i+1}. {product}")
            pdf.multi_cell(0, 10, txt=f"Analysis: {analysis}")
            pdf.multi_cell(0, 10, txt=f"Link: https://m5azn.com/product?search={product}")
            pdf.ln(5)
            print(f"✅ تم تحليل {product}")
        except: pass

    pdf_file = "Trend_Report.pdf"
    pdf.output(pdf_file)
    send_telegram_pdf(pdf_file)
    print("✅ تم إرسال الـ PDF!")

if __name__ == "__main__":
    asyncio.run(main())
