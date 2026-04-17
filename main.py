from fastapi import FastAPI
import yfinance as yf

app = FastAPI()

stocks = ["RELIANCE.NS","HDFCBANK.NS","ICICIBANK.NS","TATAMOTORS.NS","INFY.NS","SBIN.NS"]

@app.get("/stocks")
def get_stocks():
    data = []
    
    for s in stocks:
        try:
            ticker = yf.Ticker(s)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                continue
            
            price = float(hist["Close"].iloc[-1])
            
            data.append({
                "stock": s.replace(".NS",""),
                "buy_price": round(price * 1.01,2),
                "target": round(price * 1.05,2),
                "stop_loss": round(price * 0.97,2)
            })
        
        except Exception as e:
            print(f"Error with {s}: {e}")
            continue

    return data