# ===================== quran.py =====================
import os
import json
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

SURAH_NAMES = [
    "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة",
    "الأنعام", "الأعراف", "الأنفال", "التوبة", "يونس",
    "هود", "يوسف", "الرعد", "إبراهيم", "الحجر",
    "النحل", "الإسراء", "الكهف", "مريم", "طه",
    "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان",
    "الشعراء", "النمل", "القصص", "العنكبوت", "الروم",
    "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر",
    "يس", "الصافات", "ص", "الزمر", "غافر",
    "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية",
    "الأحقاف", "محمد", "الفتح", "الحجرات", "ق",
    "الذاريات", "الطور", "النجم", "القمر", "الرحمن",
    "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة",
    "الصف", "الجمعة", "المنافقون", "التغابن", "الطلاق",
    "التحريم", "الملك", "القلم", "الحاقة", "المعارج",
    "نوح", "الجن", "المزمل", "المدثر", "القيامة",
    "الإنسان", "المرسلات", "النبأ", "النازعات", "عبس",
    "التكوير", "الانفطار", "المطففين", "الانشقاق", "البروج",
    "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد",
    "الشمس", "الليل", "الضحى", "الشرح", "التين",
    "العلق", "القدر", "البينة", "الزلزلة", "العاديات",
    "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل",
    "قريش", "الماعون", "الكوثر", "الكافرون", "النصر",
    "المسد", "الإخلاص", "الفلق", "الناس"
]

CACHE_DIR = "cache"


def surah_list_keyboard(page=0):
    per_page = 10
    start = page * per_page
    slice_ = SURAH_NAMES[start:start + per_page]

    buttons = [
        [InlineKeyboardButton(f"{start + i + 1}. {name}", callback_data=f"surah_{start + i + 1}")]
        for i, name in enumerate(slice_)
    ]

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("◀️ السابق", callback_data=f"qpage_{page - 1}"))
    if start + per_page < len(SURAH_NAMES):
        nav_row.append(InlineKeyboardButton("التالي ▶️", callback_data=f"qpage_{page + 1}"))
    if nav_row:
        buttons.append(nav_row)

    buttons.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def _cache_path(surah_number: int) -> str:
    return os.path.join(CACHE_DIR, f"{surah_number}.json")


def fetch_surah(surah_number: int):
    # 1) هل السورة محفوظة مسبقًا؟
    path = _cache_path(surah_number)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # 2) غير موجودة، نجلبها من API
    res = requests.get(f"https://api.alquran.cloud/v1/surah/{surah_number}", timeout=10)
    res.raise_for_status()
    data = res.json()["data"]

    # 3) نحفظها للمرة القادمة
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    return data


def build_surah_messages(surah):
    """يقسّم السورة إلى رسائل، كل رسالة تحتوي مجموعة آيات كاملة (لا تقطع آية بالمنتصف)."""
    header = f"📖 سورة {surah['name']}\n\n"
    messages = []
    current = header
    for ayah in surah["ayahs"]:
        line = f"{ayah['text']} ({ayah['numberInSurah']})\n"
        if len(current) + len(line) > 3800:
            messages.append(current)
            current = line
        else:
            current += line
    if current.strip():
        messages.append(current)
    return messages