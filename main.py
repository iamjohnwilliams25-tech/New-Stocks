from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kiteconnect import KiteConnect

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 PUT YOUR KEYS HERE
API_KEY = "PASTE_YOUR_API_KEY"
API_SECRET = "PASTE_YOUR_API_SECRET"

kite = KiteConnect(api_key=API_KEY)

# 1️⃣ Get login URL
@app.get("/login")
def login():
    return {"login_url": kite.login_url()}


# 2️⃣ Generate access token
@app.get("/generate-token")
def generate_token(request_token: str):
    data = kite.generate_session(request_token, api_secret=API_SECRET)
    access_token = data["access_token"]

    # save token in memory
    kite.set_access_token(access_token)

    return {"access_token": access_token}


# 3️⃣ Get live stock data
@app.get("/stocks")
def get_stocks():
    try:
        instruments = [
            "NSE:RELIANCE",
            "NSE:HDFCBANK",
            "NSE:ICICIBANK",
            "NSE:TATAMOTORS",
            "NSE:SBIN"
        ]

        quotes = kite.ltp(instruments)

        result = []

        for key, value in quotes.items():
            price = value["last_price"]

            result.append({
                "stock": key.replace("NSE:", ""),
                "buy_price": round(price * 1.01, 2),
                "target": round(price * 1.05, 2),
                "stop_loss": round(price * 0.97, 2),
                "change_10d": 0,
                "expected_days": "2-4",
                "suggestion": "BUY",
                "confidence": "High"
            })

        return result

    except Exception as e:
        return {"error": str(e)}