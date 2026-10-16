from fastapi import FastAPI

from app.api.wallet import router as wallet_router

app = FastAPI(
    title="Wallet API",
    description="REST API для управления балансом кошельков",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "Wallet API is running!"}


app.include_router(wallet_router)
