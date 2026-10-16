import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# تفعيل نظام السجلات لمتابعة حالة البوت
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# إعدادات البوت والمالك
TOKEN = "8750644059:AAEA-loCMcUkGH_EU-Zd334E7NikGI0KOfs"
OWNER_ID = 8201127054

# قاعدة بيانات مؤقتة لتخزين بطاقات الاستذكار
user_flashcards = {}

# قاموس طبي مدمج للمصطلحات (يمكنك إضافة أو تعديل ما تحتاجه هنا)
medical_dictionary = {
    "obesity": {
        "en": "Excess body fat accumulation affecting health",
        "ar": "السمنة / تراكم الدهون المفرط",
    },
    "diabetes": {
        "en": "A metabolic disease causing high blood sugar",
        "ar": "مرض السكري",
    },
    "hypertension": {
        "en": "Condition in which blood pressure is persistently elevated",
        "ar": "ارتفاع ضغط الدم",
    },
    "arthritis": {
        "en": "Inflammation of one or more joints causing pain and stiffness",
        "ar": "التهاب المفاصل",
    },
    "metabolism": {
        "en": (
            "The chemical processes that occur within a living organism to"
            " maintain life"
        ),
        "ar": "عملية الأيض / التمثيل الغذائي",
    },
    "dieting": {
        "en": "Restricting food intake to lose weight or for medical reasons",
        "ar": "اتباع نظام غذائي / حمية",
    },
    "treatment": {
        "en": "Medical care given to a patient for an illness or injury",
        "ar": "العلاج الطبي",
    },
    "patient": {
        "en": "A person receiving medical treatment",
        "ar": "مريض",
    },
    "inflammation": {
        "en": (
            "A localized physical condition in which part of the body becomes"
            " reddened, swollen, hot, and often painful"
        ),
        "ar": "التهاب",
    },
    "symptoms": {
        "en": (
            "A physical or mental feature which is regarded as indicating a"
            " condition of disease"
        ),
        "ar": "أعراض المرض",
    },
}


# 1. أمر البدء (Start)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  # حماية البوت ليعمل معك خصيصاً بناءً على الآي دي الخاص بك
  if user_id != OWNER_ID:
    await update.message.reply_text("عذراً، هذا البوت مخصص للاستخدام الخاص.")
    return

  await update.message.reply_text(
      "أهلاً بك يا دكتور! 🩺✨\n\n"
      "قم بإرسال أو لصق أي نص أو شيت طبي هنا، وسأقوم فوراً بتحويله إلى أزرار"
      " تفاعلية:\n"
      "1️⃣ انقر على أي كلمة لعرض معناها الإنجليزي وترجمتها العربية.\n"
      "2️⃣ أضفها إلى قائمة الاستذكار الخاصة بك.\n"
      "3️⃣ تصفح قائمة استذكارك في أي وقت للمراجعة!"
  )


# 2. استقبال الشيت أو النص وعرضه كأزرار تفاعلية
async def handle_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  if user_id != OWNER_ID:
    return

  text = update.message.text
  words = text.
