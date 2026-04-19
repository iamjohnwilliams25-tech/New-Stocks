from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from kiteconnect import KiteConnect
from datetime import datetime, timedelta
import os

app = FastAPI()

API_KEY = "v4se78490za52f7m"
API_SECRET = "hestwv676imoo7wcf443vmj70s7muhzr"

kite = KiteConnect(api_key=API_KEY)

TOKEN_FILE = "access_token.txt"

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

# ✅ SIMPLE TEST STOCKS
stocks = {
    "RELIANCE": 738561,
    "INFY": 408065,
    "TCS": 2953217,
    "HDFCBANK": 1333
}

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/login")
def login():
    return RedirectResponse(kite.login_url())

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

        return {"message": "Login success"}

    except Exception as e:
        return {"error": str(e)}

@app.get("/stocks")
def get_stocks():

    token = load_token()

    if not token:
        return {"error": "NO TOKEN - LOGIN REQUIRED"}

    try:
        kite.set_access_token(token)
    except Exception as e:
        return {"error": "TOKEN ERROR: " + str(e)}

    results = []

    for name, tk in stocks.items():
        try:
            data = kite.historical_data(
                tk,
                datetime.now() - timedelta(days=10),
                datetime.now(),
                "day"
            )

            if not data:
                continue

            latest = data[-1]["close"]

            results.append({
                "stock": name,
                "price": latest,
                "signal": "WORKING"
            })

        except Exception as e:
            print("ERROR:", name, e)

    # 🔥 FALLBACK (VERY IMPORTANT)
    if len(results) == 0:
        return {
            "error": "API FAILED",
            "debug": "Token exists but data fetch failed"
        }

    return {
        "count": len(results),
        "data": results
    }
