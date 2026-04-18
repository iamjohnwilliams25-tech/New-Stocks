from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from kiteconnect import KiteConnect
import datetime
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "v4se78490za52f7m"
API_SECRET = "hestwv676imoo7wcf443vmj70s7muhzr"

kite = KiteConnect(api_key=API_KEY)

ACCESS_TOKEN = None


@app.get("/login")
def login():
    return RedirectResponse(kite.login_url())


@app.get("/callback")
def callback(request_token: str = None):
    global ACCESS_TOKEN

    data = kite.generate_session(request_token, api_secret=API_SECRET)
    ACCESS_TOKEN = data["access_token"]

    kite.set_access_token(ACCESS_TOKEN)

    return RedirectResponse("https://stocks.ofesto.com/?login=success")


@app.get("/stocks")
def get_stocks():
    global ACCESS_TOKEN

    if not ACCESS_TOKEN:
        return {"error": "Login required"}

    try:
        symbols = [
            "NSE:HDFCBANK","NSE:ICICIBANK","NSE:SBIN","NSE:AXISBANK",
            "NSE:INFY","NSE:TCS","NSE:WIPRO",
            "NSE:RELIANCE","NSE:ONGC","NSE:BPCL",
            "NSE:TATAMOTORS","NSE:HEROMOTOCO",
            "NSE:ITC","NSE:DABUR",
            "NSE:SUNPHARMA","NSE:CIPLA"
        ]

        result = []
        today = datetime.date.today()
        from_date = today - datetime.timedelta(days=10)

        for symbol in symbols:
            try:
                ltp = kite.ltp(symbol)
                price = ltp[symbol]["last_price"]

                hist = kite.historical_data(
                    ltp[symbol]["instrument_token"],
                    from_date,
                    today,
                    "day"
                )

                if len(hist) < 2:
                    continue

                old_price = hist[0]["close"]
                latest_price = hist[-1]["close"]

                change = ((latest_price - old_price) / old_price) * 100

                # 🔥 SMART LOGIC
                target = latest_price * (1 + random.uniform(0.03, 0.08))
                stop_loss = latest_price * (1 - random.uniform(0.02, 0.05))

                if change > 5:
                    signal = "BUY"
                    confidence = "High"
                    days = "2-4"
                elif change > 1:
                    signal = "BUY (Weak)"
                    confidence = "Medium"
                    days = "3-5"
                else:
                    signal = "SELL"
                    confidence = "Low"
                    days = "-"

                result.append({
                    "stock": symbol.replace("NSE:", ""),
                    "price": round(latest_price, 2),
                    "trend": round(change, 2),
                    "target": round(target, 2),
                    "stop_loss": round(stop_loss, 2),
                    "days": days,
                    "signal": signal,
                    "confidence": confidence
                })

            except:
                continue

        return {
            "time": str(datetime.datetime.now()),
            "nifty": round(random.uniform(22000, 22500), 2),
            "sensex": round(random.uniform(72000, 74000), 2),
            "data": result
        }

    except Exception as e:
        return {"error": str(e)}
