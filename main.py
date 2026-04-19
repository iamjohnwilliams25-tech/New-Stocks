from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from kiteconnect import KiteConnect
from datetime import datetime, timedelta
import os

app = FastAPI()

# ============================
# 🔐 YOUR KEYS
# ============================
API_KEY = "v4se78490za52f7m"
API_SECRET = "hestwv676imoo7wcf443vmj70s7muhzr"

kite = KiteConnect(api_key=API_KEY)

# ============================
# 🔐 TOKEN STORAGE (FILE)
# ============================
TOKEN_FILE = "access_token.txt"

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

# ============================
# 📊 STOCK TOKENS (STABLE)
# ============================
stocks = {
    "HDFCBANK": 1333,
    "ICICIBANK": 4963,
    "SBIN": 779521,
    "AXISBANK": 1510401,
    "INFY": 408065,
    "TCS": 2953217,
    "WIPRO": 969473,
    "RELIANCE": 738561,
    "ITC": 424961,
    "ONGC": 633601,
    "TATAMOTORS": 884737,
    "SUNPHARMA": 857857,
    "CIPLA": 177665,
    "NTPC": 2977281,
    "POWERGRID": 3834113,
    "COALINDIA": 5215745
}

# ============================
# 🏠 HOME
# ============================
@app.get("/")
def home():
    return {"status": "running"}

# ============================
# 🔐 LOGIN
# ============================
@app.get("/login")
def login():
    return RedirectResponse(kite.login_url())

# ============================
# 🔁 CALLBACK
# ============================
@app.get("/callback")
def callback(request: Request):
    request_token = request.query_params.get("request_token")

    if not request_token:
        return {"error": "No request_token"}

    try:
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        access_token = data["access_token"]

        kite.set_access_token(access_token)
        save_token(access_token)

        return RedirectResponse("https://stocks.ofesto.com/?login=success")

    except Exception as e:
        return {"error": str(e)}

# ============================
# 📊 STOCK DATA
# ============================
@app.get("/stocks")
def get_stocks():

    access_token = load_token()

    if not access_token:
        return {"error": "Login required"}

    kite.set_access_token(access_token)

    results = []

    for name, token in stocks.items():
        try:
            data = kite.historical_data(
                token,
                datetime.now() - timedelta(days=15),
                datetime.now(),
                "day"
            )

            if len(data) < 10:
                continue

            closes = [c["close"] for c in data]
            highs = [c["high"] for c in data]

            latest = closes[-1]
            old = closes[-10]

            change = ((latest - old) / old) * 100
            high_10 = max(highs[:-1])

            if change > 3 and latest >= high_10 * 0.95:
                signal = "TOP BUY"
                confidence = "High"
            elif change > 1.5:
                signal = "MEDIUM BUY"
                confidence = "Medium"
            elif change > 0:
                signal = "AVERAGE"
                confidence = "Low"
            else:
                signal = "LOW / AVOID"
                confidence = "Very Low"

            target = latest * (1 + change/100 * 0.5)
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

        except:
            continue

    results = sorted(results, key=lambda x: x["trend"], reverse=True)

    return {
        "time": str(datetime.now()),
        "count": len(results),
        "data": results
    }
