from flask import Flask, request, jsonify
from binance.client import Client
from dotenv import load_dotenv
import os
import csv
from datetime import datetime

app = Flask(__name__)
load_dotenv()

# Paramètres API Binance
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
SIMULATE = os.getenv("SIMULATE", "true").lower() == "true"

client = Client(API_KEY, API_SECRET)

# Chemin du fichier log
CSV_FILE = "trades_log.csv"

# Création du CSV si pas encore là
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp", "symbol", "side", "qty", "entry_price",
            "exit_price", "pnl_usd", "pnl_percent"
        ])

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    action = data.get("action")  # "buy" ou "sell"
    symbol = data.get("symbol")
    qty = float(data.get("qty"))

    if SIMULATE:
        print(f"[SIMULATION] {action.upper()} {qty} {symbol}")
        log_trade(symbol, action, qty, 0, 0, 0, 0)
        return jsonify({"status": "simulated"})

    try:
        # Get entry price from ticker
        ticker = client.get_symbol_ticker(symbol=symbol)
        entry_price = float(ticker["price"])

        if action == "buy":
            order = client.order_market_buy(symbol=symbol, quantity=qty)
        elif action == "sell":
            order = client.order_market_sell(symbol=symbol, quantity=qty)
        else:
            return jsonify({"error": "Action invalide"})

        print("✅ Order executed")

        # Get exit price after 5 secondes (simulation clôture)
        import time
        time.sleep(5)
        exit_price = float(client.get_symbol_ticker(symbol=symbol)["price"])

        # PnL brut (pour simplifier, on suppose tout en USDT)
        pnl = (exit_price - entry_price) * qty if action == "buy" else (entry_price - exit_price) * qty
        pnl_percent = (pnl / (entry_price * qty)) * 100

        # Log dans le CSV
        log_trade(symbol, action, qty, entry_price, exit_price, pnl, pnl_percent)

        return jsonify({"status": "executed", "entry": entry_price, "exit": exit_price, "pnl": pnl})

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)})

def log_trade(symbol, side, qty, entry_price, exit_price, pnl_usd, pnl_percent):
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            symbol, side, qty, entry_price, exit_price,
            round(pnl_usd, 2), round(pnl_percent, 2)
        ])
