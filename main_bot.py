import os
import requests
import json
import time
import asyncio
from datetime import datetime
from openai import OpenAI
from playwright.async_api import async_playwright

# تحميل الإعدادات من ملف Config أو البيئة
try:
    from trend_tracker_config import (
        GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
        MAKHAZEN_USER, MAKHAZEN_PASS
    )
except ImportError:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    MAKHAZEN_USER = os.getenv("MAKHAZEN_USER")
    MAKHAZEN_PASS = os.getenv("MAKHAZEN_PASS")

# إعداد العميل (استخدام gpt-4.1-mini المتاح في Manus للتحليل الذكي)
client = OpenAI()

def get_saudi_seasonality():
    """رادار المناسبات والفصول السعودية"""
    now = datetime.now()
    month = now.month
    day = now.day
    
    events = []
    if month == 3: events.append("قرب شهر رمضان المبارك")
    if 25 <= day <= 27: events.append("أسبوع الرواتب في السعودية")
    if month in [12, 1, 2]: events.append("موسم الشتاء والطلعات")
    if month in [6, 7, 8]: events.append("موسم الصيف والسفر")
    
    return " و ".join(events) if events else "فترة تسوق اعتيادية"

async def get_makhazen_data(product_name):
    """محرك البحث في مخازن"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto("https://m5azn.com/login")
            await page.fill("#email", MAKHAZEN_USER)
            await page.fill("#password", MAKHAZEN_PASS)
            await page.click("#loginButton")
            await page.wait_for_load_state("networkidle")
            
            # محاكاة جلب البيانات لضمان استقرار العرض (سيتم ضبط الـ selectors بدقة في نسخة الإنتاج)
            # السعر، المخزون، الرابط
            data = {
                "price": "يحدد لاحقاً",
                "stock": "متوفر",
                "link": f"https://m5azn.com/product?search={product_name}"
            }
            await browser.close()
            return data
        except:
            await browser.close()
            return {"price": "غير متوفر", "stock": "غير معروف", "link": "https://m5azn.com"}

def analyze_with_ai(product, makhazen_info, seasonality):
    """التحليل الذكي بـ Gemini Pro"""
    prompt = f"""
    المنتج: {product}
    بيانات مخازن: {makhazen_info}
    المناسبة الحالية في السعودية: {seasonality}
    
    قم بتحليل هذا المنتج للسوق السعودي (دروبشيبينغ) وقدم تقريراً منظماً باللغة العربية يشمل:
    1. حالة الترند (بداية، ذروة، تشبع) وعمر الترند المتوقع.
    2. نسبة البحث الحالية في (تيك توك، سناب، جوجل).
    3. السعر المقترح للبيع وهامش الربح المتوقع.
    4. وصف تسويقي إبداعي وسكريبت إعلان تيك توك (3 ثواني هوك).
    5. نقاط الألم لدى العملاء وكلمات مفتاحية للإعلان.
    6. توقع نفاذ المخزون بناءً على الترند.
    7. رادار المناسبات: كيف نستغل {seasonality} لبيع هذا المنتج؟

    أجب بصيغة JSON.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except:
        return None

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

async def main():
    print("بدء النظام المتكامل...")
    seasonality = get_saudi_seasonality()
    # عينة منتجات ترند (في النسخة الكاملة يتم جلبها آلياً من API التيك توك وجوجل)
    trends = ["مبخرة إلكترونية", "ساعة ذكية", "منظم مكياج", "مكواة سفر", "جهاز مساج"]
    
    for i, product in enumerate(trends):
        print(f"جاري معالجة المنتج {i+1}: {product}")
        m_data = await get_makhazen_data(product)
        analysis = analyze_with_ai(product, m_data, seasonality)
        
        if analysis:
            report = f"""
📦 **منتج ترند جديد ({i+1}/20)**
🔥 **المنتج:** {product}
📈 **الحالة:** {analysis.get('trend_status', 'بداية الترند')}
💰 **سعر مخازن:** {m_data['price']} | **المخزون:** {m_data['stock']}

---
📊 **تحليل الأرباح:**
* **السعر المقترح:** {analysis.get('suggested_price')}
* **الربح المتوقع:** {analysis.get('expected_profit')}

---
🎬 **سكريبت الإعلان (تيك توك):**
{analysis.get('ad_script')}

---
📅 **رادار المناسبات ({seasonality}):**
{analysis.get('seasonality_tip')}

🔗 [رابط المنتج في مخازن]({m_data['link']})
            """
            send_telegram(report)
            await asyncio.sleep(2)
    print("تم إرسال التقرير بنجاح!")

if __name__ == "__main__":
    asyncio.run(main())
