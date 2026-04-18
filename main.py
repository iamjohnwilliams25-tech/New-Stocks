from fastapi import FastAPI
from kiteconnect import KiteConnect
import datetime

app = FastAPI()

# 🔴 PASTE YOUR KEYS HERE
API_KEY = "v4se78490za52f7m"
API_SECRET = "hestwv676imoo7wcf443vmj70s7muhzr"
ACCESS_TOKEN = "FuPaS2aQ5rxXNP1BRoB80IGIy7OWYqIS"

kite = KiteConnect(api_key=API_KEY)

# Set access token only if available
if ACCESS_TOKEN != "PASTE_DAILY_ACCESS_TOKEN":
    kite.set_access_token(ACCESS_TOKEN)

# ✅ HOME
@app.get("/")
def home():
    return {"message": "API running"}

# ✅ LOGIN URL
@app.get("/login")
def login():
    return {"login_url": kite.login_url()}

# ✅ GENERATE TOKEN
@app.get("/generate-token")
def generate_token(request_token: str):
    data = kite.generate_session(request_token, api_secret=API_SECRET)
    access_token = data["access_token"]
    return {"access_token": access_token}

# ✅ STOCK DATA
@app.get("/stocks")
def get_stocks():
    try:
        stocks = [
            {"symbol": "NSE:HDFCBANK", "sector": "Banking"},
            {"symbol": "NSE:ICICIBANK", "sector": "Banking"},
            {"symbol": "NSE:SBIN", "sector": "Banking"},
            {"symbol": "NSE:AXISBANK", "sector": "Banking"},

            {"symbol": "NSE:INFY", "sector": "IT"},
            {"symbol": "NSE:TCS", "sector": "IT"},
            {"symbol": "NSE:WIPRO", "sector": "IT"},

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

                # ❗ Skip if no token set
                if not kite.access_token:
                    return {"error": "Access token missing"}

                # 🔥 Get historical data
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

                # 🔥 Filter <1500
                if latest_price > 1500:
                    continue

                # 🔥 Signal logic
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
                    "current_price": round(latest_price, 2),
                    "buy_price": round(latest_price * 1.01, 2),
                    "target": round(latest_price * 1.05, 2),
                    "stop_loss": round(latest_price * 0.97, 2),
                    "change_10d": round(change, 2),
                    "buy_date": str(today),
                    "target_date": str(today + datetime.timedelta(days=3)),
                    "suggestion": suggestion,
                    "confidence": confidence
                })

            except:
                continue

        return result

    except Exception as e:
        return {"error": str(e)}
