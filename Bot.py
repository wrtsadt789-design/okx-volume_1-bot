
import os
import requests
import telebot

# جلب توكن البوت من المتغيرات
TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    print("خطأ: لم يتم ضبط TELEGRAM_TOKEN!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! البوت يعمل بنجاح عبر telebot. أرسل /volume لجلب أعلى عملات OKX.")

@bot.message_handler(commands=['volume'])
def get_volume(message):
    try:
        url = "https://www.okx.com/api/v5/market/tickers?instType=SPOT"
        response = requests.get(url).json()
        
        if response.get("code") == "0":
            data = response["data"]
            # ترتيب العملات حسب حجم التداول في 24 ساعة
            sorted_data = sorted(data, key=lambda x: float(x.get("volCcy24h", 0)), reverse=True)[:10]
            
            msg = "🔥 *أعلى 10 عملات حتماً للتداول على OKX:*\n\n"
            for item in sorted_data:
                symbol = item["instId"]
                vol = float(item["volCcy24h"])
                last_price = item["last"]
                msg += f"🔹 *{symbol}*: ${vol:,.0f} (السعر: ${last_price})\n"
                
            bot.reply_to(message, msg, parse_mode="Markdown")
        else:
            bot.reply_to(message, "حدث خطأ في استجابة API الخاصة بـ OKX.")
    except Exception as e:
        bot.reply_to(message, f"خطأ أثناء جلب البيانات: {str(e)}")

print("جاري تشغيل البوت...")
bot.infinity_polling()
