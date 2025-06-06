from flask import Flask, render_template, jsonify
from commands.funding import detect_arbitrage_opportunities
from flask import request
from exchanges.hyperliquid import Hyperliquid
from exchanges.bybit import Bybit
from exchanges.gmx import Gmx
from exchanges.dydx import Dydx

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/arbitrage')
def api_arbitrage():
    opportunities = detect_arbitrage_opportunities()
    return jsonify(opportunities)

@app.route('/api/open_position', methods=['POST'])
def api_open_position():
    data = request.get_json()
    coin = data.get('coin')
    exchange = data.get("exchange")
    size = data.get("size")
    leverage = data.get("leverage")
    limit = data.get("limit")
    if exchange == "hyperliquid":
        client = Hyperliquid()
    elif exchange == "bybit":
        client = Bybit()
    elif exchange == "gmx":
        client = Gmx()
    elif exchange == "dydx":
        client = Dydx()
    position_id = client.open_position(coin, size, leverage, limit)
    print(position_id, '----------------')
    return jsonify({"message": "Position received", "data": data})

@app.route('/api/close_position', methods=['POST'])
def api_close_position():
    data = request.get_json()
    exchange = data.get("exchange")
    if exchange == "hyperliquid":
        client = Hyperliquid()
    elif exchange == "bybit":
        client = Bybit()
    elif exchange == "gmx":
        client = Gmx()
    elif exchange == "dydx":
        client = Dydx()
    position_id = client.get_open_positions()
    print(position_id, '------------------------------')
    result = client.close_position(position_id)
    if result == True:
        return True
    else: 
        return False

if __name__ == "__main__":
    app.run(debug=False, port=5000)