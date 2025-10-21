# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from functools import lru_cache
import time

app = Flask(__name__)
CORS(app)

# Cache results for repeated symbols to reduce API load
@lru_cache(maxsize=512)
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        # Some tickers may not return data
        if not info or "regularMarketPrice" not in info:
            return {"error": f"No data found for symbol '{symbol}'"}

        data = {
            "symbol": symbol.upper(),
            "currentPrice": info.get("regularMarketPrice"),
            "dayHigh": info.get("dayHigh"),
            "dayLow": info.get("dayLow"),
            "previousClose": info.get("previousClose"),
            "marketCap": info.get("marketCap"),
            "timestamp": time.time()
        }
        return data
    except Exception as e:
        return {"error": str(e)}

@app.route('/stock', methods=['GET'])
def get_stock():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({"error": "Please provide a stock symbol"}), 400

    data = get_stock_data(symbol)
    if "error" in data:
        return jsonify(data), 404
    return jsonify(data)

@app.route('/')
def home():
    return jsonify({"message": "Stock API is running ✅"})

if __name__ == '__main__':
    # For local testing
    app.run(host='0.0.0.0', port=5000, debug=True)
