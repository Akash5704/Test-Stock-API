# Run `python main.py` in the terminal

# Note: Python is lazy loaded so the first run will take a moment,
# But after cached, subsequent loads are super fast! ⚡️
# app.py
from flask import Flask, jsonify, request
import yfinance as yf

app = Flask(__name__)

@app.route('/stock', methods=['GET'])
def get_stock():
    # Get the stock symbol from query params
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({"error": "Please provide a stock symbol"}), 400
    
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        data = {
            "symbol": symbol.upper(),
            "currentPrice": info.get("regularMarketPrice"),
            "dayHigh": info.get("dayHigh"),
            "dayLow": info.get("dayLow"),
            "previousClose": info.get("previousClose"),
            "marketCap": info.get("marketCap")
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
