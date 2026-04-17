from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stocks")
def get_stocks():
    try:
        # Always returns data (no crash)
        return [
            {"stock": "RELIANCE", "buy_price": 3000, "target": 3150, "stop_loss": 2900, "change_10d": 5.2, "expected_days": "2-4", "suggestion": "BUY", "confidence": "High"},
            {"stock": "HDFCBANK", "buy_price": 1600, "target": 1680, "stop_loss": 1550, "change_10d": 2.1, "expected_days": "3-5", "suggestion": "BUY (Weak)", "confidence": "Medium"},
            {"stock": "ICICIBANK", "buy_price": 1050, "target": 1100, "stop_loss": 1010, "change_10d": -1.5, "expected_days": "-", "suggestion": "SELL", "confidence": "Low"}
        ]
    except:
        return []