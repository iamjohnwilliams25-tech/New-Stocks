from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ IMPORTANT: Fix for WordPress (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary working data (so everything runs perfectly)
stocks_data = [
    {"stock": "RELIANCE", "price": 2950},
    {"stock": "HDFCBANK", "price": 1600},
    {"stock": "ICICIBANK", "price": 1050},
    {"stock": "TATAMOTORS", "price": 950},
    {"stock": "INFY", "price": 1500},
    {"stock": "SBIN", "price": 800}
]

@app.get("/stocks")
def get_stocks():
    result = []
    
    for s in stocks_data:
        price = s["price"]
        
        result.append({
            "stock": s["stock"],
            "buy_price": round(price * 1.01, 2),
            "target": round(price * 1.05, 2),
            "stop_loss": round(price * 0.97, 2),
            "confidence": "Medium"
        })
    
    return result