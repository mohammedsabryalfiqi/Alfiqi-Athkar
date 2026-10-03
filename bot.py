# ===================== bot.py =====================
import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

import adhkar
from quran import surah_list_keyboard, fetch_surah, build_surah_messages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise SystemExit("❌ خطأ: BOT_TOKEN غير موجود. تأكد من ملف .env وأنه يحتوي على السطر: BOT_TOKEN=...")


def main_menu():
    keyboard = [
        [InlineKeyboardButton("🌅 أذكار الصباح", callback_data="morning")],
        [InlineKeyboardButton("🌙 أذكار المساء", callback_data="evening")],
        [InlineKeyboardButton("📖 القرآن الكريم", callback_data="quran_menu")],
        [InlineKeyboardButton("📿 التسبيح", callback_data="tasbih_start")]
    ]
    return InlineKeyboardMarkup(keyboard)


def tasbih_keyboard(counts):
    keyboard = [
        [InlineKeyboardButton(f"الحمد لله 📿 ({counts['hamd']})", callback_data="tasbih_hamd")],
        [InlineKeyboardButton(f"سبحان الله 📿 ({counts['subhan']})", callback_data="tasbih_subhan")],
        [InlineKeyboardButton(f"الله أكبر 📿 ({counts['akbar']})", callback_data="tasbih_akbar")],
        [InlineKeyboardButton("🔄 إعادة العداد", callback_data="tasbih_reset")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "السلام عليكم ورحمة الله، أهلًا بك في بوت ذكر 🕌\nاختر من القائمة:",
        reply_markup=main_menu()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 كيفية استخدام بوت ذكر:\n\n"
        "/start - عرض القائمة الرئيسية\n"
        "/help - عرض هذه الرسالة\n\n"
        "🌅 أذكار الصباح وأذكار المساء: اضغط الزر وستصلك الأذكار كاملة.\n"
        "📖 القرآن الكريم: تصفح السور عبر الصفحات، واضغط على أي سورة لقراءتها.\n"
        "📿 التسبيح: اضغط أي زر وسيزيد عدّاده الخاص مع كل ضغطة."
    )
    await update.message.reply_text(text)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "morning":
        for dhikr in adhkar.MORNING:
            await query.message.reply_text(dhikr)
            await asyncio.sleep(0.3)

    elif query.data == "evening":
        for dhikr in adhkar.EVENING:
            await query.message.reply_text(dhikr)
            await asyncio.sleep(0.3)

    elif query.data == "main_menu":
        await query.message.reply_text("اختر من القائمة:", reply_markup=main_menu())

    elif query.data == "quran_menu":
        await query.message.reply_text("اختر السورة:", reply_markup=surah_list_keyboard(0))

    elif query.data.startswith("qpage_"):
        page = int(query.data.split("_")[1])
        await query.edit_message_reply_markup(reply_markup=surah_list_keyboard(page))

    elif query.data.startswith("surah_"):
        num = int(query.data.split("_")[1])
        try:
            surah = fetch_surah(num)
            messages = build_surah_messages(surah)
            for msg in messages:
                await query.message.reply_text(msg)
                await asyncio.sleep(0.3)
        except Exception as e:
            logger.error(f"فشل جلب السورة {num}: {e}")
            await query.message.reply_text("⚠️ حدث خطأ أثناء تحميل السورة. تأكد من اتصالك بالإنترنت وحاول مرة أخرى.")

    elif query.data == "tasbih_start":
        context.user_data["tasbih"] = {"hamd": 0, "subhan": 0, "akbar": 0}
        await query.message.reply_text(
            "اضغط الزر للتسبيح:",
            reply_markup=tasbih_keyboard(context.user_data["tasbih"])
        )

    elif query.data in ("tasbih_hamd", "tasbih_subhan", "tasbih_akbar"):
        key = query.data.replace("tasbih_", "")  # hamd / subhan / akbar
        counts = context.user_data.setdefault("tasbih", {"hamd": 0, "subhan": 0, "akbar": 0})
        counts[key] += 1
        try:
            await query.edit_message_reply_markup(reply_markup=tasbih_keyboard(counts))
        except Exception:
            pass

    elif query.data == "tasbih_reset":
        context.user_data["tasbih"] = {"hamd": 0, "subhan": 0, "akbar": 0}
        await query.edit_message_reply_markup(reply_markup=tasbih_keyboard(context.user_data["tasbih"]))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"حدث خطأ غير متوقع: {context.error}")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)
    print("البوت يعمل الآن ✅")
    app.run_polling()


if __name__ == "__main__":
    main()