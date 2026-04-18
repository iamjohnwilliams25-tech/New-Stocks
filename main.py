from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from kiteconnect import KiteConnect
import datetime

app = FastAPI()

API_KEY = "v4se78490za52f7m"
API_SECRET = "hestwv676imoo7wcf443vmj70s7muhzr"

kite = KiteConnect(api_key=API_KEY)

# 🔥 store token globally
ACCESS_TOKEN = None


# ✅ LOGIN BUTTON
@app.get("/login")
def login():
    return RedirectResponse(kite.login_url())


# ✅ AUTO CALLBACK (NO USER ACTION NEEDED)
@app.get("/callback")
def callback(request_token: str):
    global ACCESS_TOKEN

    data = kite.generate_session(request_token, api_secret=API_SECRET)
    ACCESS_TOKEN = data["access_token"]

    kite.set_access_token(ACCESS_TOKEN)

    return RedirectResponse("https://stocks.ofesto.com/?login=success")


# ✅ STOCK API
@app.get("/stocks")
def get_stocks():
    global ACCESS_TOKEN

    if not ACCESS_TOKEN:
        return {"error": "Please click Login first"}

    try:
        stocks = [
            {"symbol": "NSE:HDFCBANK", "sector": "Banking"},
            {"symbol": "NSE:ICICIBANK", "sector": "Banking"},
            {"symbol": "NSE:SBIN", "sector": "Banking"},
            {"symbol": "NSE:AXISBANK", "sector": "Banking"},

            {"symbol": "NSE:INFY", "sector": "IT"},
            {"symbol": "NSE:WIPRO", "sector": "IT"},
            {"symbol": "NSE:TCS", "sector": "IT"},

            {"symbol": "NSE:RELIANCE", "sector": "Energy"},
            {"symbol": "NSE:ONGC", "sector": "Energy"},
            {"symbol": "NSE:BPCL", "sector": "Energy"},

            {"symbol": "NSE:TATAMOTORS", "sector": "Auto"},
            {"symbol": "NSE:HEROMOTOCO", "sector": "Auto"},

            {"symbol": "NSE:ITC", "sector": "FMCG"},
            {"symbol": "NSE:DABUR", "sector": "FMCG"},

            {"symbol": "NSE:SUNPHARMA", "sector": "Pharma"},
            {"symbol": "NSE:CIPLA", "sector": "Pharma"},
        ]

        result = []
        today = datetime.date.today()
        from_date = today - datetime.timedelta(days=10)

        for s in stocks:
            symbol = s["symbol"]
            sector = s["sector"]

            try:
                ltp_data = kite.ltp(symbol)
                price = ltp_data[symbol]["last_price"]

                hist = kite.historical_data(
                    instrument_token=ltp_data[symbol]["instrument_token"],
                    from_date=from_date,
                    to_date=today,
                    interval="day"
                )

                if len(hist) < 2:
                    continue

                old_price = hist[0]["close"]
                latest_price = hist[-1]["close"]

                change = ((latest_price - old_price) / old_price) * 100

                if latest_price > 1500:
                    continue

                if change > 5:
                    suggestion = "BUY"
                    confidence = "High"
                elif change > 1:
                    suggestion = "BUY (Weak)"
                    confidence = "Medium"
                else:
                    suggestion = "SELL"
                    confidence = "Low"

                result.append({
                    "stock": symbol.replace("NSE:", ""),
                    "sector": sector,
                    "price": round(latest_price, 2),
                    "trend_10d": round(change, 2),
                    "suggestion": suggestion,
                    "confidence": confidence
                })

            except:
                continue

        return sorted(result, key=lambda x: x["trend_10d"], reverse=True)

    except Exception as e:
        return {"error": str(e)}
