"""MongoDB connection plus small helpers shared by every route."""

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from pymongo import MongoClient
from pymongo.database import Database

from backend import config

client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=3000, tz_aware=True)
db = client[config.MONGO_DB]


def get_db() -> Database:
    """FastAPI dependency that hands the database to a route (tests swap in an in-memory one)."""
    return db


def serialize(doc: dict) -> dict:
    """Turn MongoDB's ObjectId `_id` into a plain string `id` that JSON and the browser understand."""
    doc["id"] = str(doc.pop("_id"))
    return doc


def to_object_id(value: str) -> ObjectId:
    """Parse an id taken from the URL. A malformed id can never match a document, so answer 404."""
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(status_code=404, detail="Product not found") from None
