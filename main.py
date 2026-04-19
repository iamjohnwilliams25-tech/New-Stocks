from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from kiteconnect import KiteConnect
from datetime import datetime, timedelta
import os

app = FastAPI()

# 🔐 YOUR KEYS
API_KEY = "v4se78490za52f7m"
API_SECRET = "hestwv676imoo7wcf443vmj70s7muhzr"

# 🔁 TOKEN STORAGE (temporary memory)
ACCESS_TOKEN = None

kite = KiteConnect(api_key=API_KEY)


# 📊 STOCK LIST
symbols = [
"NSE:HDFCBANK","NSE:ICICIBANK","NSE:SBIN","NSE:AXISBANK",
"NSE:INDUSINDBK","NSE:KOTAKBANK","NSE:CANBK","NSE:PNB",
"NSE:INFY","NSE:TCS","NSE:WIPRO","NSE:HCLTECH","NSE:TECHM",
"NSE:RELIANCE","NSE:ONGC","NSE:BPCL","NSE:IOC",
"NSE:TATAMOTORS","NSE:HEROMOTOCO","NSE:BAJAJ-AUTO",
"NSE:ITC","NSE:DABUR","NSE:HINDUNILVR",
"NSE:SUNPHARMA","NSE:CIPLA","NSE:DRREDDY",
"NSE:COALINDIA","NSE:NTPC","NSE:POWERGRID",
"NSE:ADANIPORTS","NSE:ADANIENT",
"NSE:ZOMATO","NSE:PAYTM","NSE:NYKAA"
]


@app.get("/")
def home():
    return {"message": "Stock API Running"}


# 🔐 LOGIN
@app.get("/login")
def login():
    login_url = kite.login_url()
    return RedirectResponse(login_url)


# 🔁 CALLBACK (AUTO TOKEN GENERATION)
@app.get("/callback")
def callback(request: Request):
    global ACCESS_TOKEN

    request_token = request.query_params.get("request_token")

    if not request_token:
        return {"error": "No request_token received"}

    try:
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        ACCESS_TOKEN = data["access_token"]
        kite.set_access_token(ACCESS_TOKEN)

        return RedirectResponse("https://stocks.ofesto.com/?login=success")

    except Exception as e:
        return {"error": str(e)}


# 📊 STOCK DATA
@app.get("/stocks")
def get_stocks():
    global ACCESS_TOKEN

    if not ACCESS_TOKEN:
        return {"error": "Please login first"}

    results = []

    try:
        for symbol in symbols:
            try:
                ltp_data = kite.ltp(symbol)
                instrument_token = ltp_data[symbol]["instrument_token"]

                data = kite.historical_data(
                    instrument_token,
                    datetime.now() - timedelta(days=15),
                    datetime.now(),
                    "day"
                )

                if len(data) < 10:
                    continue

                closes = [c["close"] for c in data]
                highs = [c["high"] for c in data]

                latest_price = closes[-1]
                old_price = closes[-10]

                # 💰 PRICE FILTER
                if latest_price > 1500:
                    continue

                # 📈 TREND %
                change = ((latest_price - old_price) / old_price) * 100
                high_10 = max(highs[:-1])

                # 🧠 LOGIC
                strong_breakout = latest_price >= (high_10 * 0.97)
                medium_trend = change > 1.5

                if change > 3 and strong_breakout:
                    signal = "STRONG BUY"
                    confidence = "High"
                    target = latest_price * 1.06
                    stop_loss = latest_price * 0.97

                elif medium_trend:
                    signal = "BUY"
                    confidence = "Medium"
                    target = latest_price * 1.04
                    stop_loss = latest_price * 0.96

                else:
                    continue

                results.append({
                    "stock": symbol.replace("NSE:", ""),
                    "price": round(latest_price, 2),
                    "trend": round(change, 2),
                    "target": round(target, 2),
                    "stop_loss": round(stop_loss, 2),
                    "days": "2-7",
                    "signal": signal,
                    "confidence": confidence
                })

            except:
                continue

        results = sorted(results, key=lambda x: x["trend"], reverse=True)

        return {
            "time": str(datetime.now()),
            "count": len(results),
            "data": results
        }

    except Exception as e:
        return {"error": str(e)}
