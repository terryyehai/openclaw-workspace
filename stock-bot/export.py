#!/usr/bin/env python3
"""
生成靜態數據供 GitHub Pages 使用
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from investor import StockInvestor

def export_data():
    investor = StockInvestor()
    
    # 獲取股價
    prices = {}
    import yfinance as yf
    for symbol in ["2330.TW", "2317.TW", "2454.TW", "2603.TW", "2615.TW", "2884.TW", "2891.TW", "0050.TW", "0056.TW"]:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            prices[symbol] = info.get('currentPrice') or info.get('regularMarketPrice')
        except:
            prices[symbol] = None
    
    # 計算組合
    holdings = []
    total_stock = 0
    for symbol, pos in investor.positions.items():
        price = prices.get(symbol)
        if price:
            value = price * pos["quantity"]
            cost = pos["avg_cost"] * pos["quantity"]
            profit = value - cost
            holdings.append({
                "symbol": symbol,
                "name": pos["name"],
                "quantity": pos["quantity"],
                "avg_cost": pos["avg_cost"],
                "current_price": price,
                "value": value,
                "profit": profit,
                "profit_pct": (profit / cost * 100) if cost > 0 else 0
            })
            total_stock += value
    
    # 大盤漲幅
    try:
        ticker = yf.Ticker("0050.TW")
        hist = ticker.history(period="1mo")
        benchmark = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100 if len(hist) > 1 else 0
    except:
        benchmark = 0
    
    total_value = investor.cash + total_stock
    initial = 100000
    profit = total_value - initial
    profit_pct = (profit / initial) * 100
    vs_benchmark = profit_pct - benchmark
    
    data = {
        "total_value": total_value,
        "cash": investor.cash,
        "profit": profit,
        "profit_pct": profit_pct,
        "benchmark": benchmark,
        "vs_benchmark": vs_benchmark,
        "holdings": holdings,
        "updated": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 寫入 JSON
    with open('/home/terry/.openclaw/workspace-dev/webapp/data.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"已導出數據: 總市值 ${total_value:,.0f}, 損益 ${profit:,.0f}")

if __name__ == "__main__":
    export_data()
