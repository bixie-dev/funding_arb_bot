from flask import Flask, render_template, jsonify
from commands.funding import detect_arbitrage_opportunities
import asyncio

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/arbitrage')
def api_arbitrage():
    opportunities = detect_arbitrage_opportunities()
    return jsonify(opportunities)

if __name__ == "__main__":
    app.run(debug=False, port=5000)