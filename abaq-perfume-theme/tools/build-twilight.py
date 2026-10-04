"""Adds the Abaq perfume components and settings to twilight.json (idempotent).
Run from the theme root:  python3 tools/build-twilight.py
"""
import json, uuid

NS = uuid.UUID('6f1c1f7e-3a1b-4c8e-9b7a-abaq00000000'.replace('abaq', 'aba0'))
def key(*parts): return str(uuid.uuid5(NS, '/'.join(parts)))

LINK_SOURCES = [{"label": l, "key": k, "value": k} for l, k in [
    ("منتج", "products"), ("منتجات مع وسم", "products_tags"), ("تصنيف", "categories"), ("ماركة تجارية", "brands"),
    ("صفحة تعريفية", "pages"), ("مقالة", "blog_articles"), ("تصنيف ضمن المدونة", "blog_categories"),
    ("التخفيضات", "offers_link"), ("الماركات التجارية", "brands_link"), ("المدونة", "blog_link"), ("رابط خارجي", "custom")]]

def text(id, label, value=None, ph=None, max=120, desc=None, required=False):
    return {"type": "string", "format": "text", "id": id, "label": label, "icon": "sicon-format-text-alt", "multilanguage": True,
            "value": value, "placeholder": ph, "description": desc, "required": required, "minLength": 0, "maxLength": max}
def area(id, label, value=None, ph=None, max=500, desc=None):
    return {"type": "string", "format": "textarea", "id": id, "label": label, "icon": "sicon-typography", "multilanguage": True,
            "value": value, "placeholder": ph, "description": desc, "required": False, "minLength": 0, "maxLength": max}
def image(id, label, desc, required=False):
    return {"type": "string", "format": "image", "id": id, "label": label, "icon": "sicon-image", "value": None,
            "placeholder": None, "description": desc, "required": required}
def link(id, label, desc=None):
    return {"type": "items", "format": "variable-list", "id": id, "label": label, "icon": "sicon-link", "value": [],
            "description": desc, "required": False, "searchable": True, "source": "custom", "sources": LINK_SOURCES}
def switch(id, label, value, desc=None):
    return {"type": "boolean", "format": "switch", "id": id, "label": label, "icon": "sicon-toggle-off",
            "description": desc, "required": False, "value": value, "selected": value}
def integer(id, label, value, mn, mx, desc=None):
    return {"type": "number", "format": "integer", "id": id, "label": label, "icon": "sicon-pencil-ruler",
            "description": desc, "required": False, "value": value, "minimum": mn, "maximum": mx}
def icon(id, label, value):
    return {"type": "string", "format": "icon", "id": id, "label": label, "icon": "sicon-format-text-alt",
            "value": value, "required": False, "class": "form--inline", "description": None}
def note(id, html):
    return {"type": "static", "format": "description", "id": id, "value": f"<div>{html}</div>"}
def collection(id, label, item_label, fields, value, mn=1, mx=12):
    return {"type": "collection", "format": "collection", "id": id, "label": label, "item_label": item_label,
            "icon": "sicon-list-add", "required": False, "minLength": mn, "maxLength": mx, "value": value, "fields": fields}

MOTION = "الحركة تعمل تلقائياً عند التمرير، وتتوقف عند العملاء اللي مفعّلين خاصية تقليل الحركة في أجهزتهم."

