import time
import threading
import requests
import telebot

TOKEN = "8829854527:AAF5SrjntKMn3Lwe1VnjKJYzUpVgmUe6-hQ"
CHAT_ID = "8201127054" 

bot = telebot.TeleBot(TOKEN)

# إزالة أي جلسة أو Webhook قديم
try:
    bot.remove_webhook()
except Exception as e:
    print(f"إشعارات Webhook: {e}")

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

            # 2. حساب الفوليوم الصافي وتحويله لـ BTC
            diff_text = ""
            prediction_text = ""
            
            price_move_01 = current_price * 0.001  # حركة 0.1%
            
            if previous_vol_usd is not None and previous_price is not None:
                net_usd_10m = vol_24h_usd - previous_vol_usd
                net_btc_10m = net_usd_10m / current_price if current_price > 0 else 0
                price_change_10m = current_price - previous_price
                
                if net_usd_10m >= 0:
                    diff_text = f"📈 **صافي الفوليوم (آخر 10 دقائق):**\n🟢 **شرائي:** +${net_usd_10m:,.2f} (يعادل **+{net_btc_10m:,.2f} BTC**)\n"
                else:
                    diff_text = f"📉 **صافي الفوليوم (آخر 10 دقائق):**\n🔴 **بيعي:** -${abs(net_usd_10m):,.2f} (يعادل **-{abs(net_btc_10m):,.2f} BTC**)\n"

                # حساب التوقع بحجم الـ BTC والدولار
                if abs(price_change_10m) > 0 and abs(net_usd_10m) > 0:
                    vol_per_dollar_move = abs(net_usd_10m) / abs(price_change_10m)
                    needed_vol_for_01_usd = vol_per_dollar_move * price_move_01
                    needed_vol_for_01_btc = needed_vol_for_01_usd / current_price
                    
                    if net_usd_10m > 0:
                        prediction_text = (
                            f"🎯 **احتمالية الحركة (0.1% = ${price_move_01:,.2f}):**\n"
                            f"دخول فوليوم شرائي بقيمة **${needed_vol_for_01_usd:,.0f}** (حوالي **{needed_vol_for_01_btc:,.2f} BTC**) "
                            f"يتوقع أن يرفع السعر إلى **${current_price + price_move_01:,.2f}**\n"
                        )
                    else:
                        prediction_text = (
                            f"🎯 **احتمالية الحركة (0.1% = ${price_move_01:,.2f}):**\n"
                            f"خروج فوليوم بيعي بقيمة **${needed_vol_for_01_usd:,.0f}** (حوالي **{needed_vol_for_01_btc:,.2f} BTC**) "
                            f"يتوقع أن يخفض السعر إلى **${current_price - price_move_01:,.2f}**\n"
                        )
                else:
                    approx_needed_vol_usd = vol_24h_usd * 0.0005
                    approx_needed_vol_btc = approx_needed_vol_usd / current_price
                    prediction_text = f"🎯 **توقع الحركة (0.1% = ${price_move_01:,.2f}):**\nيحتاج السعر لضخ/سحب فوليوم يقارب **${approx_needed_vol_usd:,.0f}** (**{approx_needed_vol_btc:,.2f} BTC**) للتحرك بنسبة 0.1%\n"

            previous_vol_usd = vol_24h_usd
            previous_price = current_price

            text = (
                f"⚡ **تقرير BTC/USDT الحصري (كل 10 دقائق)**\n\n"
                f"📊 **حالة السوق:** {market_status}\n"
                f"💰 **السعر الحالي:** ${current_price:,.2f}\n\n"
                f"{diff_text}\n"
                f"{prediction_text}\n"
                f"📈 **إجمالي الفوليوم (24 ساعة):** ${vol_24h_usd:,.0f}\n"
                f"🪙 **إجمالي البيتكوين (24 ساعة):** {vol_24h_btc:,.2f} BTC"
            )
            return text
        return "خطأ في استجابة API الخاصة بـ OKX."
    except Exception as e:
        return f"حدث خطأ أثناء جلب البيانات: {str(e)}"

def auto_send_btc_analysis():
    while True:
        try:
            msg = get_btc_volume_and_analysis()
            bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
        except Exception as e:
            print(f"خطأ في الإرسال التلقائي: {e}")
        time.sleep(600)

threading.Thread(target=auto_send_btc_analysis, daemon=True).start()

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "أهلاً بك! البوت يعمل بنجاح ويرسل التقرير باللغة العربية مع حساب قيمة البيتكوين مباشرة.")

@bot.message_handler(commands=['volume'])
def fetch_btc_volume(message):
    msg = get_btc_volume_and_analysis()
    bot.reply_to(message, msg, parse_mode="Markdown")

if __name__ == "__main__":
    print("جاري تشغيل البوت المحدث...")
    bot.infinity_polling(skip_pending=True)
