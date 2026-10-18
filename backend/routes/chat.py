"""AI shopping assistant: an LLM agent turns plain English into a safe product search."""

import logging
import re
from dataclasses import dataclass

from fastapi import APIRouter, Depends
from pydantic_ai import Agent, RunContext
from pymongo.database import Database

from backend import config
from backend.database import get_db, serialize
from backend.models import ChatRequest, ChatResponse
from backend.routes.products import build_filter
from backend.seed import ICONS

router = APIRouter(prefix="/api/chat", tags=["chat"])
log = logging.getLogger(__name__)

HELP_TEXT = (
    'I\'m the ClothStore assistant. Try: "men\'s jackets under 3000" or "kids hoodies".'
)
CATEGORY_WORDS = {
    "men": "men",
    "mens": "men",
    "man": "men",
    "women": "women",
    "womens": "women",
    "woman": "women",
    "ladies": "women",
    "kids": "kids",
    "kid": "kids",
    "children": "kids",
}
ITEM_WORDS = {name.lower() for name in ICONS}


@dataclass
class ShopDeps:
    db: Database
    found: list[dict] | None = (
        None  # filled by the tool; None means "the agent never searched"
    )


agent = Agent(
    deps_type=ShopDeps,
    instructions=(
        "You are the friendly shopping assistant of ClothStore, a clothing shop with three categories: men, women and kids. Whenever the user wants to see, find or buy clothes, call search_products. After searching, reply in one or two short sentences. The products are shown to the user as cards, so do not list them. Never invent products, prices or store policies. If the message has nothing to do with shopping for clothes, politely say you can only help with ClothStore products."
    ),
)


def find_products(
    db: Database, category=None, keyword=None, min_price=None, max_price=None
) -> list[dict]:
    """The one search used by both the agent and the keyword fallback (max 8 cards fit the chat)."""
    query = build_filter(
        category.lower() if category else None, keyword, min_price, max_price
    )
    return [serialize(p) for p in db.products.find(query).limit(8)]


@agent.tool
def search_products(
    ctx: RunContext[ShopDeps],
    category: str | None = None,
    keyword: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
) -> str:
    """Search the ClothStore catalogue.

    Args:
        category: 'men', 'women' or 'kids'.
        keyword: a clothing item such as 'shirt', 'jeans' or 'dress'.
        min_price: lowest price in rupees.
        max_price: highest price in rupees.
    """
    ctx.deps.found = find_products(ctx.deps.db, category, keyword, min_price, max_price)
    if not ctx.deps.found:
        return "No products matched."
    return "Found: " + ", ".join(f"{p['name']} (₹{p['price']})" for p in ctx.deps.found)


def parse_query(message: str) -> dict:
    """Rule-based understanding for when no LLM is available: find category, item and price limits."""
    text = message.lower().replace("₹", " ").replace(",", "")
    filters = {}
    for word in re.findall(r"[a-z-]+", text):
        if word in CATEGORY_WORDS:
            filters.setdefault("category", CATEGORY_WORDS[word])
        for candidate in (
            word,
            word[:-1],
            word[:-2],
        ):  # "shirts" -> "shirt", "dresses" -> "dress"
            if candidate in ITEM_WORDS:
                filters.setdefault("keyword", candidate)
    if match := re.search(r"between\s*(\d+)\s*(?:and|to|-)\s*(\d+)", text):
        filters["min_price"], filters["max_price"] = int(match[1]), int(match[2])
    if match := re.search(
        r"(?:under|below|less than|upto|up to|within)\s*(?:rs\.?|inr)?\s*(\d+)", text
    ):
        filters["max_price"] = int(match[1])
    if match := re.search(r"(?:over|above|more than)\s*(?:rs\.?|inr)?\s*(\d+)", text):
        filters["min_price"] = int(match[1])
    return filters


async def ask_llm(message: str, deps: ShopDeps) -> str | None:
    """Ask the LLM. Returns None when it is off, unreachable or answers with junk, so the caller can fall back."""
    if config.LLM_MODEL == "off":
        return None
    try:
        result = await agent.run(message, deps=deps, model=config.LLM_MODEL)
        return (
            None if result.output.lstrip().startswith("{") else result.output
        )  # small models may print a tool call as text
    except Exception as exc:
        log.warning("LLM unavailable, using keyword search instead: %s", exc)
        return None


@router.post("", response_model=ChatResponse)
async def chat(body: ChatRequest, db: Database = Depends(get_db)):
    """Answer a shopper's message with a short reply and, when relevant, matching products."""
    deps = ShopDeps(db=db)
    reply = await ask_llm(body.message, deps)
    filters = parse_query(body.message)
    if (
        deps.found is None and filters
    ):  # the LLM did not search, but the text clearly asks for products
        deps.found = find_products(db, **filters)
        reply = (
            "Here's what I found for you."
            if deps.found
            else "Sorry, nothing matched that. Try another item or price."
        )
    return {"reply": reply or HELP_TEXT, "products": deps.found or []}