COMPONENTS = [
  {"path": "home.abaq-hero", "icon": "sicon-image", "title": {"ar": "عبق: الواجهة الرئيسية المتحركة", "en": "Abaq: Animated hero"},
   "fields": [
     note("abaq-hero-note", "واجهة فخمة بزجاجة عطر عائمة وبخار عطري متحرك. " + MOTION),
     text("eyebrow", "عنوان صغير", "دار عطور سعودية", "مثال: دار عطور سعودية", 60),
     text("title", "العنوان الرئيسي", "عطرك يحكي عنك قبل ما تتكلم", "كل كلمة تظهر بحركة متتالية", 90),
     area("subtitle", "النص التوضيحي", "تركيبات من العود الكمبودي والورد الطائفي، معتّقة بعناية لتدوم معك من الصبح لين آخر الليل.", None, 220),
     image("image", "صورة زجاجة العطر", "* يفضّل صورة بخلفية شفافة بصيغة WebP أو PNG، المقاس المناسب 600×800 بكسل"),
     image("background", "صورة خلفية (اختياري)", "* المقاس المناسب 1920×1080 بكسل، تظهر بشفافية خفيفة"),
     text("cta_text", "نص الزر الرئيسي", "تسوّق العطور", None, 40), link("cta_url", "رابط الزر الرئيسي"),
     text("cta2_text", "نص الزر الثانوي", "اكتشف عطرك", None, 40), link("cta2_url", "رابط الزر الثانوي"),
     collection("badges", "شارات النوتات العطرية", "شارة",
        [text("badges.text", "النص", None, "مثال: عود كمبودي", 30)],
        [{"badges.text": "عود كمبودي"}, {"badges.text": "ورد طائفي"}, {"badges.text": "عنبر"}, {"badges.text": "مسك أبيض"}], 0, 4),
     switch("light_mode", "خلفية فاتحة بدل الداكنة", False),
     switch("show_mist", "إظهار البخار العطري المتحرك", True),
     switch("show_scroll_hint", "إظهار مؤشر التمرير", True)]},
  {"path": "home.abaq-marquee", "icon": "sicon-list-play", "title": {"ar": "عبق: شريط نصي متحرك", "en": "Abaq: Moving text strip"},
   "fields": [
     note("abaq-marquee-note", "شريط يتحرك باستمرار لعرض العروض أو مميزات المتجر، ويتوقف عند مرور الفأرة."),
     collection("items", "العبارات", "عبارة",
        [text("items.text", "النص", None, "مثال: شحن مجاني فوق 300 ريال", 60), icon("items.icon", "الأيقونة", "sicon-star2")],
        [{"items.text": "شحن مجاني للطلبات فوق 300 ريال", "items.icon": "sicon-shipping-fast"},
         {"items.text": "عينة مجانية مع كل طلب", "items.icon": "sicon-gift-sharing"},
         {"items.text": "عطور أصلية 100٪", "items.icon": "sicon-award-ribbon"},
         {"items.text": "تغليف هدايا فاخر", "items.icon": "sicon-star2"}], 1, 10),
     integer("speed", "مدة الدورة الكاملة بالثواني", 30, 10, 90, "كل ما زاد الرقم صارت الحركة أبطأ"),
     switch("reverse", "عكس اتجاه الحركة", False),
     switch("pause_hover", "إيقاف الحركة عند مرور الفأرة", True),
     switch("light_mode", "شريط فاتح بدل الداكن", False)]},
  {"path": "home.abaq-families", "icon": "sicon-layout-grid-rearrange", "title": {"ar": "عبق: عائلات العطور", "en": "Abaq: Scent families"},
   "fields": [
     note("abaq-families-note", "بطاقات تساعد العميل يختار حسب ذوقه: عود، ورد، عنبر، فريش... كل بطاقة تربطها بتصنيف."),
     text("title", "العنوان", "اختر العائلة اللي تشبهك", None, 80),
     area("description", "الوصف", "كل عائلة لها شخصية. اختر اللي تحس إنها تمثّلك، ونرشّح لك أنسب العطور.", None, 250),
     collection("items", "العائلات", "عائلة", [
        text("items.name", "اسم العائلة", None, "مثال: العود", 40, required=True),
        area("items.description", "وصف قصير", None, None, 140),
        image("items.image", "الصورة", "* المقاس المناسب 600×700 بكسل"),
        text("items.tag", "شارة (اختياري)", None, "مثال: الأكثر مبيعاً", 24),
        link("items.url", "الرابط")],
        [{"items.name": "العود", "items.description": "دافئ وعميق، للحضور اللي ما يُنسى.", "items.tag": "الأكثر مبيعاً"},
         {"items.name": "الورد", "items.description": "ناعم وأنيق، من ورد الطائف."},
         {"items.name": "العنبر", "items.description": "حلو ودافئ، مثالي للمساء."},
         {"items.name": "الفريش", "items.description": "منعش وخفيف لأيام الصيف."}], 1, 8),
     switch("tilt", "حركة ميلان ثلاثية الأبعاد عند مرور الفأرة", True)]},
  {"path": "home.abaq-notes", "icon": "sicon-list", "title": {"ar": "عبق: الهرم العطري", "en": "Abaq: Fragrance pyramid"},
   "fields": [
     note("abaq-notes-note", "يعرض مكونات عطر مميز على ثلاث طبقات تظهر بالتتابع أثناء التمرير. افصل بين النوتات بفاصلة."),
     text("title", "العنوان", "رحلة العطر على بشرتك", None, 80),
     area("description", "الوصف", "من أول رشة لين آخر الليل، كل طبقة تكشف لك جانب جديد من العطر.", None, 250),
     image("image", "صورة العطر", "* يفضّل خلفية شفافة، المقاس المناسب 600×800 بكسل"),
     text("top_label", "عنوان الطبقة العليا", None, "النوتات العليا", 30), text("top_notes", "النوتات العليا", "برغموت، زعفران، هيل", "مثال: برغموت، زعفران", 160),
     text("heart_label", "عنوان طبقة القلب", None, "نوتات القلب", 30), text("heart_notes", "نوتات القلب", "ورد طائفي، ياسمين، باتشولي", None, 160),
     text("base_label", "عنوان الطبقة الأساسية", None, "النوتات الأساسية", 30), text("base_notes", "النوتات الأساسية", "عود كمبودي، عنبر، مسك، صندل", None, 160),
     text("cta_text", "نص الزر", "اطلب العطر", None, 40), link("cta_url", "رابط الزر"),
     switch("image_first", "إظهار الصورة أولاً", False)]},
  {"path": "home.abaq-products", "icon": "sicon-list-play", "title": {"ar": "عبق: منتجات مختارة", "en": "Abaq: Featured perfumes"},
   "fields": [
     note("abaq-products-note", "سلايدر منتجات بتصميم عبق. إذا ما اخترت منتجات، يعرض أحدث المنتجات تلقائياً."),
     text("title", "العنوان", "الأكثر طلباً هذا الموسم", None, 80),
     area("description", "الوصف", None, "وصف قصير للقسم...", 250),
     {"type": "items", "format": "dropdown-list", "id": "products", "label": "المنتجات", "icon": "sicon-keyboard_arrow_down",
      "description": "اترك الحقل فاضي لعرض أحدث المنتجات", "selected": [], "options": [], "required": False, "multichoice": True,
      "source": "products", "searchable": True, "maxLength": 12, "minLength": 0, "value": []},
     link("display_all_url", "رابط عرض الكل", "عند اختيار رابط فارغ سيتم إخفاء زر 'عرض الكل'"),
     switch("dark_mode", "خلفية داكنة", False)]},
  {"path": "home.abaq-story", "icon": "sicon-newspaper", "title": {"ar": "عبق: قصة العلامة", "en": "Abaq: Brand story"},
   "fields": [
     note("abaq-story-note", "قسم يحكي قصة متجرك مع أرقام تعدّ تلقائياً عند ظهورها، والصورة تنكشف بحركة سينمائية."),
     image("image", "الصورة", "* المقاس المناسب 800×1000 بكسل"),
     text("eyebrow", "عنوان صغير", "قصتنا", None, 40),
     text("title", "العنوان", "صنعة العطر بأصول عريقة", None, 90),
     area("text", "النص", "بدأنا من شغف بسيط: عطر يعيش معك ويذكّرك بأجمل لحظاتك. ننتقي خاماتنا من أفضل المصادر ونعتّقها بصبر، عشان توصلك تجربة تستاهلها.", None, 700),
     collection("stats", "الأرقام", "رقم", [
        integer("stats.number", "الرقم", 0, 0, 10000000),
        text("stats.suffix", "بعد الرقم", None, "مثال: + أو ٪", 6),
        text("stats.label", "الوصف", None, "مثال: عميل سعيد", 40)],
        [{"stats.number": 15, "stats.suffix": "+", "stats.label": "سنة خبرة"},
         {"stats.number": 40, "stats.suffix": "+", "stats.label": "تركيبة عطرية"},
         {"stats.number": 98, "stats.suffix": "٪", "stats.label": "رضا العملاء"}], 0, 4),
     text("cta_text", "نص الزر", "تعرّف علينا", None, 40), link("cta_url", "رابط الزر"),
     switch("image_end", "الصورة في الجهة الثانية", False),
     switch("dark_mode", "خلفية داكنة", True)]},
  {"path": "home.abaq-testimonials", "icon": "sicon-chat-bubbles", "title": {"ar": "عبق: آراء العملاء", "en": "Abaq: Reviews"},
   "fields": [
     note("abaq-testimonials-note", "بطاقات تقييمات أنيقة تظهر بالتتابع، مع اسم العطر اللي اشتراه العميل."),
     text("title", "العنوان", "وش قالوا عن عطورنا", None, 80),
     collection("items", "التقييمات", "تقييم", [
        text("items.name", "اسم العميل", None, None, 40, required=True),
        text("items.city", "المدينة", None, "مثال: الرياض", 30),
        integer("items.stars", "عدد النجوم", 5, 1, 5),
        area("items.text", "نص التقييم", None, None, 300),
        text("items.scent", "العطر اللي اشتراه", None, "مثال: عود ملكي", 40)],
        [{"items.name": "نورة", "items.city": "الرياض", "items.stars": 5, "items.text": "الثبات خيالي، رشيته الصبح وللحين ريحته موجودة. التغليف فخم ويصلح هدية.", "items.scent": "عود ملكي"},
         {"items.name": "عبدالله", "items.city": "جدة", "items.stars": 5, "items.text": "أخذت العينات قبل وطلبت الحجم الكبير، كل اللي حولي يسألوني عن اسمه.", "items.scent": "عنبر الليل"},
         {"items.name": "سارة", "items.city": "الدمام", "items.stars": 5, "items.text": "الورد الطائفي عندهم غير، ناعم ومو ثقيل. والتوصيل كان سريع.", "items.scent": "ورد الطائف"}], 1, 12)]},
  {"path": "home.abaq-features", "icon": "sicon-award-ribbon", "title": {"ar": "عبق: مميزات المتجر", "en": "Abaq: Store features"},
   "fields": [
     note("abaq-features-note", "شريط ثقة يوضح أهم مميزات متجرك."),
     collection("items", "المميزات", "ميزة", [
        icon("items.icon", "الأيقونة", "sicon-star2"),
        text("items.title", "العنوان", None, None, 40, required=True),
        text("items.text", "الوصف", None, None, 90)],
        [{"items.icon": "sicon-award-ribbon", "items.title": "أصلي 100٪", "items.text": "نضمن لك أصالة كل عطر"},
         {"items.icon": "sicon-shipping-fast", "items.title": "شحن سريع", "items.text": "يوصلك خلال 1-3 أيام"},
         {"items.icon": "sicon-gift-sharing", "items.title": "تغليف هدايا", "items.text": "تغليف فاخر مع بطاقة إهداء"},
         {"items.icon": "sicon-refund", "items.title": "استبدال سهل", "items.text": "خلال 7 أيام من الاستلام"}], 1, 6),
     switch("dark_mode", "خلفية داكنة", False)]},
]

