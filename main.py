from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from kiteconnect import KiteConnect
from datetime import datetime, timedelta

app = FastAPI()

# ✅ CORS FIX (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 YOUR KEYS
API_KEY = "v4se78490za52f7m"
API_SECRET = "hestwv676imoo7wcf443vmj70s7muhzr"

kite = KiteConnect(api_key=API_KEY)

# 🔑 TOKEN (SESSION BASED)
ACCESS_TOKEN = None

# 📊 STOCK TOKENS
stocks = {
    "RELIANCE": 738561,
    "INFY": 408065,
    "TCS": 2953217,
    "HDFCBANK": 1333,
    "ICICIBANK": 4963,
    "SBIN": 779521,
    "AXISBANK": 1510401,
    "ITC": 424961,
    "ONGC": 633601,
    "TATAMOTORS": 884737
}

@app.get("/")
def home():
    return {"status": "running"}

# 🔐 LOGIN
@app.get("/login")
def login():
    return RedirectResponse(kite.login_url())

# 🔁 CALLBACK
@app.get("/callback")
def callback(request: Request):
    global ACCESS_TOKEN

    request_token = request.query_params.get("request_token")

    if not request_token:
        return {"error": "No request_token"}

    try:
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        ACCESS_TOKEN = data["access_token"]

        kite.set_access_token(ACCESS_TOKEN)

        # 🔁 REDIRECT BACK TO YOUR SITE
        return RedirectResponse("https://stocks.ofesto.com/?login=success")

    except Exception as e:
        return {"error": str(e)}

# 📊 STOCK API
@app.get("/stocks")
def get_stocks():
    global ACCESS_TOKEN

    try:
        if not ACCESS_TOKEN:
            return {"error": "LOGIN REQUIRED"}

        kite.set_access_token(ACCESS_TOKEN)

        results = []

        for name, token in stocks.items():
            try:
                data = kite.historical_data(
                    token,
                    datetime.now() - timedelta(days=10),
                    datetime.now(),
                    "day"
                )

                if not data:
                    continue

                closes = [c["close"] for c in data]
                latest = closes[-1]
                old = closes[0]

                change = ((latest - old) / old) * 100

                # 📊 SIGNAL LOGIC
                if change > 3:
                    signal = "STRONG BUY"
                    confidence = "High"
                elif change > 1.5:
                    signal = "BUY"
                    confidence = "Medium"
                elif change > 0:
                    signal = "WEAK BUY"
                    confidence = "Low"
                else:
                    signal = "AVOID"
                    confidence = "Low"

                target = latest * 1.03
                stop_loss = latest * 0.95

                results.append({
                    "stock": name,
                    "price": round(latest, 2),
                    "trend": round(change, 2),
                    "target": round(target, 2),
                    "stop_loss": round(stop_loss, 2),
                    "days": "2-7",
                    "signal": signal,
                    "confidence": confidence
                })

            except Exception as e:
                print("Stock error:", name, e)

        if len(results) == 0:
            return {"error": "NO DATA FROM API"}

        results = sorted(results, key=lambda x: x["trend"], reverse=True)

        return {
            "time": str(datetime.now()),
            "count": len(results),
            "data": results
        }

    except Exception as e:
        return {"error": str(e)}
