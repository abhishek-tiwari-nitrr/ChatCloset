"""Product catalogue: browsing plus create, update, delete and demo reset for the admin page."""

import math
import re
import uuid
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pymongo import ReturnDocument
from pymongo.database import Database

from backend import config
from backend.database import get_db, serialize, to_object_id
from backend.models import Category, Product, ProductPage
from backend.security import require_admin
from backend.seed import demo_products, placeholder_image

router = APIRouter(prefix="/api/products", tags=["products"])
admin_only = [Depends(require_admin)]
SORTS = {"newest": ("_id", -1), "price_asc": ("price", 1), "price_desc": ("price", -1)}


def build_filter(category=None, q=None, min_price=None, max_price=None) -> dict:
    """Turn optional search options into a MongoDB filter. User text is escaped, never run as a regex."""
    query: dict = {}
    if category:
        query["category"] = category
    if q:
        query["name"] = {"$regex": re.escape(q.strip()), "$options": "i"}
    price = {}
    if min_price is not None:
        price["$gte"] = min_price
    if max_price is not None:
        price["$lte"] = max_price
    if price:
        query["price"] = price
    return query


@router.get("", response_model=ProductPage)
def list_products(
    category: Category | None = None,
    q: str | None = Query(None, max_length=50),
    min_price: int | None = Query(None, ge=0),
    max_price: int | None = Query(None, ge=0),
    sort: Literal["newest", "price_asc", "price_desc"] = "newest",
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=48),
    db: Database = Depends(get_db),
):
    """Browse the catalogue with optional filters, sorting and pagination."""
    query = build_filter(category, q, min_price, max_price)
    total = db.products.count_documents(query)
    field, direction = SORTS[sort]
    cursor = (
        db.products.find(query)
        .sort(field, direction)
        .skip((page - 1) * limit)
        .limit(limit)
    )
    return {
        "items": [serialize(p) for p in cursor],
        "total": total,
        "page": page,
        "pages": math.ceil(total / limit),
    }


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: str, db: Database = Depends(get_db)):
    """Fetch one product for the detail page."""
    product = db.products.find_one({"_id": to_object_id(product_id)})
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return serialize(product)


def split_list(value: str) -> list[str]:
    """'S, M ,L' -> ['S', 'M', 'L']  (HTML forms send lists as comma-separated text)."""
    return [part.strip() for part in value.split(",") if part.strip()]


def product_form(
    name: str = Form(min_length=2, max_length=80),
    description: str = Form(max_length=500),
    price: int = Form(gt=0, le=1_000_000),
    category: Category = Form(),
    sizes: str = Form("S,M,L"),
    colors: str = Form("Black"),
) -> dict:
    """Validated form fields shared by 'create' and 'update'."""
    fields = {
        "name": name.strip(),
        "description": description.strip(),
        "price": price,
        "category": category,
        "sizes": split_list(sizes),
        "colors": split_list(colors),
    }
    if not fields["sizes"]:
        raise HTTPException(status_code=422, detail="Choose at least one size")
    return fields


def detect_image_type(data: bytes) -> str | None:
    """Recognise JPEG, PNG or WebP from the file's first bytes (the browser-sent type can lie)."""
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return None


async def save_image(image: UploadFile) -> str:
    """Check an uploaded image, store it in the uploads folder under a random name, return its URL."""
    data = await image.read(config.MAX_UPLOAD_BYTES + 1)
    if len(data) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image is too large")
    extension = detect_image_type(data)
    if extension is None:
        raise HTTPException(
            status_code=400, detail="Image must be a JPEG, PNG or WebP file"
        )
    filename = f"{uuid.uuid4().hex}{extension}"
    (Path(config.UPLOAD_DIR) / filename).write_bytes(data)
    return f"/uploads/{filename}"


@router.post("", response_model=Product, status_code=201, dependencies=admin_only)
async def create_product(
    fields: dict = Depends(product_form),
    image: UploadFile | None = File(None),
    db: Database = Depends(get_db),
):
    """Add a product. The image is optional; without one we draw a placeholder."""
    if image and image.filename:
        fields["image"] = await save_image(image)
    else:
        fields["image"] = placeholder_image("🛍️", fields["category"].title(), "#71717a")
    db.products.insert_one(fields)
    return serialize(fields)


@router.put("/{product_id}", response_model=Product, dependencies=admin_only)
async def update_product(
    product_id: str,
    fields: dict = Depends(product_form),
    image: UploadFile | None = File(None),
    db: Database = Depends(get_db),
):
    """Replace a product's details; keep the current image unless a new one is uploaded."""
    if image and image.filename:
        fields["image"] = await save_image(image)
    product = db.products.find_one_and_update(
        {"_id": to_object_id(product_id)},
        {"$set": fields},
        return_document=ReturnDocument.AFTER,
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return serialize(product)


@router.delete("/{product_id}", status_code=204, dependencies=admin_only)
def delete_product(product_id: str, db: Database = Depends(get_db)):
    """Remove a product from the catalogue."""
    if db.products.delete_one({"_id": to_object_id(product_id)}).deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")


@router.post("/reset-demo", dependencies=admin_only)
def reset_demo(db: Database = Depends(get_db)):
    """Wipe the catalogue and refill it with fresh demo products."""
    db.products.delete_many({})
    db.products.insert_many(demo_products())
    return {
        "message": "Demo catalogue restored",
        "count": db.products.count_documents({}),
    }
