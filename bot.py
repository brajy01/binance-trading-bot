from flask import Flask, request, jsonify
import os
import requests
from binance.client import Client

app = Flask(__name__)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
SIMULATE = os.getenv("SIMULATE", "true").lower() == "true"

client = Client(API_KEY, API_SECRET)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    action = data.get("action")
    symbol = data.get("symbol")
    qty = float(data.get("qty"))

    if SIMULATE:
        print(f"🔁 [SIMULATION] {action.upper()} {qty} {symbol}")
        return jsonify({"status": "simulated", "action": action, "symbol": symbol, "qty": qty})

    try:
        if action == "buy":
            order = client.order_market_buy(symbol=symbol, quantity=qty)
        elif action == "sell":
            order = client.order_market_sell(symbol=symbol, quantity=qty)
        else:
            return jsonify({"error": "Invalid action"})

        return jsonify({"status": "executed", "order": order})

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)})