SETTINGS = [
  {"type": "static", "format": "line", "id": "abaq-static-line"},
  {"type": "static", "format": "title", "id": "abaq-static-title", "value": "إعدادات عبق للحركة والتصميم"},
  {"id": "abaq_motion_level", "type": "items", "format": "dropdown-list", "label": "مستوى الحركة في المتجر", "icon": "sicon-list",
   "description": "الحركة تحترم تلقائياً إعداد تقليل الحركة في أجهزة العملاء", "source": "Manual", "required": True,
   "options": [{"label": "كاملة (حركة عند التمرير + حركات مستمرة)", "value": "full", "key": key('opt', 'full')},
               {"label": "خفيفة (حركة عند التمرير فقط)", "value": "subtle", "key": key('opt', 'subtle')},
               {"label": "بدون حركة", "value": "off", "key": key('opt', 'off')}],
   "selected": [{"label": "كاملة (حركة عند التمرير + حركات مستمرة)", "value": "full", "key": key('opt', 'full')}]},
  {"type": "boolean", "format": "switch", "id": "abaq_page_transitions", "label": "انتقال ناعم بين الصفحات", "icon": "sicon-toggle-off",
   "description": "يستخدم تقنية View Transitions الحديثة في المتصفحات الداعمة", "required": False, "value": True, "selected": True},
  {"type": "boolean", "format": "switch", "id": "abaq_heading_font", "label": "خط عبق الكلاسيكي للعناوين (أميري)", "icon": "sicon-toggle-off",
   "description": "خط عربي كلاسيكي للعناوين فقط، ويبقى خط المتجر لباقي النصوص", "required": False, "value": True, "selected": True},
  {"type": "boolean", "format": "switch", "id": "abaq_skin", "label": "تطبيق ستايل عبق على الهيدر والفوتر وبطاقات المنتجات", "icon": "sicon-toggle-off",
   "description": None, "required": False, "value": True, "selected": True},
]

