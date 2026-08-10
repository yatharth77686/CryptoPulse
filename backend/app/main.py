from fastapi import FastAPI

app = FastAPI(
    title="CryptoPulse API",
    description="AI-powered social media crypto intelligence system",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "CryptoPulse API is running!"
    }