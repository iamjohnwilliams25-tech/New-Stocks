from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kiteconnect import KiteConnect
import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔴 PUT YOUR REAL KEYS HERE
API_KEY = "v4se78490za52f7m"
API_SECRET = "hestwv676imoo7wcf443vmj70s7muhzr"
ACCESS_TOKEN = "FuPaS2aQ5rxXNP1BRoB80IGIy7OWYqIS"

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

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
            {"symbol": "NSE:HCLTECH", "sector": "IT"},

            {"symbol": "NSE:RELIANCE", "sector": "Energy"},
            {"symbol": "NSE:ONGC", "sector": "Energy"},
            {"symbol": "NSE:BPCL", "sector": "Energy"},
            {"symbol": "NSE:IOC", "sector": "Energy"},

            {"symbol": "NSE:TATAMOTORS", "sector": "Auto"},
            {"symbol": "NSE:HEROMOTOCO", "sector": "Auto"},
            {"symbol": "NSE:EICHERMOT", "sector": "Auto"},

            {"symbol": "NSE:ITC", "sector": "FMCG"},
            {"symbol": "NSE:DABUR", "sector": "FMCG"},
            {"symbol": "NSE:BRITANNIA", "sector": "FMCG"},

            {"symbol": "NSE:SUNPHARMA", "sector": "Pharma"},
            {"symbol": "NSE:CIPLA", "sector": "Pharma"},
            {"symbol": "NSE:DRREDDY", "sector": "Pharma"},
        ]

        result = []

        today = datetime.date.today()
        from_date = today - datetime.timedelta(days=15)

        for s in stocks:
            symbol = s["symbol"]
            sector = s["sector"]

            try:
                # 🔥 GET HISTORICAL DATA (REAL TREND)
                hist = kite.historical_data(
                    instrument_token=kite.ltp(symbol)[symbol]["instrument_token"],
                    from_date=from_date,
                    to_date=today,
                    interval="day"
                )

                if len(hist) < 5:
                    continue

                old_price = hist[0]["close"]
                latest_price = hist[-1]["close"]

                change = ((latest_price - old_price) / old_price) * 100

                # 🔥 FILTER PRICE < 1500
                if latest_price > 1500:
                    continue

                # 🔥 SMART SIGNAL
                if change > 5:
                    suggestion = "BUY"
                    confidence = "High"
                    days = "2-4"
                elif change > 1:
                    suggestion = "BUY (Weak)"
                    confidence = "Medium"
                    days = "3-5"
                else:
                    suggestion = "SELL"
                    confidence = "Low"
                    days = "-"

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
                    "expected_days": days,
                    "suggestion": suggestion,
                    "confidence": confidence
                })

            except:
                continue

        # 🔥 SORT BEST FIRST
        result = sorted(result, key=lambda x: x["change_10d"], reverse=True)

        return result

    except Exception as e:
        return {"error": str(e)}
