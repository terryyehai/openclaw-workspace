#!/usr/bin/env python3
"""
股票收益追蹤系統
"""

import yfinance as yf
from datetime import datetime
import sqlite3

DB_PATH = "/home/terry/.openclaw/workspace-dev/stock-bot/earnings.db"
BOT_TOKEN = "8585809641:AAFbfI-CIIigP7Zd0bsemeOdfPNa0y8qHyA"
CHAT_ID = "6490946430"

STOCKS = [
    {"symbol": "00955.TWO", "name": "中信日本ETF", "sector": "ETF"},
    {"symbol": "0050.TW", "name": "元大台灣50", "sector": "ETF"},
    {"symbol": "006208.TW", "name": "富邦台灣500", "sector": "ETF"},
    {"symbol": "009816.TW", "name": "元大台灣高股息", "sector": "ETF"},
    {"symbol": "00919.TW", "name": "統一台灣高股息精選", "sector": "ETF"},
    {"symbol": "2330.TW", "name": "台積電", "sector": "半導體"},
    {"symbol": "2317.TW", "name": "鴻海", "sector": "電子"},
    {"symbol": "2454.TW", "name": "聯發科", "sector": "半導體"},
    {"symbol": "AAPL", "name": "蘋果", "sector": "科技"},
    {"symbol": "NVDA", "name": "輝達", "sector": "AI/晶片"},
    {"symbol": "MSFT", "name": "微軟", "sector": "科技"},
    {"symbol": "GOOGL", "name": "Google", "sector": "科技"},
    {"symbol": "TSLA", "name": "特斯拉", "sector": "電動車"},
    {"symbol": "AMD", "name": "超微", "sector": "AI/晶片"},
    {"symbol": "META", "name": "Meta", "sector": "社群"},
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS earnings (id INTEGER PRIMARY KEY, symbol TEXT, name TEXT, earnings_date TEXT, estimated_eps REAL, actual_eps REAL, estimated_revenue REAL, actual_revenue REAL, status TEXT, updated TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY, symbol TEXT, alert_date TEXT, type TEXT, sent INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def generate_report():
    report = []
    report.append("=" * 50)
    report.append("📊 ETF & 股票收益追蹤")
    report.append("=" * 50)
    report.append("")
    
    for stock in STOCKS:
        try:
            ticker = yf.Ticker(stock["symbol"])
            info = ticker.info
            
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            nav = info.get('navPrice')
            fpe = info.get('forwardPE')
            dividend = info.get('dividendYield')
            
            report.append(f"📈 {stock['symbol']} {stock['name']} [{stock['sector']}]")
            report.append(f"   現價: ${price:,.2f}" if price else "   現價: N/A")
            
            # ETF 顯示淨值
            if stock["sector"] == "ETF" and nav and price:
                premium = (price - nav) / nav * 100
                report.append(f"   淨值(NAV): ${nav:,.2f}")
                report.append(f"   溢價: {premium:+.2f}%")
            elif stock["sector"] == "ETF":
                report.append(f"   淨值(NAV): N/A")
            
            report.append(f"   預期本益比: {fpe:.2f}" if fpe else "   預期本益比: N/A")
            report.append(f"   殖利率: {dividend*100:.2f}%" if dividend else "   殖利率: N/A")
            report.append("")
        except Exception as e:
            report.append(f"📈 {stock['symbol']} {stock['name']} - 載入中")
            report.append("")
    
    report.append("=" * 50)
    report.append(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 50)
    return "\n".join(report)

def send_to_telegram(message):
    import urllib.request, urllib.parse
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode())
    urllib.request.urlopen(req)

if __name__ == "__main__":
    init_db()
    report = generate_report()
    print(report)
    send_to_telegram(report)
