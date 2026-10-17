"""Orders: checkout turns the cart into an order with a price snapshot, then empties the cart."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from backend.database import get_db, serialize
from backend.models import Order
from backend.routes.cart import SessionId, load_cart

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/{session_id}/checkout", response_model=Order, status_code=201)
def checkout(session_id: SessionId, db: Database = Depends(get_db)):
    """Create an order from the cart. Prices are copied so later price changes never alter it."""
    cart = load_cart(db, session_id)
    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Your cart is empty")
    order = {
        "session_id": session_id,
        "items": [
            {
                key: item[key]
                for key in ("product_id", "name", "price", "size", "quantity")
            }
            for item in cart["items"]
        ],
        "total": cart["total"],
        "status": "placed",
        "created_at": datetime.now(timezone.utc),
    }
    db.orders.insert_one(order)
    db.cart.delete_many({"session_id": session_id})
    return serialize(order)


@router.get("/{session_id}", response_model=list[Order])
def list_orders(session_id: SessionId, db: Database = Depends(get_db)):
    """Order history for this browser, newest first."""
    return [
        serialize(o)
        for o in db.orders.find({"session_id": session_id})
        .sort("created_at", -1)
        .limit(50)
    ]
