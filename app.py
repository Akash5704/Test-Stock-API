from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_caching import Cache
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
import time

app = Flask(__name__)
CORS(app)

# Configure caching (in-memory)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

# ---- Helper Function for Single Symbol ----
@cache.memoize(timeout=300)
def fetch_info(symbol):
    """Fetch stock info for a single symbol with caching."""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        if not info or "regularMarketPrice" not in info:
            return {"symbol": symbol.upper(), "error": f"No data found for '{symbol}'"}

        return {
            "symbol": symbol.upper(),
            "price": info.get("regularMarketPrice"),
            "dayHigh": info.get("dayHigh"),
            "dayLow": info.get("dayLow"),
            "previousClose": info.get("previousClose"),
            "marketCap": info.get("marketCap"),
            "timestamp": time.time()
        }
    except Exception as e:
        return {"symbol": symbol.upper(), "error": str(e)}


# ---- Route: Single Stock ----
@app.route('/stock', methods=['GET'])
def get_stock():
    """Fetch data for one stock symbol."""
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({"error": "Please provide a stock symbol"}), 400

    data = fetch_info(symbol)
    if "error" in data:
        return jsonify(data), 404
    return jsonify(data)


# ---- Route: Multiple Stocks (Parallel Fetch) ----
@app.route('/stocks', methods=['POST'])
def get_multiple_stocks_parallel():
    """Fetch data for multiple symbols in parallel."""
    data = request.get_json()
    symbols = data.get('symbols', [])

    if not symbols or not isinstance(symbols, list):
        return jsonify({"error": "Please provide a list of symbols"}), 400

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_info, symbols))

    return jsonify(results)

@app.route('/history', methods=['GET'])
def get_stock_history():
    """Fetch historical data for chart intervals."""
    symbol = request.args.get('symbol')
    interval = request.args.get('interval', '1d')  # default 1d
    period = request.args.get('period', '1mo')     # default 1 month

    if not symbol:
        return jsonify({"error": "Please provide a stock symbol"}), 400

    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period, interval=interval)

        if hist.empty:
            return jsonify({"error": f"No historical data for '{symbol}'"}), 404

        data = []
        for date, row in hist.iterrows():
            data.append({
                "date": date.strftime('%Y-%m-%d %H:%M:%S'),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            })

        return jsonify({
            "symbol": symbol.upper(),
            "interval": interval,
            "period": period,
            "data": data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---- Home Route ----
@app.route('/')
def home():
    return jsonify({"message": "Stock API is running ✅"})


# ---- Run Server ----
if __name__ == '__main__':
    # For local testing
    app.run(host='0.0.0.0', port=7860,debug = True)
