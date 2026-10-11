"""Pydantic models: the exact shape of the data going in and out of the API."""
from typing import Literal

from pydantic import BaseModel

Category = Literal["men", "women", "kids"]


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: int
    category: Category
    sizes: list[str]
    colors: list[str]
    image: str
