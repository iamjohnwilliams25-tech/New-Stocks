from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from kiteconnect import KiteConnect
from datetime import datetime, timedelta

app = FastAPI()

# ==============================
# 🔐 ADD YOUR KEYS HERE
# ==============================
API_KEY = "v4se78490za52f7m"
API_SECRET = "hestwv676imoo7wcf443vmj70s7muhzr"

# ⚠️ DO NOT TOUCH BELOW
ACCESS_TOKEN = None
kite = KiteConnect(api_key=API_KEY)

# ==============================
# 📊 STOCK LIST (BIG LIST)
# ==============================
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

# ==============================
# 🏠 HOME
# ==============================
@app.get("/")
def home():
    return {"status": "API Running"}

# ==============================
# 🔐 LOGIN
# ==============================
@app.get("/login")
def login():
    return RedirectResponse(kite.login_url())

# ==============================
# 🔁 CALLBACK (IMPORTANT)
# ==============================
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

        # redirect back to your site
        return RedirectResponse("https://stocks.ofesto.com/?login=success")

    except Exception as e:
        return {"error": str(e)}

# ==============================
# 📊 STOCK DATA
# ==============================
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

                # 💰 FILTER PRICE < 1500
                if latest_price > 1500:
                    continue

                change = ((latest_price - old_price) / old_price) * 100
                high_10 = max(highs[:-1])

                # ======================
                # 📈 CATEGORY LOGIC
                # ======================

                if change > 3 and latest_price >= high_10 * 0.95:
                    signal = "TOP BUY"
                    confidence = "High"
                    target = latest_price * 1.06
                    stop_loss = latest_price * 0.97

                elif change > 1.5:
                    signal = "MEDIUM BUY"
                    confidence = "Medium"
                    target = latest_price * 1.04
                    stop_loss = latest_price * 0.96

                elif change > 0:
                    signal = "AVERAGE"
                    confidence = "Low"
                    target = latest_price * 1.02
                    stop_loss = latest_price * 0.95

                else:
                    signal = "LOW / AVOID"
                    confidence = "Very Low"
                    target = latest_price * 1.01
                    stop_loss = latest_price * 0.93

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

        # 📊 SORT BEST FIRST
        results = sorted(results, key=lambda x: x["trend"], reverse=True)

        # 🔥 ALWAYS 50
        results = results[:50]

        return {
            "time": str(datetime.now()),
            "count": len(results),
            "data": results
        }

    except Exception as e:
        return {"error": str(e)}
