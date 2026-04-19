from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from kiteconnect import KiteConnect
import datetime

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 KEYS
API_KEY = "v4se78490za52f7m"
API_SECRET = "hestwv676imoo7wcf443vmj70s7muhzr"

kite = KiteConnect(api_key=API_KEY)

ACCESS_TOKEN = None


# 🔐 LOGIN
@app.get("/login")
def login():
    return RedirectResponse(kite.login_url())


# 🔁 CALLBACK
@app.get("/callback")
def callback(request_token: str = None):
    global ACCESS_TOKEN

    data = kite.generate_session(request_token, api_secret=API_SECRET)
    ACCESS_TOKEN = data["access_token"]
    kite.set_access_token(ACCESS_TOKEN)

    return RedirectResponse("https://stocks.ofesto.com/?login=success")


# 📊 STOCK SCANNER
@app.get("/stocks")
def get_stocks():
    global ACCESS_TOKEN

    if not ACCESS_TOKEN:
        return {"error": "Login required"}

    try:
        # 🔥 MARKET TREND CHECK (NIFTY)
        nifty = kite.ltp("NSE:NIFTY 50")["NSE:NIFTY 50"]["last_price"]

        # Simple bullish filter (you can improve later)
        if nifty < 20000:
            return {"error": "Market weak. No trades today."}

        symbols = [
            "NSE:HDFCBANK","NSE:ICICIBANK","NSE:SBIN","NSE:AXISBANK",
            "NSE:INFY","NSE:TCS","NSE:WIPRO",
            "NSE:RELIANCE","NSE:ONGC","NSE:BPCL",
            "NSE:TATAMOTORS","NSE:HEROMOTOCO",
            "NSE:ITC","NSE:DABUR",
            "NSE:SUNPHARMA","NSE:CIPLA",
            "NSE:COALINDIA","NSE:NTPC","NSE:POWERGRID",
            "NSE:INDUSINDBK","NSE:CANBK","NSE:PNB"
        ]

        result = []
        today = datetime.date.today()
        from_date = today - datetime.timedelta(days=10)

        for symbol in symbols:
            try:
                ltp = kite.ltp(symbol)
                price = ltp[symbol]["last_price"]

                if price > 1500:
                    continue

                hist = kite.historical_data(
                    ltp[symbol]["instrument_token"],
                    from_date,
                    today,
                    "day"
                )

                if len(hist) < 5:
                    continue

                closes = [x["close"] for x in hist]
                highs = [x["high"] for x in hist]

                old_price = closes[0]
                latest_price = closes[-1]

                change = ((latest_price - old_price) / old_price) * 100

                # 🔥 STRICT FILTERS
                breakout = latest_price >= max(highs[:-1])
                momentum = change > 3

                if not (breakout and momentum):
                    continue

                # 🎯 TARGET LOGIC (realistic)
                target = latest_price * 1.05
                stop_loss = latest_price * 0.97

                result.append({
                    "stock": symbol.replace("NSE:", ""),
                    "price": round(latest_price, 2),
                    "trend": round(change, 2),
                    "target": round(target, 2),
                    "stop_loss": round(stop_loss, 2),
                    "days": "2-7",
                    "signal": "STRONG BUY",
                    "confidence": "High"
                })

            except:
                continue

        return {
            "time": str(datetime.datetime.now()),
            "count": len(result),
            "data": sorted(result, key=lambda x: x["trend"], reverse=True)
        }

    except Exception as e:
        return {"error": str(e)}
