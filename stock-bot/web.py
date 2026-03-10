#!/usr/bin/env python3
"""
股票投資儀表板
Web 介面顯示投資組合
"""

from flask import Flask, jsonify, render_template_string
import sqlite3
import yfinance as yf
import json

DB_PATH = "/home/terry/.openclaw/workspace-dev/stock-bot/investment.db"
app = Flask(__name__)

def get_portfolio():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM portfolio")
    rows = c.fetchall()
    conn.close()
    
    portfolio = []
    for row in rows:
        symbol = row['symbol']
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.info.get('currentPrice') or ticker.info.get('regularMarketPrice')
        except:
            price = 0
        
        item = dict(row)
        item['current_price'] = price or 0
        item['market_value'] = (price or 0) * row['shares']
        item['profit'] = item['market_value'] - (row['avg_price'] * row['shares'])
        item['profit_pct'] = (item['profit'] / (row['avg_price'] * row['shares']) * 100) if row['avg_price'] > 0 else 0
        portfolio.append(item)
    
    return portfolio

def get_cash():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM cash_log WHERE action='deposit'")
    deposit = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM cash_log WHERE action='withdraw'")
    withdraw = c.fetchone()[0] or 0
    conn.close()
    return deposit - withdraw

@app.route('/')
def index():
    portfolio = get_portfolio()
    cash = get_cash()
    total_value = sum(p['market_value'] for p in portfolio) + cash
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>股票投資儀表板</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            h1 { color: #333; }
            .card { background: white; padding: 20px; margin: 10px 0; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .positive { color: green; }
            .negative { color: red; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #4CAF50; color: white; }
            .summary { display: flex; justify-content: space-around; }
            .summary-item { text-align: center; }
            .summary-value { font-size: 24px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>📈 股票投資儀表板</h1>
        
        <div class="card">
            <div class="summary">
                <div class="summary-item">
                    <div>總資產</div>
                    <div class="summary-value">NT$ {{ "%.0f"|format(total_value) }}</div>
                </div>
                <div class="summary-item">
                    <div>現金</div>
                    <div class="summary-value">NT$ {{ "%.0f"|format(cash) }}</div>
                </div>
                <div class="summary-item">
                    <div>股票市值</div>
                    <div class="summary-value">NT$ {{ "%.0f"|format(total_value - cash) }}</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>持股明細</h2>
            <table>
                <tr>
                    <th>股票</th>
                    <th>股數</th>
                    <th>均價</th>
                    <th>現價</th>
                    <th>市值</th>
                    <th>損益</th>
                </tr>
                {% for stock in portfolio %}
                <tr>
                    <td>{{ stock.symbol }}</td>
                    <td>{{ stock.shares }}</td>
                    <td>NT$ {{ "%.2f"|format(stock.avg_price) }}</td>
                    <td>NT$ {{ "%.2f"|format(stock.current_price) }}</td>
                    <td>NT$ {{ "%.0f"|format(stock.market_value) }}</td>
                    <td class="{{ 'positive' if stock.profit >= 0 else 'negative' }}">
                        NT$ {{ "%.0f"|format(stock.profit) }} ({{ "%.1f"|format(stock.profit_pct) }}%)
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
        
        <p style="color: #666;">更新時間: {{ now }}</p>
    </body>
    </html>
    '''
    from datetime import datetime
    return render_template_string(html, portfolio=portfolio, cash=cash, total_value=total_value, now=datetime.now().strftime('%Y-%m-%d %H:%M'))

@app.route('/api')
def api():
    portfolio = get_portfolio()
    cash = get_cash()
    return jsonify({
        "portfolio": portfolio,
        "cash": cash,
        "total_value": sum(p['market_value'] for p in portfolio) + cash
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
