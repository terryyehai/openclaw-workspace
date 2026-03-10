#!/usr/bin/env python3
"""
虛擬股票投資策略
趨勢追蹤策略：MA20 / MA60
"""

import yfinance as yf
import sqlite3
from datetime import datetime
import requests

DB_PATH = "/home/terry/.openclaw/workspace-dev/stock-bot/investment.db"
BOT_TOKEN = "8585809641:AAFbfI-CIIigP7Zd0bsemeOdfPNa0y8qHyA"
CHAT_ID = "6490946430"

# 追蹤股票
STOCKS = [
    "2330.TW",  # 台積電
    "0050.TW",  # 元大台灣50
    "006208.TW", # 富邦台灣500
    "2317.TW",  # 鴻海
    "2454.TW",  # 聯發科
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS portfolio (id INTEGER PRIMARY KEY, symbol TEXT, name TEXT, shares INTEGER, avg_price REAL, updated TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cash_log (id INTEGER PRIMARY KEY, date TEXT, action TEXT, amount REAL, balance REAL)''')
    conn.commit()
    conn.close()

def get_ma(symbol, period="20d"):
    """取得移動平均"""
    try:
        df = yf.download(symbol, period=f"{period}y", interval="1d", progress=False)
        if len(df) > 0:
            mean_val = df['Close'].mean()
            # Handle Series result
            if hasattr(mean_val, 'item'):
                return mean_val.item()
            return float(mean_val)
    except Exception as e:
        print(f"Error getting MA for {symbol}: {e}")
    return None

def analyze_stock(symbol):
    """分析股票趨勢"""
    ma20 = get_ma(symbol, 20)
    ma60 = get_ma(symbol, 60)
    
    if ma20 and ma60:
        trend = "上漲" if ma20 > ma60 else "下跌"
        return {"ma20": ma20, "ma60": ma60, "trend": trend}
    return None

def generate_report():
    report = []
    report.append("=" * 50)
    report.append("📈 股票策略分析")
    report.append("=" * 50)
    report.append("")
    
    for symbol in STOCKS:
        analysis = analyze_stock(symbol)
        if analysis:
            report.append(f"📊 {symbol}")
            report.append(f"   MA20: ${analysis['ma20']:.2f}")
            report.append(f"   MA60: ${analysis['ma60']:.2f}")
            report.append(f"   趨勢: {analysis['trend']}")
            report.append("")
    
    report.append("=" * 50)
    report.append(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 50)
    return "\n".join(report)

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def trade():
    """執行交易邏輯"""
    print("執行虛擬交易...")
    report = generate_report()
    print(report)
    send_to_telegram(report)

if __name__ == "__main__":
    init_db()
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "trade":
        trade()
    else:
        print(generate_report())
