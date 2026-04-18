from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from kiteconnect import KiteConnect
import datetime

app = FastAPI()

# 🔐 ALLOW YOUR WEBSITE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can later restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 YOUR KEYS
API_KEY = "v4se78490za52f7m"
API_SECRET = "hestwv676imoo7wcf443vmj70s7muhzr"

kite = KiteConnect(api_key=API_KEY)

ACCESS_TOKEN = None


# 🔵 LOGIN
@app.get("/login")
def login():
    return RedirectResponse(kite.login_url())


# 🔵 CALLBACK
@app.get("/callback")
def callback(request_token: str = None):
    global ACCESS_TOKEN

    if not request_token:
        return {"error": "Missing request_token"}

    data = kite.generate_session(request_token, api_secret=API_SECRET)
    ACCESS_TOKEN = data["access_token"]

    kite.set_access_token(ACCESS_TOKEN)

    return RedirectResponse("https://stocks.ofesto.com/?login=success")


# 🔵 STOCK DATA
@app.get("/stocks")
def get_stocks():
    global ACCESS_TOKEN

    if not ACCESS_TOKEN:
        return {"error": "Please login first"}

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

                if change > 5:
                    signal = "BUY"
                elif change > 1:
                    signal = "BUY (Weak)"
                else:
                    signal = "SELL"

                result.append({
                    "stock": symbol.replace("NSE:", ""),
                    "price": round(latest_price, 2),
                    "trend": round(change, 2),
                    "signal": signal
                })

            except:
                continue

        return result

    except Exception as e:
        return {"error": str(e)}
