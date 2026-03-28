import os
import requests
import json
import logging
import asyncio
from datetime import datetime
from openai import OpenAI
from fpdf import FPDF

# إعداد السجلات لمتابعة العمل في GitHub Actions
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# كلاس مخصص لإنشاء PDF يدعم اللغة العربية وتنسيق الصفحات
class SaudiTrendPDF(FPDF):
    def header(self):
        # إضافة عنوان في رأس كل صفحة
        if hasattr(self, 'font_family') and 'DejaVu' in self.fonts:
            self.set_font("DejaVu", "B", 15)
            self.cell(0, 10, "تقرير ترندات السوق السعودي اليومي", 0, 1, "C")
            self.ln(5)

    def footer(self):
        # إضافة رقم الصفحة في الأسفل
        self.set_y(-15)
        if hasattr(self, 'font_family') and 'DejaVu' in self.fonts:
            self.set_font("DejaVu", "", 8)
            self.cell(0, 10, f"صفحة {self.page_no()}", 0, 0, "C")

# جلب الإعدادات من GitHub Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# إعداد عميل الذكاء الاصطناعي (Gemini 2.5 Flash)
client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/models/",
 )

async def analyze_product(product, index):
    """تحليل المنتج باستخدام الذكاء الاصطناعي"""
    prompt = f"""
    حلل المنتج التالي للسوق السعودي: '{product}'
    المطلوب تقديم تقرير شامل باللغة العربية يتضمن:
    1. حالة الترند (بداية، ذروة، تشبع).
    2. السعر المقترح للبيع بالريال السعودي وهامش الربح.
    3. وصف تسويقي جذاب.
    4. سكريبت إعلان تيك توك (3 ثواني هوك).
    5. رابط البحث في مخازن: https://m5azn.com/product?search={product.replace(' ', '+' )}
    
    أجب بصيغة نصية منظمة وواضحة جداً.
    """
    try:
        logging.info(f"جاري تحليل المنتج {index}: {product}...")
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"خطأ في تحليل {product}: {e}")
        return f"تعذر تحليل المنتج {product} حالياً."

def send_pdf_to_telegram(file_path):
    """إرسال ملف PDF النهائي إلى تيليجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    try:
        logging.info("جاري إرسال ملف PDF إلى تيليجرام..." )
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

async def main():
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
    except:
        logging.warning("لم يتم العثور على الخطوط، سيتم استخدام الخط الافتراضي (قد لا يظهر العربي بشكل صحيح)")

    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # محتوى التقرير
    results = []
    for i, product in enumerate(trends, 1):
        analysis = await analyze_product(product, i)
        results.append((product, analysis))
        # تأخير بسيط لتجنب ضغط الـ API
        await asyncio.sleep(1)

    # كتابة البيانات في الـ PDF بعد اكتمال كل التحليلات
    for i, (name, content) in enumerate(results, 1):
        pdf.set_font("DejaVu", "B", 12)
        pdf.multi_cell(0, 10, txt=f"{i}. المنتج: {name}", align="R")
        pdf.set_font("DejaVu", "", 10)
        pdf.multi_cell(0, 7, txt=content, align="R")
        pdf.ln(5)
        pdf.cell(0, 0, "", "T") # خط فاصل
        pdf.ln(5)

    # حفظ الملف وإرساله
    file_name = "Saudi_Trend_Report.pdf"
    pdf.output(file_name)
    send_pdf_to_telegram(file_name)

if __name__ == "__main__":
    asyncio.run(main())
