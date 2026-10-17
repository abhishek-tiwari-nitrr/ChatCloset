"""Shopping cart: one document per (session, product, size). Prices always come from the database."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from pymongo.database import Database

from backend.database import get_db, to_object_id
from backend.models import MAX_QUANTITY, Cart, CartAdd, CartUpdate

router = APIRouter(prefix="/api/cart", tags=["cart"])
SessionId = Annotated[str, Path(pattern=r"^[A-Za-z0-9-]{8,64}$")]


def load_cart(db: Database, session_id: str) -> dict:
    """Join the cart lines with live product data and work out the totals on the server."""
    lines = list(db.cart.find({"session_id": session_id}))
    ids = [to_object_id(line["product_id"]) for line in lines]
    products = {str(p["_id"]): p for p in db.products.find({"_id": {"$in": ids}})}
    items = []
    for line in lines:
        product = products.get(line["product_id"])
        if product is None:
            continue
        items.append(
            {
                "product_id": line["product_id"],
                "name": product["name"],
                "image": product["image"],
                "price": product["price"],
                "size": line["size"],
                "quantity": line["quantity"],
                "line_total": product["price"] * line["quantity"],
            }
        )
    return {
        "items": items,
        "total": sum(i["line_total"] for i in items),
        "count": sum(i["quantity"] for i in items),
    }


@router.get("/{session_id}", response_model=Cart)
def get_cart(session_id: SessionId, db: Database = Depends(get_db)):
    """Return the cart with names, images, prices and totals."""
    return load_cart(db, session_id)


@router.post("/{session_id}/items", response_model=Cart)
def add_item(session_id: SessionId, line: CartAdd, db: Database = Depends(get_db)):
    """Put a product in the cart, or raise its quantity if that product and size are already there."""
    product = db.products.find_one({"_id": to_object_id(line.product_id)})
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if line.size not in product["sizes"]:
        raise HTTPException(status_code=400, detail="That size is not available")
    key = {"session_id": session_id, "product_id": line.product_id, "size": line.size}
    current = db.cart.find_one(key) or {"quantity": 0}
    new_quantity = min(current["quantity"] + line.quantity, MAX_QUANTITY)
    db.cart.update_one(key, {"$set": {"quantity": new_quantity}}, upsert=True)
    return load_cart(db, session_id)


@router.put("/{session_id}/items", response_model=Cart)
def set_quantity(
    session_id: SessionId, line: CartUpdate, db: Database = Depends(get_db)
):
    """Set a line's quantity directly; 0 removes the line."""
    key = {"session_id": session_id, "product_id": line.product_id, "size": line.size}
    if line.quantity == 0:
        db.cart.delete_one(key)
    else:
        db.cart.update_one(key, {"$set": {"quantity": line.quantity}})
    return load_cart(db, session_id)
