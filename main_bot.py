import os, requests, json, time, asyncio
from datetime import datetime
from openai import OpenAI

# تحميل الإعدادات من GitHub Secrets
# ملاحظة: تأكد إن أسماء السكرت في GitHub تطابق هذي الأسماء تماماً
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# إعداد العميل (تأكد من إعداد الـ Base URL إذا كنت تستخدم Gemini عبر مكتبة OpenAI)
client = OpenAI(api_key=GEMINI_API_KEY)

def send_telegram_file(file_path, caption):
    """دالة محسنة لإرسال الملفات مع معالجة أخطاء تيليجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    
    # التيليجرام يرفض الكابشن إذا زاد عن 1024 حرف، هنا نقصه للاحتياط
    if len(caption) > 1000:
        caption = caption[:950] + "... (التفاصيل كاملة داخل الملف)"

    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            r = requests.post(url, files=files, data=data)
            
            result = r.json()
            if r.status_code == 200 and result.get("ok"):
                print("✅ تم إرسال الملف لتيليجرام بنجاح!")
            else:
                print(f"❌ فشل الإرسال! كود الخطأ: {r.status_code}")
                print(f"السبب من تيليجرام: {result.get('description')}")
                
    except Exception as e:
        print(f"حدث خطأ أثناء محاولة الإرسال: {e}")

async def main():
    print("🚀 جاري توليد التقرير الشامل وتحليله...")
    
    trends = [
        "مبخرة إلكترونية", "ساعة ذكية الترا", "منظم مكياج", "مكواة بخار", "جهاز مساج",
        "خلاط محمول", "إضاءة قيمنق", "كاميرا مراقبة", "سماعات بلوتوث", "ماكينة حلاقة",
        "ميزان ذكي", "حقيبة ضد السرقة", "قلاية هوائية", "مطحنة قهوة", "حامل جوال",
        "تنظيف البشرة", "مصباح ذكي", "أدوات عناية", "منقي هواء", "وسادة طبية"
    ]
    
    full_report_text = f"🚀 تقرير ترندات السعودية - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    full_report_text += "="*40 + "\n\n"

    for i, product in enumerate(trends):
        prompt = f"Analyze product '{product}' for Saudi market: Trend Status, Suggested Price, Expected Profit, and TikTok Ad Script. Keep it professional and detailed."
        
        try:
            # استخدمنا موديل GPT-4o-mini أو الموديل المتوفر لديك
            response = client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[{"role": "user", "content": prompt}]
            )
            analysis_text = response.choices[0].message.content
            
            full_report_text += f"📦 المنتج ({i+1}/20): {product}\n"
            full_report_text += f"{analysis_text}\n"
            full_report_text += f"🔗 رابط مخازن: https://m5azn.com/product?search={product.replace(' ', '%20')}\n"
            full_report_text += "-"*30 + "\n\n"
            
            print(f"✅ تم تحليل {product}")
            await asyncio.sleep(1) # تأخير بسيط لتجنب الـ Rate Limit
                
        except Exception as e:
            print(f"Error analyzing {product}: {e}")

    # حفظ التقرير في ملف نصي بصيغة UTF-8 ليدعم العربي
    file_name = "Saudi_Trend_Report.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(full_report_text)

    # إرسال الملف
    send_telegram_file(file_name, "✅ أبشر يا ياسر! هذا هو تقرير الـ 20 منتج ترند كامل وبالتفصيل.")
    print("🏁 انتهت العملية.")

if __name__ == "__main__":
    asyncio.run(main())
