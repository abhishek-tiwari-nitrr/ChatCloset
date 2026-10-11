"""ClothStore entry point: builds the FastAPI app, connects the routes and serves the website."""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.database import db
from backend.routes import products
from backend.seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once when the server starts: add demo products if the store is empty."""
    seed_if_empty(db)
    yield


app = FastAPI(title="ClothStore API", version="1.0.0", lifespan=lifespan)
app.include_router(products.router)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
