from flask import Flask, request, jsonify
import requests
import os
import time
import hmac
import hashlib

app = Flask(__name__)

# === Configuration Binance ===
API_KEY = os.getenv("BINANCE_API_KEY", "TEST")
API_SECRET = os.getenv("BINANCE_API_SECRET", "TEST")
BASE_URL = "https://api.binance.com"

# === Envoi de la requête à Binance ===
def place_order(symbol, side, qty):
    if os.getenv("SIMULATE") == "true":
        print(f"[SIMULATION] {side.upper()} {qty} {symbol}")
        return {"simulated": True, "side": side, "qty": qty, "symbol": symbol}

    endpoint = "/api/v3/order"
    url = BASE_URL + endpoint

    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side.upper(),
        "type": "MARKET",
        "quantity": qty,
        "timestamp": timestamp
    }

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature

    headers = {
        "X-MBX-APIKEY": API_KEY
    }

    response = requests.post(url, headers=headers, params=params)
    return response.json()

# === Webhook endpoint ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        symbol = data.get("symbol")
        action = data.get("action")
        qty = float(data.get("qty", 0.01))

        if symbol and action in ["buy", "sell"]:
            result = place_order(symbol, action, qty)
            return jsonify({"status": "success", "response": result})
        else:
            return jsonify({"status": "error", "message": "Invalid data"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# === Lancement ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
