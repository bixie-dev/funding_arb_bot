from flask import Flask, render_template, jsonify
from commands.funding import detect_arbitrage_opportunities
from flask import request
from exchanges.hyperliquid import Hyperliquid
from exchanges.bybit import Bybit
from exchanges.gmx import Gmx
from exchanges.dydx import Dydx
from exchanges.drift import Drift
from exchanges.derive import Derive
from exchanges.lighter import Lighter
from exchanges.gate import Gate
import asyncio

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/arbitrage')
def api_arbitrage():
    opportunities = asyncio.run(detect_arbitrage_opportunities())
    return jsonify(opportunities)

@app.route('/api/open_position', methods=['POST'])
def api_open_position():
    data = request.get_json()
    coin = data.get('coin')
    long_ex = data.get('long_ex')
    short_ex = data.get('short_ex')
    order = data.get('order')
    amount = data.get('amount')
    size = data.get('size')
    leverage = data.get('leverage')

    if long_ex == "Hyperliquid":
        client_long = Hyperliquid()
    elif long_ex == "Bybit":
        client_long = Bybit()
    elif long_ex == "gmx":
        client_long = Gmx()
    elif long_ex == "dydx":
        client_long = Dydx()
    elif long_ex == "drift":
        client_long = Drift()
    elif long_ex == "derive":
        client_long = Derive()
    elif long_ex == "lighter":
        client_long = Lighter()
    elif long_ex == "gate":
        client_long = Gate()
        
    if short_ex == "Hyperliquid":
        client_short = Hyperliquid()
    elif short_ex == "Bybit":
        client_short = Bybit()
    elif short_ex == "GMX":
        client_short = Gmx()
    elif short_ex == "Dydx":
        client_short = Dydx()
    elif short_ex == "Drift":
        client_short = Drift()
    elif short_ex == "Derive":
        client_short = Derive()
    elif short_ex == "Lighter":
        client_short = Lighter()
    elif short_ex == "Gate.io":
        client_short = Gate()
    if(client_long.get_open_positions()):
        return False
    elif client_short.get_open_positions():
        return False
    result_long = client_long.open_position(coin, size, leverage, 'long', order)
    result_short = client_short.open_position(coin, size, leverage, 'short', order)
    data = {
        'long': result_long,
        'short': result_short
    }
    return jsonify({"message": "Position received", "data": data})

@app.route('/api/close_position', methods=['POST'])
def api_close_position():
    data = request.get_json()
    long_ex = data.get("long_ex") 
    short_ex = data.get("short_ex") 
    if long_ex == "Hyperliquid":
        client_long = Hyperliquid()
    elif long_ex == "Bybit":
        client_long = Bybit()
    elif long_ex == "gmx":
        client_long = Gmx()
    elif long_ex == "dydx":
        client_long = Dydx()
    elif long_ex == "drift":
        client_long = Drift()
    elif long_ex == "derive":
        client_long = Derive()
    elif long_ex == "lighter":
        client_long = Lighter()
    elif long_ex == "gate":
        client_long = Gate()
        
    if short_ex == "Hyperliquid":
        client_short = Hyperliquid()
    elif short_ex == "Bybit":
        client_short = Bybit()
    elif short_ex == "GMX":
        client_short = Gmx()
    elif short_ex == "Dydx":
        client_short = Dydx()
    elif short_ex == "Drift":
        client_short = Drift()
    elif short_ex == "Derive":
        client_short = Derive()
    elif short_ex == "Lighter":
        client_short = Lighter()
    elif short_ex == "Gate.io":
        client_short = Gate()
    result_long = client_long.close_position()
    result_short = client_short.close_position()
    if result_long * result_short == 1:
        return True
    else:
        return False


if __name__ == "__main__":
    app.run(debug=False, port=5000)