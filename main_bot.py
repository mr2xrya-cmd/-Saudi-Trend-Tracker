import os
import requests
import json
import logging
import time
from datetime import datetime
from openai import OpenAI
from fpdf import FPDF

# إعداد السجلات لمتابعة العمل في GitHub Actions
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# كلاس مخصص لإنشاء PDF يدعم اللغة العربية وتنسيق الصفحات
class SaudiTrendPDF(FPDF):
    def header(self):
        # إضافة عنوان في رأس كل صفحة
        try:
            self.set_font("DejaVu", "B", 15)
            self.cell(0, 10, "تقرير ترندات السوق السعودي اليومي", 0, 1, "C")
            self.ln(5)
        except:
            pass

    def footer(self):
        # إضافة رقم الصفحة في الأسفل
        self.set_y(-15)
        try:
            self.set_font("DejaVu", "", 8)
            self.cell(0, 10, f"صفحة {self.page_no()}", 0, 0, "C")
        except:
            pass

# جلب الإعدادات من GitHub Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# إعداد عميل الذكاء الاصطناعي (Gemini 2.5 Flash)
client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/models/",
 )

def analyze_product(product, index):
    """تحليل المنتج باستخدام الذكاء الاصطناعي (طريقة متزامنة لتجنب الأخطاء)"""
    prompt = f"Analyze '{product}' for Saudi market: Trend Status, Suggested Price (SAR), Profit Margin, Marketing Description, and TikTok Script. Provide a detailed summary in Arabic."
    
    try:
        logging.info(f"جاري تحليل المنتج {index}/20: {product}...")
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"خطأ في تحليل {product}: {e}")
        return f"تعذر تحليل المنتج {product} حالياً بسبب خطأ فني."

def send_pdf_to_telegram(file_path):
    """إرسال ملف PDF النهائي إلى تيليجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    try:
        logging.info("جاري إرسال ملف PDF النهائي إلى تيليجرام..." )
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {
                "chat_id": TELEGRAM_CHAT_ID, 
                "caption": f"✅ تم اكتمال تقرير الـ 20 منتج بنجاح!\n📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}"
            }
            r = requests.post(url, files=files, data=data)
            if r.status_code == 200:
                logging.info("✅ تم إرسال الملف بنجاح!")
            else:
                logging.error(f"فشل الإرسال: {r.text}")
    except Exception as e:
        logging.error(f"خطأ أثناء إرسال الملف: {e}")

def main():
    # قائمة الـ 20 منتج الأكثر طلباً في السعودية حالياً
    trends = [
        "مبخرة إلكترونية ذكية", "ساعة ذكية Ultra", "منظم مكياج دوار", "مكواة بخار محمولة", 
        "جهاز مساج الرقبة", "خلاط عصائر محمول", "إضاءة قيمنق RGB", "كاميرا مراقبة منزلية", 
        "سماعات بلوتوث عازلة", "ماكينة حلاقة VGR", "ميزان قياس دهون الجسم", "حقيبة ظهر ضد السرقة", 
        "قلاية هوائية رقمية", "مطحنة قهوة مختصة", "حامل جوال للسيارة مغناطيسي", "جهاز تنظيف البشرة", 
        "مصباح مكتب ذكي", "طقم عناية بالأظافر", "منقي هواء صغير", "وسادة طبية للظهر"
    ]

    pdf = SaudiTrendPDF()
    
    # تحميل الخطوط العربية (تأكد من وجود مجلد fonts في GitHub)
    try:
        pdf.add_font("DejaVu", "", "fonts/DejaVuSansCondensed.ttf", uni=True)
        pdf.add_font("DejaVu", "B", "fonts/DejaVuSansCondensed-Bold.ttf", uni=True)
        pdf.set_font("DejaVu", "", 12)
    except Exception as e:
        logging.warning(f"فشل تحميل الخطوط: {e}")
        pdf.set_font("Arial", "", 12)

    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # محتوى التقرير - تجميع كل التحليلات أولاً
    results = []
    for i, product in enumerate(trends, 1):
        analysis = analyze_product(product, i)
        results.append((product, analysis))
        time.sleep(1) # تأخير بسيط لضمان استقرار الـ API

    # كتابة البيانات في الـ PDF بعد اكتمال كل التحليلات الـ 20
    for i, (name, content) in enumerate(results, 1):
        # عنوان المنتج
        pdf.set_font("DejaVu", "B", 12)
        pdf.multi_cell(0, 10, txt=f"{i}. المنتج: {name}", align="R")
        
        # تفاصيل التحليل
        pdf.set_font("DejaVu", "", 10)
        pdf.multi_cell(0, 7, txt=content, align="R")
        
        # رابط المخازن
        pdf.set_text_color(0, 0, 255)
        link = f"https://m5azn.com/product?search={name.replace(' ', '+' )}"
        pdf.multi_cell(0, 7, txt=f"رابط البحث في مخازن: {link}", align="R")
        pdf.set_text_color(0, 0, 0)
        
        pdf.ln(5)
        pdf.cell(0, 0, "", "T") # خط فاصل
        pdf.ln(5)

    # حفظ الملف وإرساله فقط بعد الانتهاء من كل شيء
    file_name = "Saudi_Trend_Report.pdf"
    pdf.output(file_name)
    send_pdf_to_telegram(file_name)

if __name__ == "__main__":
    main()
