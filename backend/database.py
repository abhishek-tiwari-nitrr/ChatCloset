"""MongoDB connection plus small helpers shared by every route."""
from pymongo import MongoClient
from pymongo.database import Database

from backend import config

client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=3000)
db = client[config.MONGO_DB]


def get_db() -> Database:
    """FastAPI dependency that hands the database to a route (tests swap in an in-memory one)."""
    return db


def serialize(doc: dict) -> dict:
    """Turn MongoDB's ObjectId `_id` into a plain string `id` that JSON and the browser understand."""
    doc["id"] = str(doc.pop("_id"))
    return doc
