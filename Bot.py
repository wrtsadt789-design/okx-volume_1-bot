import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# جلب التوكن من متغيرة البيئة
TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! البوت يعمل بنجاح. أرسل /volume لجلب بيانات OKX.")

async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = "https://www.okx.com/api/v5/market/tickers?instType=SPOT"
        response = requests.get(url).json()
        
        if response.get("code") == "0":
            data = response["data"]
            # ترتيب العملات حسب حجم التداول 24 ساعة (volCcy24h)
            sorted_data = sorted(data, key=lambda x: float(x.get("volCcy24h", 0)), reverse=True)[:10]
            
            msg = "🔥 **أعلى 10 عملات من حيث حجم التداول على OKX:**\n\n"
            for item in sorted_data:
                symbol = item["instId"]
                vol = float(item["volCcy24h"])
                last_price = item["last"]
                msg += f"🔹 **{symbol}**: ${vol:,.0f} (السعر: ${last_price})\n"
                
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("حدث خطأ أثناء جلب البيانات من OKX.")
    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")

def main():
    if not TOKEN:
        print("خطأ: لم يتم ضبط TELEGRAM_TOKEN!")
        return

    print("جاري تشغيل البوت...")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("volume", volume))
    
    app.run_polling()

if __name__ == "__main__":
    main()
