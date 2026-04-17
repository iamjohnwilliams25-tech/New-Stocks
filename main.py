from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import time

app = FastAPI()

# CORS (IMPORTANT for WordPress)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stock list (you can expand to 100+ later)
stocks = [
    "RELIANCE.NS","HDFCBANK.NS","ICICIBANK.NS","TATAMOTORS.NS","INFY.NS","SBIN.NS",
    "AXISBANK.NS","KOTAKBANK.NS","LT.NS","MARUTI.NS","BAJFINANCE.NS","HCLTECH.NS",
    "WIPRO.NS","ULTRACEMCO.NS","ASIANPAINT.NS","TITAN.NS","SUNPHARMA.NS",
    "ONGC.NS","NTPC.NS","POWERGRID.NS","ADANIENT.NS","ADANIPORTS.NS",
    "COALINDIA.NS","BPCL.NS","IOC.NS","TECHM.NS","DRREDDY.NS","CIPLA.NS"
]

# Cache system
cache_data = []
last_updated = 0

@app.get("/stocks")
def get_stocks():
    global cache_data, last_updated

    # refresh every 5 minutes
    if time.time() - last_updated < 300:
        return cache_data

    result = []

    for s in stocks:
        try:
            ticker = yf.Ticker(s)
            hist = ticker.history(period="10d")

            if hist.empty or len(hist) < 2:
                continue

            price = float(hist["Close"].iloc[-1])
            old_price = float(hist["Close"].iloc[0])

            change = ((price - old_price) / old_price) * 100

            # Trading logic
            if change > 5:
                suggestion = "BUY"
                confidence = "High"
                days = "2-4"
            elif change > 0:
                suggestion = "BUY (Weak)"
                confidence = "Medium"
                days = "3-5"
            else:
                suggestion = "SELL"
                confidence = "Low"
                days = "-"

            result.append({
                "stock": s.replace(".NS",""),
                "buy_price": round(price * 1.01, 2),
                "target": round(price * 1.05, 2),
                "stop_loss": round(price * 0.97, 2),
                "change_10d": round(change, 2),
                "expected_days": days,
                "suggestion": suggestion,
                "confidence": confidence
            })

        except Exception as e:
            print("Error:", s, e)
            continue

    # Sort best stocks first
    result = sorted(result, key=lambda x: x["change_10d"], reverse=True)

    cache_data = result
    last_updated = time.time()

    return result