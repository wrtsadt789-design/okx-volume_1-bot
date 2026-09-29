import os
import requests
import telebot

TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    print("خطأ: لم يتم ضبط TELEGRAM_TOKEN!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "أهلاً بك! البوت يعمل بنجاح. أرسل /volume لجلب بيانات OKX.")

@bot.message_handler(commands=['volume'])
def volume(message):
    try:
        url = "https://www.okx.com/api/v5/market/tickers?instType=SPOT"
        res = requests.get(url).json()
        if res.get("code") == "0":
            data = sorted(res["data"], key=lambda x: float(x.get("volCcy24h", 0)), reverse=True)[:10]
            msg = "🔥 **أعلى 10 عملات بحجم التداول على OKX:**\n\n"
            for item in data:
                msg += f"🔹 **{item['instId']}**: ${float(item['volCcy24h']):,.0f} (السعر: ${item['last']})\n"
            bot.reply_to(message, msg, parse_mode="Markdown")
        else:
            bot.reply_to(message, "خطأ في جلب البيانات من OKX.")
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ: {str(e)}")

print("جاري تشغيل البوت...")
bot.infinity_polling()
