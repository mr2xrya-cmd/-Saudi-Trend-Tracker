import os
import requests
import logging
import time
from datetime import datetime
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def reshape(text):
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except:
        return str(text)

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
    
    for attempt in range(3):
        try:
            logging.info(f"جاري تحليل المنتج {index}/20: {product}...")
            response = client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                wait = 65
                logging.warning(f"Rate limit، انتظر {wait} ثانية...")
                time.sleep(wait)
            elif "403" in error_str and "leaked" in error_str:
                logging.error("❌ API key مسرّب! يجب تغييره في GitHub Secrets")
                return f"[خطأ: API key مسرّب - المنتج: {product}]"
            else:
                logging.error(f"خطأ: {e}")
                return f"تعذر تحليل {product}"
    return f"تعذر تحليل {product} بعد 3 محاولات"

def send_pdf_to_telegram(file_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as f:
            r = requests.post(url, files={"document": f}, data={
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": f"✅ تقرير الـ 20 منتج مكتمل!\n📅 {datetime.now().strftime('%Y-%m-%d')}"
            })
            if r.status_code == 200:
                logging.info("✅ تم الإرسال بنجاح!")
            else:
                logging.error(f"فشل الإرسال: {r.text}")
    except Exception as e:
        logging.error(f"خطأ: {e}")

def main():
    trends = [
        "مبخرة إلكترونية ذكية", "ساعة ذكية Ultra", "منظم مكياج دوار", "مكواة بخار محمولة",
        "جهاز مساج الرقبة", "خلاط عصائر محمول", "إضاءة قيمنق RGB", "كاميرا مراقبة منزلية",
        "سماعات بلوتوث عازلة", "ماكينة حلاقة VGR", "ميزان قياس دهون الجسم", "حقيبة ظهر ضد السرقة",
        "قلاية هوائية رقمية", "مطحنة قهوة مختصة", "حامل جوال للسيارة مغناطيسي", "جهاز تنظيف البشرة",
        "مصباح مكتب ذكي", "طقم عناية بالأظافر", "منقي هواء صغير", "وسادة طبية للظهر"
    ]

    # تسجيل خط Amiri
    font_path = "Amiri-Regular.ttf"
    if not os.path.exists(font_path):
        logging.error(f"❌ ملف الخط غير موجود: {font_path}")
        return
    
    pdfmetrics.registerFont(TTFont("Amiri", font_path))

    # تجميع التحليلات
    all_results = []
    for i, product in enumerate(trends, 1):
        analysis = analyze_product(product, i)
        all_results.append((product, analysis))
        time.sleep(13)  # 5 طلبات/دقيقة → انتظر 13 ثانية بين كل طلب

    # إنشاء PDF
    file_name = "Saudi_Trend_Report.pdf"
    doc = SimpleDocTemplate(file_name, pagesize=A4,
                             rightMargin=40, leftMargin=40,
                             topMargin=40, bottomMargin=40)

    title_style = ParagraphStyle("title", fontName="Amiri", fontSize=18,
                                  alignment=TA_RIGHT, spaceAfter=10)
    product_style = ParagraphStyle("product", fontName="Amiri", fontSize=14,
                                    alignment=TA_RIGHT, spaceAfter=6, textColor="#1a1a8c")
    body_style = ParagraphStyle("body", fontName="Amiri", fontSize=11,
                                 alignment=TA_RIGHT, spaceAfter=4, leading=18)
    link_style = ParagraphStyle("link", fontName="Amiri", fontSize=10,
                                 alignment=TA_RIGHT, textColor="#0000cc")

    story = []
    story.append(Paragraph(reshape("تقرير ترندات السوق السعودي اليومي"), title_style))
    story.append(Paragraph(reshape(f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}"), body_style))
    story.append(HRFlowable(width="100%"))
    story.append(Spacer(1, 12))

    for i, (name, content) in enumerate(all_results, 1):
        story.append(Paragraph(reshape(f"{i}. المنتج: {name}"), product_style))
        for line in content.split('\n'):
            line = line.strip()
            if line:
                story.append(Paragraph(reshape(line), body_style))
        link = f"https://m5azn.com/product?search={name.replace(' ', '+')}"
        story.append(Paragraph(reshape(f"رابط البحث في مخازن: {link}"), link_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%"))
        story.append(Spacer(1, 8))

    doc.build(story)
    logging.info(f"✅ تم حفظ: {file_name}")
    send_pdf_to_telegram(file_name)

if __name__ == "__main__":
    main()
