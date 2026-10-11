"""Product catalogue: browse all products, filtered by category and price."""
from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from backend.database import get_db, serialize
from backend.models import Category, Product

router = APIRouter(prefix="/api/products", tags=["products"])


def build_filter(category=None, min_price=None, max_price=None) -> dict:
    """Turn optional search options into a MongoDB filter."""
    query: dict = {}
    if category:
        query["category"] = category
    price = {}
    if min_price is not None:
        price["$gte"] = min_price
    if max_price is not None:
        price["$lte"] = max_price
    if price:
        query["price"] = price
    return query


@router.get("", response_model=list[Product])
def list_products(
    category: Category | None = None,
    min_price: int | None = Query(None, ge=0),
    max_price: int | None = Query(None, ge=0),
    db: Database = Depends(get_db),
):
    """List products, optionally filtered by category and price range."""
    query = build_filter(category, min_price, max_price)
    return [serialize(p) for p in db.products.find(query)]
