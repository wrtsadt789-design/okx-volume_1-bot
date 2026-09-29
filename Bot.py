import time
import threading
import requests
import telebot

TOKEN = "8698370133:AAH6yRXtsjTorCCx5iT0PYRjVUoJ_NngOx8"

# ضع هنا Chat ID الخاص بك أو بالقناة/المجموعة
CHAT_ID = "ضع_هنا_CHAT_ID" 

bot = telebot.TeleBot(TOKEN)

# **حل مشكلة Webhook Conflict**: إزالة أي ويب هوك نشط قبل البدء
try:
    bot.remove_webhook()
except Exception as e:
    print(f"إشعارات الـ Webhook: {e}")

# متغيرات لحفظ القراءات السابقة
previous_vol_usd = None
previous_price = None

def get_btc_volume_and_analysis():
    global previous_vol_usd, previous_price
    try:
        url = "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT"
        response = requests.get(url, timeout=10)
        res_data = response.json()
        
        if res_data.get("code") == "0" and len(res_data["data"]) > 0:
            ticker = res_data["data"][0]
            
            current_price = float(ticker.get("last", 0))
            high_24h = float(ticker.get("high24h", 0))
            low_24h = float(ticker.get("low24h", 0))
            vol_24h_usd = float(ticker.get("volCcy24h", 0))
            vol_24h_btc = float(ticker.get("vol24h", 0))
            
            # 1. تحديد حالة السوق اللحظية
            price_range = high_24h - low_24h
            if price_range > 0:
                price_position = (current_price - low_24h) / price_range
                if price_position > 0.7:
                    market_status = "🟢 صاعد قوياً (Bullish)"
                elif price_position < 0.3:
                    market_status = "🔴 هابط قوياً (Bearish)"
                else:
                    market_status = "🟡 متذبذب / جانبي (Neutral)"
            else:
                market_status = "🟡 غير محدد"

            # 2. حساب الفوليوم الصافي للـ 10 دقائق وتوقع حركة 0.1%
            diff_text = ""
            prediction_text = ""
            
            # حساب قيمة حركة 0.1% من السعر الحالي
            price_move_01 = current_price * 0.001
            
            if previous_vol_usd is not None and previous_price is not None:
                net_usd_10m = vol_24h_usd - previous_vol_usd
                price_change_10m = current_price - previous_price
                
                if net_usd_10m >= 0:
                    diff_text = f"📈 **صافي الفوليوم (آخر 10 دقائق):** +${net_usd_10m:,.2f}\n"
                else:
                    diff_text = f"📉 **صافي الفوليوم (آخر 10 دقائق):** -${abs(net_usd_10m):,.2f}\n"

                # تقدير كمية الفوليوم المطلوبة لتحريك السعر بنسبة 0.1%
                if abs(price_change_10m) > 0 and abs(net_usd_10m) > 0:
                    vol_per_dollar_move = abs(net_usd_10m) / abs(price_change_10m)
                    needed_vol_for_01 = vol_per_dollar_move * price_move_01
                    
                    if net_usd_10m > 0:
                        prediction_text = f"🎯 **احتمالية الحركة (0.1% = ${price_move_01:,.2f}):**\nدخول فوليوم شرائي بقيمة **${needed_vol_for_01:,.0f}** يتوقع أن يرفع السعر إلى **${current_price + price_move_01:,.2f}**\n"
                    else:
                        prediction_text = f"🎯 **احتمالية الحركة (0.1% = ${price_move_01:,.2f}):**\nخروج فوليوم بيعي بقيمة **${needed_vol_for_01:,.0f}** يتوقع أن يخفض السعر إلى **${current_price - price_move_01:,.2f}**\n"
                else:
                    approx_needed_vol = vol_24h_usd * 0.0005
                    prediction_text = f"🎯 **توقع الحركة (0.1% = ${price_move_01:,.2f}):**\nيحتاج السعر لضخ/سحب فوليوم يقارب **${approx_needed_vol:,.0f}** للتحرك بنسبة 0.1%\n"

            # تحديث القراءات السابقة
            previous_vol_usd = vol_24h_usd
            previous_price = current_price

            text = (
                f"⚡ **تقرير BTC/USDT الحصري (كل 10 دقائق)**\n\n"
                f"📊 **حالة السوق:** {market_status}\n"
                f"💰 **السعر الحالي:** ${current_price:,.2f}\n\n"
                f"{diff_text}"
                f"{prediction_text}\n"
                f"📈 **إجمالي الفوليوم (24h):** ${vol_24h_usd:,.0f}\n"
                f"🪙 **إجمالي البتكوين (24h):** {vol_24h_btc:,.2f} BTC"
            )
            return text
        return "خطأ في استجابة API الخاصة بـ OKX."
    except Exception as e:
        return f"حدث خطأ أثناء جلب البيانات: {str(e)}"

# دالة التكرار كل 10 دقائق (600 ثانية)
def auto_send_btc_analysis():
    while True:
        if CHAT_ID != "ضع_هنا_CHAT_ID":
            try:
                msg = get_btc_volume_and_analysis()
                bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
            except Exception as e:
                print(f"خطأ في الإرسال التلقائي: {e}")
        time.sleep(600)  # 10 دقائق

# تشغيل التكرار التلقائي في الخلفية
threading.Thread(target=auto_send_btc_analysis, daemon=True).start()

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "أهلاً بك! البوت يقوم بتحليل حركة فوليوم BTC/USDT وتوقع تأثير نسبة 0.1% على السعر كل 10 دقائق تلقائياً. استخدم /volume للحصول على التقرير فوراً.")

@bot.message_handler(commands=['volume'])
def fetch_btc_volume(message):
    msg = get_btc_volume_and_analysis()
    bot.reply_to(message, msg, parse_mode="Markdown")

if __name__ == "__main__":
    print("جاري تشغيل بوت التحليل والتوقع لحركة البيتكوين...")
    bot.infinity_polling(skip_pending=True)
