#!/usr/bin/env python3
"""
虛擬股票投資系統 - 小蝦理財機器人
"""

import sqlite3
import yfinance as yf
from datetime import datetime

DB_PATH = "/home/terry/.openclaw/workspace-dev/stock-bot/investment.db"
INITIAL_CAPITAL = 100000

STOCK_POOL = [
    {"symbol": "2330.TW", "name": "台積電", "sector": "半導體"},
    {"symbol": "2317.TW", "name": "鴻海", "sector": "電子"},
    {"symbol": "2454.TW", "name": "聯發科", "sector": "半導體"},
    {"symbol": "2603.TW", "name": "長榮", "sector": "航運"},
    {"symbol": "2615.TW", "name": "萬海", "sector": "航運"},
    {"symbol": "2884.TW", "name": "玉山金", "sector": "金融"},
    {"symbol": "2891.TW", "name": "中信金", "sector": "金融"},
    {"symbol": "0050.TW", "name": "元大台灣50", "sector": "ETF"},
    {"symbol": "0056.TW", "name": "元大高股息", "sector": "ETF"},
]

class StockInvestor:
    def __init__(self):
        self.init_database()
        self.load_portfolio()
        
    def init_database(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, symbol TEXT, name TEXT,
            action TEXT, quantity INTEGER, price REAL, total REAL, reason TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS portfolio (
            symbol TEXT PRIMARY KEY, name TEXT, quantity INTEGER, avg_cost REAL, sector TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS cash_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, action TEXT, amount REAL, balance REAL)''')
        
        c.execute("SELECT COUNT(*) FROM cash_log")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO cash_log (timestamp, action, amount, balance) VALUES (?, ?, ?, ?)",
                     (datetime.now().isoformat(), "INITIAL", INITIAL_CAPITAL, INITIAL_CAPITAL))
        
        conn.commit()
        conn.close()
    
    def load_portfolio(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT balance FROM cash_log ORDER BY id DESC LIMIT 1")
        self.cash = c.fetchone()[0]
        
        c.execute("SELECT symbol, name, quantity, avg_cost, sector FROM portfolio WHERE quantity > 0")
        self.positions = {}
        for row in c.fetchall():
            self.positions[row[0]] = {"name": row[1], "quantity": row[2], "avg_cost": row[3], "sector": row[4]}
        conn.close()
    
    def get_stock_price(self, symbol):
        try:
            return yf.Ticker(symbol).info.get('currentPrice') or yf.Ticker(symbol).info.get('regularMarketPrice')
        except:
            return None
    
    def buy(self, symbol, quantity, reason=""):
        price = self.get_stock_price(symbol)
        if not price: return False, "無法獲取價格"
        total = price * quantity
        if total > self.cash: return False, f"現金不足"
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("INSERT INTO trades (timestamp, symbol, name, action, quantity, price, total, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                 (datetime.now().isoformat(), symbol, self.get_stock_name(symbol), "BUY", quantity, price, total, reason))
        
        self.cash -= total
        c.execute("INSERT INTO cash_log (timestamp, action, amount, balance) VALUES (?, ?, ?, ?)",
                 (datetime.now().isoformat(), "BUY", -total, self.cash))
        
        if symbol in self.positions:
            old = self.positions[symbol]
            new_qty = old["quantity"] + quantity
            new_cost = (old["avg_cost"] * old["quantity"] + price * quantity) / new_qty
            c.execute("UPDATE portfolio SET quantity = ?, avg_cost = ? WHERE symbol = ?", (new_qty, new_cost, symbol))
        else:
            stock_info = next((s for s in STOCK_POOL if s["symbol"] == symbol), {})
            c.execute("INSERT INTO portfolio (symbol, name, quantity, avg_cost, sector) VALUES (?, ?, ?, ?, ?)",
                     (symbol, stock_info.get("name", ""), quantity, price, stock_info.get("sector", "")))
        
        conn.commit()
        conn.close()
        self.load_portfolio()
        return True, f"買入 {symbol} x{quantity} @ ${price:,.2f}"
    
    def sell(self, symbol, quantity, reason=""):
        if symbol not in self.positions: return False, "沒有持股"
        pos = self.positions[symbol]
        if pos["quantity"] < quantity: return False, "持股不足"
        
        price = self.get_stock_price(symbol)
        if not price: return False, "無法獲取價格"
        
        total = price * quantity
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("INSERT INTO trades (timestamp, symbol, name, action, quantity, price, total, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                 (datetime.now().isoformat(), symbol, pos["name"], "SELL", quantity, price, total, reason))
        
        self.cash += total
        c.execute("INSERT INTO cash_log (timestamp, action, amount, balance) VALUES (?, ?, ?, ?)",
                 (datetime.now().isoformat(), "SELL", total, self.cash))
        
        new_qty = pos["quantity"] - quantity
        if new_qty > 0:
            c.execute("UPDATE portfolio SET quantity = ? WHERE symbol = ?", (new_qty, symbol))
        else:
            c.execute("DELETE FROM portfolio WHERE symbol = ?", (symbol,))
        
        conn.commit()
        conn.close()
        self.load_portfolio()
        return True, f"賣出 {symbol} x{quantity} @ ${price:,.2f}"
    
    def get_stock_name(self, symbol):
        for s in STOCK_POOL:
            if s["symbol"] == symbol: return s["name"]
        return symbol
    
    def calculate_portfolio_value(self):
        total = self.cash
        for symbol, pos in self.positions.items():
            price = self.get_stock_price(symbol)
            if price: total += price * pos["quantity"]
        return total

if __name__ == "__main__":
    investor = StockInvestor()
    print(f"現金: ${investor.cash:,.0f}")
    print(f"持股: {list(investor.positions.keys())}")
    print(f"總市值: ${investor.calculate_portfolio_value():,.0f}")
