"""ClothStore entry point: builds the FastAPI app, connects the routes and serves the website."""

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pymongo.database import Database
from pymongo.errors import PyMongoError

from backend import config
from backend.database import create_indexed, db, get_db
from backend.routes import cart, chat, orders, products
from backend.seed import seed_if_empty

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s"
)
log = logging.getLogger("clothstore")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once when the server starts: add demo products if the store is empty."""
    try:
        create_indexed(db)
    except PyMongoError as e:
        raise RuntimeError("Cannot reach MongoDB. Check .env for MONGO_URI.") from e
    seed_if_empty(db)
    yield


app = FastAPI(title="ClothStore API", version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every api call with its status code and how long it took."""
    started = time.perf_counter()
    response = await call_next(request)
    if request.url.path.startswith("/api"):
        elapsed_ms = (time.perf_counter() - started) * 1000
        log.info(
            "%s %s -> %s in %.0f ms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
    return response


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    "Any crash become a clean json 500. Details go to the log not the User."
    log.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"details": "Something went wrong"})


@app.get("/api/health", tags=["health"])
def health(database: Database = Depends(get_db)):
    try:
        database.command("ping")
    except PyMongoError:
        return JSONResponse(
            status_code=503, content={"status": "error", "database": "unrachable"}
        )
    return {"status": "ok", "database": "ok"}


app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(chat.router)

Path(config.UPLOAD_DIR).mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=config.UPLOAD_DIR), name="uploads")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
