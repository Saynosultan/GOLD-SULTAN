import time
import requests
import yfinance as yf
import pandas as pd

# 🔑 ضع التوكين والـ Chat ID الخاصين بك هنا
TELEGRAM_TOKEN = "8403169681:AAHbp8KvxKM8eb_cfBMEPfq5XkG7cyGay5Y"
TELEGRAM_CHAT_ID = "6473128632"

def send_telegram_msg(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"خطأ في إرسال تلجرام: {e}")

def check_market():
    gold = yf.download('GC=F', period='5d', interval='15m', auto_adjust=True)
    if isinstance(gold.columns, pd.MultiIndex):
        gold.columns = gold.columns.get_level_values(0)
    
    gold = gold[['Open', 'High', 'Low', 'Close']].dropna()
    if len(gold) < 20:
        return

    close = gold['Close']
    sma = close.rolling(20).mean()
    std = close.rolling(20).std()
    bb_lower = sma - (2.0 * std)
    bb_upper = sma + (2.0 * std)

    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    c_curr, o_curr = gold['Close'].iloc[-1], gold['Open'].iloc[-1]
    h_curr, l_curr = gold['High'].iloc[-1], gold['Low'].iloc[-1]
    c_prev, o_prev = gold['Close'].iloc[-2], gold['Open'].iloc[-2]

    buy_signal = (c_prev < o_prev) and (c_curr > o_curr) and (o_curr <= c_prev) and (c_curr >= o_prev) and (l_curr <= bb_lower.iloc[-1]) and (rsi.iloc[-1] < 50)
    sell_signal = (c_prev > o_prev) and (c_curr < o_curr) and (o_curr >= c_prev) and (c_curr <= o_prev) and (h_curr >= bb_upper.iloc[-1]) and (rsi.iloc[-1] > 50)

    risk_usd = 1000.0

    if buy_signal:
        sl = l_curr - 2.5
        risk_dist = c_curr - sl
        lot = risk_usd / (risk_dist * 100)
        tp1 = c_curr + (1.5 * risk_dist)
        tp2 = c_curr + (2.0 * risk_dist)
        msg = f"🟢 *إشارة شراء ذهب (BUY)*\n📍 سعر الدخول: ${c_curr:.2f}\n🛑 الستوب: ${sl:.2f}\n🎯 الهدف 1: ${tp1:.2f}\n🚀 الهدف 2: ${tp2:.2f}\n💼 اللوت: {lot:.2f}"
        send_telegram_msg(msg)

    elif sell_signal:
        sl = h_curr + 2.5
        risk_dist = sl - c_curr
        lot = risk_usd / (risk_dist * 100)
        tp1 = c_curr - (1.5 * risk_dist)
        tp2 = c_curr - (2.0 * risk_dist)
        msg = f"🔴 *إشارة بيع ذهب (SELL)*\n📍 سعر الدخول: ${c_curr:.2f}\n🛑 الستوب: ${sl:.2f}\n🎯 الهدف 1: ${tp1:.2f}\n🚀 الهدف 2: ${tp2:.2f}\n💼 اللوت: {lot:.2f}"
        send_telegram_msg(msg)

print("🚀 تم تشغيل البوت على الخادم السحابي...")
while True:
    try:
        check_market()
    except Exception as e:
        print(f"حدث خطأ: {e}")
    time.sleep(900)
