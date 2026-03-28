import os
import requests
import logging
import time
from datetime import datetime
from openai import OpenAI
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def reshape(text):
    """معالجة النص العربي ليظهر بشكل صحيح في PDF"""
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except:
        return text

class SaudiTrendPDF(FPDF):
    def header(self):
        try:
            self.set_font("Amiri", "", 20)
            self.cell(0, 15, reshape("تقرير ترندات السوق السعودي اليومي"), 0, 1, "C")
            self.ln(5)
        except:
            pass

    def footer(self):
        self.set_y(-15)
        try:
            self.set_font("Amiri", "", 10)
            self.cell(0, 10, reshape(f"صفحة {self.page_no()}"), 0, 0, "C")
        except:
            pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

def analyze_product(product, index):
    prompt = f"""حلل المنتج '{product}' للسوق السعودي. قدم تقريراً مفصلاً يشمل:
1. حالة الترند
2. السعر المقترح (ريال سعودي)
3. هامش الربح
4. وصف تسويقي
5. سكريبت إعلان تيك توك
الرد باللغة العربية فقط."""
    
    try:
        logging.info(f"جاري تحليل المنتج {index}/20: {product}...")
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"خطأ في تحليل {product}: {e}")
        return f"تعذر تحليل المنتج {product} حالياً."

def send_pdf_to_telegram(file_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    try:
        logging.info("جاري إرسال ملف PDF إلى تيليجرام...")
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": f"✅ تقرير الـ 20 منتج مكتمل!\n📅 {datetime.now().strftime('%Y-%m-%d')}"
            }
            r = requests.post(url, files=files, data=data)
            if r.status_code == 200:
                logging.info("✅ تم إرسال الملف بنجاح!")
            else:
                logging.error(f"فشل الإرسال: {r.text}")
    except Exception as e:
        logging.error(f"خطأ أثناء إرسال الملف: {e}")

def main():
    trends = [
        "مبخرة إلكترونية ذكية", "ساعة ذكية Ultra", "منظم مكياج دوار", "مكواة بخار محمولة",
        "جهاز مساج الرقبة", "خلاط عصائر محمول", "إضاءة قيمنق RGB", "كاميرا مراقبة منزلية",
        "سماعات بلوتوث عازلة", "ماكينة حلاقة VGR", "ميزان قياس دهون الجسم", "حقيبة ظهر ضد السرقة",
        "قلاية هوائية رقمية", "مطحنة قهوة مختصة", "حامل جوال للسيارة مغناطيسي", "جهاز تنظيف البشرة",
        "مصباح مكتب ذكي", "طقم عناية بالأظافر", "منقي هواء صغير", "وسادة طبية للظهر"
    ]

    pdf = SaudiTrendPDF()
    font_path = "Amiri-Regular.ttf"

    if not os.path.exists(font_path):
        logging.error(f"❌ لم يتم العثور على ملف الخط: {font_path}")
        return

    pdf.add_font("Amiri", "", font_path)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    all_results = []
    for i, product in enumerate(trends, 1):
        analysis = analyze_product(product, i)
        all_results.append((product, analysis))
        time.sleep(1.5)

    for i, (name, content) in enumerate(all_results, 1):
        # عنوان المنتج
        pdf.set_font("Amiri", "", 16)
        pdf.multi_cell(0, 10, text=reshape(f"{i}. المنتج: {name}"), align="R")

        # محتوى التحليل - نقسمه لأسطر لتجنب مشاكل العرض
        pdf.set_font("Amiri", "", 12)
        for line in content.split('\n'):
            line = line.strip()
            if line:
                pdf.multi_cell(0, 8, text=reshape(line), align="R")

        # رابط البحث
        pdf.set_text_color(0, 0, 255)
        link_text = f"رابط البحث في مخازن: https://m5azn.com/product?search={name.replace(' ', '+')}"
        pdf.multi_cell(0, 8, text=reshape(link_text), align="R")
        pdf.set_text_color(0, 0, 0)

        pdf.ln(5)
        pdf.cell(0, 0, "", "T")
        pdf.ln(5)

    file_name = "Saudi_Trend_Report.pdf"
    pdf.output(file_name)
    logging.info(f"✅ تم حفظ الملف: {file_name}")
    send_pdf_to_telegram(file_name)

if __name__ == "__main__":
    main()
