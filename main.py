from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from kiteconnect import KiteConnect
from datetime import datetime, timedelta

app = FastAPI()

# ✅ CORS (IMPORTANT)
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

# 🔑 SESSION TOKEN
ACCESS_TOKEN = None

# 📊 50+ STOCKS (NSE LARGE + MID)
stocks = {
    "RELIANCE": 738561, "INFY": 408065, "TCS": 2953217,
    "HDFCBANK": 1333, "ICICIBANK": 4963, "SBIN": 779521,
    "AXISBANK": 1510401, "ITC": 424961, "ONGC": 633601,
    "TATAMOTORS": 884737, "LT": 2939649, "HCLTECH": 1850625,
    "WIPRO": 969473, "TECHM": 3465729, "SUNPHARMA": 857857,
    "CIPLA": 177665, "DRREDDY": 225537, "DIVISLAB": 2800641,
    "BAJFINANCE": 81153, "BAJAJFINSV": 4268801, "KOTAKBANK": 492033,
    "INDUSINDBK": 1346049, "POWERGRID": 3834113, "NTPC": 2977281,
    "COALINDIA": 5215745, "ADANIPORTS": 3861249, "ADANIENT": 6401,
    "TATASTEEL": 895745, "JSWSTEEL": 3001089, "HINDALCO": 348929,
    "UPL": 2889473, "PIDILITIND": 1102337, "ASIANPAINT": 60417,
    "NESTLEIND": 4598529, "BRITANNIA": 140033, "MARUTI": 2815745,
    "EICHERMOT": 232961, "HEROMOTOCO": 345089, "BHARTIARTL": 2714625,
    "TITAN": 897537, "ULTRACEMCO": 2952193, "SHREECEM": 794369,
    "GRASIM": 315393, "BPCL": 134657, "IOC": 415745,
    "GAIL": 4713217, "SIEMENS": 3155969, "ABB": 98049
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

        return RedirectResponse("https://stocks.ofesto.com/?login=success")

    except Exception as e:
        return {"error": str(e)}

# 📊 MAIN SCANNER
sector_map = {
    "RELIANCE": "Energy",
    "INFY": "IT",
    "TCS": "IT",
    "HDFCBANK": "Banking",
    "ICICIBANK": "Banking",
    "SBIN": "Banking",
    "AXISBANK": "Banking",
    "ITC": "FMCG",
    "ONGC": "Energy",
    "TATAMOTORS": "Auto",

    "LT": "Infrastructure",
    "HCLTECH": "IT",
    "WIPRO": "IT",
    "TECHM": "IT",

    "SUNPHARMA": "Pharma",
    "CIPLA": "Pharma",
    "DRREDDY": "Pharma",

    "DIVISLAB": "Pharma",
    "BAJFINANCE": "NBFC",
    "BAJAJFINSV": "NBFC",

    "KOTAKBANK": "Banking",
    "INDUSINDBK": "Banking",

    "POWERGRID": "Power",
    "NTPC": "Power",
    "COALINDIA": "Energy",

    "ADANIPORTS": "Logistics",
    "ADANIENT": "Conglomerate",

    "TATASTEEL": "Metal",
    "JSWSTEEL": "Metal",
    "HINDALCO": "Metal",

    "UPL": "Agro",
    "PIDILITIND": "Chemicals",

    "ASIANPAINT": "Paint",
    "NESTLEIND": "FMCG",
    "BRITANNIA": "FMCG",

    "MARUTI": "Auto",
    "EICHERMOT": "Auto",
    "HEROMOTOCO": "Auto",

    "BHARTIARTL": "Telecom",
    "TITAN": "Retail",

    "ULTRACEMCO": "Cement",
    "SHREECEM": "Cement",
    "GRASIM": "Cement",

    "BPCL": "Energy",
    "IOC": "Energy",
    "GAIL": "Energy",

    "SIEMENS": "Industrial",
    "ABB": "Industrial"
}
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
                highs = [c["high"] for c in data]
                volumes = [c["volume"] for c in data]

                latest = closes[-1]

                # ❌ FILTER PRICE
                if latest > 1500:
                    continue

                old = closes[0]
                change = ((latest - old) / old) * 100

                high_10 = max(highs[:-1])
                breakout = latest >= high_10 * 0.97

                avg_vol = sum(volumes[:-1]) / len(volumes[:-1])
                vol_boost = volumes[-1] > avg_vol * 1.1

                # 🎯 EXPECTED MOVE (RELAXED)
                expected_move = change * 1.2

                # ❌ REMOVE ONLY VERY BAD STOCKS
                if change < 0:
                    continue

                # 🔥 SCORING SYSTEM
                score = 0

                if change > 5:
                    score += 3
                elif change > 3:
                    score += 2
                elif change > 1:
                    score += 1

                if breakout:
                    score += 2

                if vol_boost:
                    score += 1

                # 📊 CLASSIFICATION
                if score >= 5:
                    signal = "TOP PICK 🔥"
                    confidence = "Very High"
                elif score >= 3:
                    signal = "STRONG BUY"
                    confidence = "High"
                elif score >= 2:
                    signal = "BUY"
                    confidence = "Medium"
                else:
                    signal = "WEAK BUY"
                    confidence = "Low"

                # 🎯 TARGET
                target = latest * (1 + expected_move / 100)
                stop_loss = latest * 0.95

                # ⏱️ DAYS
                if expected_move > 8:
                    days = "1-3 Days ⚡"
                elif expected_move > 5:
                    days = "2-4 Days 🚀"
                else:
                    days = "3-6 Days ⏳"

                results.append({
                    "stock": name,
                    "price": round(latest, 2),
                    "trend": round(change, 2),
                    "target": round(target, 2),
                    "stop_loss": round(stop_loss, 2),
                    "days": days,
                    "signal": signal,
                    "confidence": confidence,
                    "score": score,
                    "expected_move": round(expected_move, 2)
                })

            except Exception as e:
                print("Error:", name, e)

        # 🔥 SORT BEST FIRST
        results = sorted(results, key=lambda x: (x["score"], x["trend"]), reverse=True)

        # 🔥 ALWAYS GIVE MORE STOCKS
        top = [r for r in results if r["score"] >= 4]
        mid = [r for r in results if 2 <= r["score"] < 4]
        low = [r for r in results if r["score"] < 2]

        final = top + mid + low

        # LIMIT TO 50
        final = final[:50]

        return {
            "time": str(datetime.now()),
            "count": len(final),
            "data": final
        }

    except Exception as e:
        return {"error": str(e)}
