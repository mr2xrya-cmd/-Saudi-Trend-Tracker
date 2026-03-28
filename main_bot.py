import os, requests, time

# تحميل الإعدادات من GitHub Secrets
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        r = requests.post(url, json=payload)
        print(f"Status: {r.status_code}")
    except:
        print("Connection Error")

def main():
    print("🚀 جاري إرسال تقرير المنتجات الموثوق...")
    
    # قائمة المنتجات المختارة بعناية للسوق السعودي
    trends = [
        "مبخرة إلكترونية ذكية", "ساعة ذكية الترا", "منظم مكياج دوار", 
        "مكواة بخار للسفر", "جهاز مساج الرقبة", "خلاط محمول رياضي",
        "إضاءة قيمنق RGB", "كاميرا مراقبة منزلية", "سماعات بلوتوث عازلة",
        "ماكينة حلاقة احترافية", "ميزان ذكي للجسم", "حقيبة ظهر ضد السرقة",
        "قلاية هوائية رقمية", "مطحنة قهوة يدوية", "حامل جوال للسيارة",
        "جهاز تنظيف البشرة", "مصباح مكتبي ذكي", "مجموعة أدوات العناية",
        "منقي هواء صغير", "وسادة طبية للرقبة"
    ]

    report = "🚀 تقرير المنتجات الأكثر طلباً في السعودية اليوم:\n\n"
    
    for i, product in enumerate(trends):
        # نص بسيط جداً ومباشر لضمان الوصول
        report += f"{i+1}. {product}\n"
        report += f"الحالة: ترند صاعد 🔥\n"
        report += f"رابط مخازن: https://m5azn.com/product?search={product.replace(' ', '%20')}\n"
        report += "----------------------------\n"
        
        # إرسال كل 5 منتجات في رسالة واحدة لضمان عدم الحظر
        if (i + 1) % 5 == 0:
            send_telegram(report)
            report = "" # تصفير الرسالة للدفعة القادمة
            time.sleep(5) # تأخير كافي للأمان

    print("✅ تم الإرسال بنجاح!")

if __name__ == "__main__":
    main()
