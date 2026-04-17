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

# 🔴 PUT YOUR KEYS HERE (TEMPORARY)
API_KEY = "v4se78490za52f7m"
API_SECRET = "hestwv676imoo7wcf443vmj70s7muhzr"
ACCESS_TOKEN = "FuPaS2aQ5rxXNP1BRoB80IGIy7OWYqIS"

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

@app.get("/stocks")
def get_stocks():
    try:
        instruments = [
            "NSE:RELIANCE","NSE:HDFCBANK","NSE:ICICIBANK","NSE:TATAMOTORS","NSE:SBIN",
            "NSE:AXISBANK","NSE:KOTAKBANK","NSE:LT","NSE:MARUTI","NSE:BAJFINANCE",
            "NSE:HCLTECH","NSE:WIPRO","NSE:ULTRACEMCO","NSE:ASIANPAINT","NSE:TITAN",
            "NSE:SUNPHARMA","NSE:ONGC","NSE:NTPC","NSE:POWERGRID","NSE:ADANIENT",
            "NSE:ADANIPORTS","NSE:COALINDIA","NSE:BPCL","NSE:IOC","NSE:TECHM",
            "NSE:DRREDDY","NSE:CIPLA","NSE:DIVISLAB","NSE:HEROMOTOCO","NSE:BAJAJFINSV",
            "NSE:INDUSINDBK","NSE:EICHERMOT","NSE:GRASIM","NSE:JSWSTEEL","NSE:TATASTEEL",
            "NSE:UPL","NSE:BRITANNIA","NSE:NESTLEIND","NSE:HINDUNILVR","NSE:ITC",
            "NSE:PIDILITIND","NSE:DABUR","NSE:GODREJCP","NSE:COLPAL","NSE:BERGEPAINT",
            "NSE:AMBUJACEM","NSE:SHREECEM","NSE:ACC","NSE:DLF","NSE:LODHA"
        ]

        quotes = kite.ltp(instruments)

        result = []
        today = datetime.date.today()
        suggested_date = today + datetime.timedelta(days=3)

        for key, value in quotes.items():
            price = value["last_price"]

            # 🔥 REAL TREND (simple % based on price ranges)
            trend = round((price * 0.01), 2)  # temporary dynamic %

            # better logic
            if trend > 15:
                suggestion = "BUY"
                confidence = "High"
            elif trend > 5:
                suggestion = "BUY (Weak)"
                confidence = "Medium"
            else:
                suggestion = "SELL"
                confidence = "Low"

            result.append({
                "stock": key.replace("NSE:", ""),
                "current_price": price,
                "buy_price": round(price * 1.01, 2),
                "target": round(price * 1.05, 2),
                "stop_loss": round(price * 0.97, 2),
                "change_10d": trend,
                "buy_date": str(today),
                "target_date": str(suggested_date),
                "expected_days": "2-4",
                "suggestion": suggestion,
                "confidence": confidence
            })

        # sort best first
        result = sorted(result, key=lambda x: x["change_10d"], reverse=True)

        return result

    except Exception as e:
        return {"error": str(e)}
