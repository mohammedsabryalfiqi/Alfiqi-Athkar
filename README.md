# ذكر 🕌 — بوت تيليجرام إسلامي

بوت تيليجرام يوفر أذكار الصباح والمساء، القرآن الكريم كاملًا، وعدّاد تسبيح تفاعلي.

## الميزات
- 🌅 أذكار الصباح
- 🌙 أذكار المساء
- 📖 القرآن الكريم (114 سورة، يُجلب النص عبر API خارجي مع تخزين مؤقت محلي)
- 📿 عدّاد تسبيح (الحمد لله / سبحان الله / الله أكبر) بعدادات منفصلة

## التقنيات المستخدمة
- Python 3
- python-telegram-bot
- requests
- python-dotenv
- Telegram Bot API + alquran.cloud API

## التشغيل محليًا

```bash
git clone https://github.com/mahmoudbm77/zekr-telegram-bot.git
cd zekr-telegram-bot
python -m venv venv
venv\Scripts\activate      # على ويندوز
pip install -r requirements.txt
```

أنشئ ملف `.env` وضع فيه:


شغّل البوت:
```bash
python bot.py
```s

## البنية
- `bot.py` — نقطة انطلاق البوت والمعالجات (handlers)
- `adhkar.py` — بيانات أذكار الصباح والمساء
- `quran.py` — منطق جلب السور وعرضها، مع تخزين مؤقت في `cache/`

## ملاحظات
- التوكن سري ولا يُرفع أبدًا (موجود في `.env` المُستثنى عبر `.gitignore`)
- مجلد `cache/` يُنشأ تلقائيًا ولا يُرفع لـ GitHub