import os
import requests
import logging
import time
from datetime import datetime
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import arabic_reshaper
from bidi.algorithm import get_display
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def reshape(text):
    try:
        text = re.sub(r'[#*_`]', '', str(text))
        return get_display(arabic_reshaper.reshape(text.strip()))
    except:
        return str(text)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

def get_trending_products():
    prompt = """أنت خبير في التجارة الإلكترونية السعودية.
حدد أكثر 10 منتجات طلباً وترنداً الآن في السوق السعودي على منصات تيك توك، سناب شات، إكس، وجوجل.
أعطني فقط أسماء المنتجات العشرة، كل منتج في سطر منفصل، بدون ترقيم أو شرح.
ركز على المنتجات العملية ذات الطلب العالي والربحية الجيدة."""

    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        products_text = response.choices[0].message.content.strip()
        products = [p.strip() for p in products_text.split('\n') if p.strip()][:10]
        logging.info(f"✅ تم الحصول على {len(products)} منتج ترند")
        return products
    except Exception as e:
        logging.error(f"خطأ في جلب الترندات: {e}")
        return [
            "مبخرة إلكترونية ذكية", "ساعة ذكية Ultra", "منظم مكياج دوار",
            "جهاز مساج الرقبة", "سماعات بلوتوث عازلة", "قلاية هوائية رقمية",
            "جهاز تنظيف البشرة", "مصباح مكتب ذكي", "منقي هواء صغير", "وسادة طبية للظهر"
        ]

def analyze_product(product, index):
    prompt = f"""أنت خبير تحليل سوق ورادار ربحية للتجارة الإلكترونية السعودية.
حلل المنتج: {product}

قدم التحليل بهذا الشكل بالضبط بدون نجوم أو هاشتاقات:

حالة الترند: [قوي/متوسط/ضعيف] - [سبب مختصر]

نطاق السعر في السوق السعودي: من [X] ريال إلى [Y] ريال
السعر المقترح للبيع: [Z] ريال
سعر المورد المتوقع: [W] ريال

رادار الربحية:
هامش الربح: [النسبة المئوية]%
الربح المتوقع لكل وحدة: [المبلغ] ريال
ميزانية الإعلانات المقترحة: [المبلغ] ريال لكل يوم
نقطة التعادل: [عدد] وحدات يومياً
توقع الربح الشهري: [المبلغ] ريال بافتراض [عدد] وحدة يومياً

وصف تسويقي: [جملتان جذابتان للمنتج]

سكريبت تيك توك 15 ثانية:
[النص الكامل للإعلان]"""

    for attempt in range(5):
        try:
            logging.info(f"تحليل {index}/10: {product} (محاولة {attempt+1})...")
            response = client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                match = re.search(r'retryDelay.*?(\d+)s', error_str)
                wait = int(match.group(1)) + 5 if match else 70
                logging.warning(f"Rate limit، انتظر {wait} ثانية...")
                time.sleep(wait)
            elif "403" in error_str and "leaked" in error_str:
                logging.error("❌ API key مسرّب!")
                return f"خطأ: API key مسرّب - المنتج: {product}"
            else:
                logging.error(f"خطأ: {e}")
                time.sleep(15)
    return f"تعذر تحليل {product} بعد 5 محاولات"

def send_pdf_to_telegram(file_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as f:
            r = requests.post(url, files={"document": f}, data={
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": f"📊 تقرير ترندات السوق السعودي\n📅 {datetime.now().strftime('%Y-%m-%d')}\n✅ تم تحليل 10 منتجات ترند"
            })
            logging.info("✅ تم الإرسال!" if r.status_code == 200 else f"فشل: {r.text}")
    except Exception as e:
        logging.error(f"خطأ: {e}")

def main():
    font_path = "Amiri-Regular.ttf"
    if not os.path.exists(font_path):
        logging.error("❌ ملف الخط غير موجود")
        return

    pdfmetrics.registerFont(TTFont("Amiri", font_path))

    logging.info("🔍 جاري البحث عن أكثر المنتجات ترنداً...")
    trends = get_trending_products()
    time.sleep(20)

    all_results = []
    for i, product in enumerate(trends, 1):
        analysis = analyze_product(product, i)
        all_results.append((product, analysis))
        if i < len(trends):
            time.sleep(20)

    # أنماط التصميم
    title_style = ParagraphStyle("title", fontName="Amiri", fontSize=20,
                                  alignment=TA_CENTER, spaceAfter=6,
                                  textColor=HexColor("#1a1a6e"))
    date_style = ParagraphStyle("date", fontName="Amiri", fontSize=11,
                                 alignment=TA_CENTER, spaceAfter=4,
                                 textColor=HexColor("#555555"))
    product_style = ParagraphStyle("product", fontName="Amiri", fontSize=15,
                                    alignment=TA_RIGHT, spaceAfter=6,
                                    textColor=HexColor("#0d47a1"))
    section_style = ParagraphStyle("section", fontName="Amiri", fontSize=12,
                                    alignment=TA_RIGHT, spaceAfter=3,
                                    textColor=HexColor("#1b5e20"))
    body_style = ParagraphStyle("body", fontName="Amiri", fontSize=11,
                                 alignment=TA_RIGHT, spaceAfter=3, leading=18)
    link_style = ParagraphStyle("link", fontName="Amiri", fontSize=10,
                                 alignment=TA_RIGHT, textColor=HexColor("#0000cc"),
                                 spaceAfter=6)

    # بناء PDF
    file_name = "Saudi_Trend_Report.pdf"
    doc = SimpleDocTemplate(file_name, pagesize=A4,
                             rightMargin=45, leftMargin=45,
                             topMargin=40, bottomMargin=40)
    story = []

    story.append(Paragraph(reshape("📊 تقرير ترندات السوق السعودي"), title_style))
    story.append(Paragraph(reshape(f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}"), date_style))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor("#1a1a6e")))
    story.append(Spacer(1, 14))

    for i, (name, content) in enumerate(all_results, 1):
        story.append(Paragraph(reshape(f"● المنتج {i}: {name}"), product_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#bbbbbb")))
        story.append(Spacer(1, 4))

        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            if any(line.startswith(k) for k in ["حالة الترند", "رادار الربحية", "وصف تسويقي", "سكريبت تيك توك"]):
                story.append(Paragraph(reshape(line), section_style))
            else:
                story.append(Paragraph(reshape(line), body_style))

        story.append(Paragraph(reshape(f"🔗 البحث في مخازن: m5azn.com ← {name}"), link_style))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#dddddd")))
        story.append(Spacer(1, 10))

    doc.build(story)
    logging.info(f"✅ تم حفظ: {file_name}")
    send_pdf_to_telegram(file_name)

if __name__ == "__main__":
    main()