d = json.load(open('twilight.json'))
d['name'] = {"ar": "عبق", "en": "Abaq"}
d['description'] = {"ar": "ثيم فاخر لمتاجر العطور والبخور والعود، بحركات سينمائية عند التمرير وأقسام مصممة لعرض النوتات والعائلات العطرية.",
                    "en": "A luxury theme for perfume, oud and incense stores, with cinematic scroll animations and sections built for scent notes and fragrance families."}
d['repository'] = ""
d['author_email'] = ""
d['support_url'] = ""

paths = {c['path'] for c in COMPONENTS}
d['components'] = [c for c in d['components'] if c['path'] not in paths]
for c in d['components']:
    c['is_default'] = False  # Raed blocks stay available but our sections lead the default home page
new = []
for c in COMPONENTS:
    for f in c['fields']:
        f.setdefault('key', key(c['path'], f['id']))
        for sub in f.get('fields', []): sub.setdefault('key', key(c['path'], sub['id']))
    new.append({"key": key(c['path']), "title": c['title'], "icon": c['icon'], "path": c['path'], "is_default": True, "fields": c['fields']})
d['components'] = new + d['components']

ids = {s['id'] for s in SETTINGS}
d['settings'] = [s for s in d['settings'] if s['id'] not in ids] + SETTINGS
json.dump(d, open('twilight.json', 'w'), ensure_ascii=False, indent=4)
open('twilight.json', 'a').write('\n')
print(len(d['components']), 'components,', len(d['settings']), 'settings')
