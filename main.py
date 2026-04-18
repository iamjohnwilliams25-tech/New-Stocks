from fastapi import FastAPI
from kiteconnect import KiteConnect

app = FastAPI()

API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"

kite = KiteConnect(api_key=API_KEY)

@app.get("/")
def home():
    return {"message": "API is running"}

@app.get("/login")
def login():
    return {"login_url": kite.login_url()}

@app.get("/generate-token")
def generate_token(request_token: str):
    data = kite.generate_session(request_token, api_secret=API_SECRET)
    access_token = data["access_token"]
    return {"access_token": access_token}
