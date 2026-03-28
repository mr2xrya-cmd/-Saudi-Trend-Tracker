import os
import requests
import logging
import time
from datetime import datetime
from openai import OpenAI
from fpdf import FPDF

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SaudiTrendPDF(FPDF):
    def header(self):
        if "Amiri" in self.fonts:
            self.set_font("Amiri", "", 20)
            self.cell(0, 15, "تقرير ترندات السوق السعودي اليومي", 0, 1, "C")
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        if "Amiri" in self.fonts:
            self.set_font("Amiri", "", 10)
            self.cell(0, 10, f"صفحة {self.page_no()}", 0, 0, "C")

# جلب الإعدادات
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/models/",
 )

def analyze_product(product, index):
    prompt = f"Analyze the product '{product}' for the Saudi market. Provide a detailed report in Arabic including: Trend Status, Suggested Price (SAR), Profit Margin, Marketing Description, and a TikTok Ad Script. Ensure the output is only in Arabic."
    try:
        logging.info(f"جاري تحليل المنتج {index}/20: {product}...")
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"خطأ في تحليل {product}: {e}")
        return f"تعذر تحليل المنتج {product} حالياً."

def send_pdf_to_telegram(file_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    try:
        logging.info("جاري إرسال ملف PDF النهائي..." )
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": f"✅ تقرير الـ 20 منتج جاهز\n📅 {datetime.now().strftime('%Y-%m-%d')}"}
            requests.post(url, files=files, data=data)
    except Exception as e:
        logging.error(f"خطأ في الإرسال: {e}")

def main():
    trends = [
        "مبخرة إلكترونية ذكية", "ساعة ذكية Ultra", "منظم مكياج دوار", "مكواة بخار محمولة", 
        "جهاز مساج الرقبة", "خلاط عصائر محمول", "إضاءة قيمنق RGB", "كاميرا مراقبة منزلية", 
        "سماعات بلوتوث عازلة", "ماكينة حلاقة VGR", "ميزان قياس دهون الجسم", "حقيبة ظهر ضد السرقة", 
        "قلاية هوائية رقمية", "مطحنة قهوة مختصة", "حامل جوال للسيارة مغناطيسي", "جهاز تنظيف البشرة", 
        "مصباح مكتب ذكي", "طقم عناية بالأظافر", "منقي هواء صغير", "وسادة طبية للظهر"
    ]

    pdf = SaudiTrendPDF()
    
    # استخدام الخط الذي قمت أنت برفعه (Amiri-Regular.ttf)
    font_path = "Amiri-Regular.ttf"
    
    if os.path.exists(font_path):
        pdf.add_font("Amiri", "", font_path)
        pdf.set_font("Amiri", "", 12)
    else:
        logging.error("❌ لم يتم العثور على خط Amiri-Regular.ttf في المجلد الرئيسي!")
        return

    pdf.add_page()
    
    all_results = []
    for i, product in enumerate(trends, 1):
        analysis = analyze_product(product, i)
        all_results.append((product, analysis))
        time.sleep(1)

    for i, (name, content) in enumerate(all_results, 1):
        pdf.set_font("Amiri", "", 16)
        pdf.multi_cell(0, 10, txt=f"{i}. المنتج: {name}", align="R")
        pdf.set_font("Amiri", "", 12)
        pdf.multi_cell(0, 8, txt=content, align="R")
        pdf.set_text_color(0, 0, 255)
        pdf.multi_cell(0, 8, txt=f"رابط المخازن: https://m5azn.com/product?search={name.replace(' ', '+' )}", align="R")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        pdf.cell(0, 0, "", "T")
        pdf.ln(5)

    file_name = "Saudi_Trend_Report.pdf"
    pdf.output(file_name)
    send_pdf_to_telegram(file_name)

if __name__ == "__main__":
    main()
