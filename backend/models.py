"""Pydantic models: the exact shape of the data going in and out of the API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["men", "women", "kids"]
MAX_QUANTITY = 5


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: int
    category: Category
    sizes: list[str]
    colors: list[str]
    image: str


class ProductPage(BaseModel):
    items: list[Product]
    total: int
    page: int
    pages: int


class CartAdd(BaseModel):
    product_id: str
    size: str
    quantity: int = Field(1, ge=1, le=MAX_QUANTITY)


class CartUpdate(CartAdd):
    quantity: int = Field(ge=0, le=MAX_QUANTITY)


class CartLine(BaseModel):
    product_id: str
    name: str
    image: str
    price: int
    size: str
    quantity: int
    line_total: int


class Cart(BaseModel):
    items: list[CartLine]
    total: int
    count: int


class OrderLine(BaseModel):
    product_id: str
    name: str
    price: int
    size: str
    quantity: int


class Order(BaseModel):
    id: str
    items: list[OrderLine]
    total: int
    status: str
    created_at: datetime


class ChatRequest(BaseModel):
    message: str = Field(min_length=3, max_length=500)


class ChatResponse(BaseModel):
    reply: str
    products: list[Product]
