import os
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# جلب التوكن والمعلومات من متغيرة البيئة (Environment Variables)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# دالة لجلب البيانات من منصة OKX
def get_okx_volume():
    url = "https://www.okx.com/api/v5/market/tickers?instType=SPOT"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("code") == "0":
            tickers = data.get("data", [])
            # ترتيب العملات حسب حجم التداول في 24 ساعة
            sorted_tickers = sorted(
                tickers, 
                key=lambda x: float(x.get("volCcy24h", 0)), 
                reverse=True
            )
            top_5 = sorted_tickers[:5]
            
            msg = "📊 **أعلى 5 عملات من حيث حجم التداول على OKX:**\n\n"
            for t in top_5:
                symbol = t.get("instId")
                price = t.get("last")
                vol = float(t.get("volCcy24h", 0))
                msg += f"🔹 **{symbol}**\nSعر: `{price}`$\nحجم التداول: `{vol:,.2f}`$\n\n"
            return msg
        else:
            return "❌ تعذر جلب البيانات من منصة OKX."
    except Exception as e:
        return f"⚠️ حدث خطأ أثناء جلب البيانات: {str(e)}"

# دالة الأوامر /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "أهلاً بك في بوت متابعة أحجام التداول على OKX! 🚀\n\n"
        "الأوامر المتاحة:\n"
        "/volume - عرض أعلى العملات في حجم التداول الان"
    )
    await update.message.reply_text(welcome_text)

# دالة الأمر /volume
async def volume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ جاري جلب البيانات من منصة OKX...")
    result = get_okx_volume()
    await update.message.reply_text(result, parse_mode="Markdown")

if __name__ == "__main__":
    if not TELEGRAM_TOKEN:
        print("خطأ: لم يتم ضبط TELEGRAM_TOKEN!")
        exit(1)
        
    print("جاري تشغيل البوت...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("volume", volume_command))
    
    app.run_polling()
