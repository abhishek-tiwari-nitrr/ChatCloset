"""Demo catalogue: fills an empty store with realistic products, real photos where available, else SVG images."""

import random
from pathlib import Path
from urllib.parse import quote

from pymongo.database import Database

ICONS = {
    "Shirt": "👔",
    "T-Shirt": "👕",
    "Polo": "👕",
    "Jeans": "👖",
    "Chinos": "👖",
    "Palazzo": "👖",
    "Dungaree": "👖",
    "Shorts": "🩳",
    "Pajama": "🩳",
    "Blazer": "🧥",
    "Jacket": "🧥",
    "Hoodie": "🧥",
    "Cardigan": "🧥",
    "Sweater": "🧶",
    "Dress": "👗",
    "Frock": "👗",
    "Skirt": "👗",
    "Kurti": "👚",
    "Blouse": "👚",
    "Top": "👚",
    "Saree": "🥻",
    "Jumpsuit": "🩱",
    "Romper": "🩱",
}
CATALOGUE = {
    "men": [
        "Shirt",
        "T-Shirt",
        "Polo",
        "Jeans",
        "Chinos",
        "Shorts",
        "Blazer",
        "Jacket",
        "Hoodie",
        "Sweater",
    ],
    "women": [
        "Dress",
        "Kurti",
        "Saree",
        "Blouse",
        "Top",
        "Skirt",
        "Palazzo",
        "Jumpsuit",
        "Cardigan",
        "Jacket",
    ],
    "kids": [
        "T-Shirt",
        "Frock",
        "Dungaree",
        "Shorts",
        "Pajama",
        "Romper",
        "Hoodie",
        "Sweater",
        "Jacket",
        "Shirt",
    ],
}
STYLES = [
    "Classic",
    "Modern",
    "Premium",
    "Casual",
    "Elegant",
    "Vintage",
    "Sporty",
    "Relaxed",
]
COLORS = {
    "Black": "#27272a",
    "White": "#f4f4f5",
    "Navy": "#1e3a8a",
    "Red": "#b91c1c",
    "Olive": "#4d7c0f",
    "Beige": "#d6c7a1",
    "Maroon": "#7f1d1d",
    "Mustard": "#ca8a04",
    "Grey": "#71717a",
    "Pink": "#db2777",
    "Teal": "#0f766e",
    "Brown": "#78350f",
}
SIZES = ["S", "M", "L", "XL", "XXL"]
TAGLINES = [
    "Comfortable fit for everyday wear.",
    "Soft, breathable fabric made to last.",
    "A timeless piece that pairs with everything.",
    "Tailored for a clean, modern silhouette.",
    "Lightweight and easy to care for.",
]
PHOTO_DIR = Path(
    "frontend/images/products"
)  # real photos made by scripts/generate_product_images.py


def photo_name(product_name: str) -> str:
    """'Classic Navy T-Shirt' -> 'classic-navy-t-shirt.webp' (the file name of that product's photo)."""
    return product_name.lower().replace(" ", "-") + ".webp"


def placeholder_image(icon: str, label: str, color: str) -> str:
    """Draw a small SVG picture (coloured background + icon + label) and return it as a data: URL."""
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 500'>"
        f"<rect width='400' height='500' fill='{color}'/>"
        "<circle cx='200' cy='220' r='130' fill='white' fill-opacity='0.85'/>"
        f"<text x='200' y='262' font-size='120' text-anchor='middle'>{icon}</text>"
        "<rect x='100' y='395' width='200' height='50' rx='25' fill='white' fill-opacity='0.9'/>"
        f"<text x='200' y='428' font-family='sans-serif' font-size='22' fill='#18181b' text-anchor='middle'>{label}</text>"
        "</svg>"
    )
    return "data:image/svg+xml;charset=utf-8," + quote(svg)


def demo_products(count: int = 120) -> list[dict]:
    """Build `count` products, spread evenly over the three categories. Same output every time."""
    rng = random.Random(42)
    color_names = list(COLORS)
    products = []
    for i in range(count):
        category = list(CATALOGUE)[i % 3]
        n = i // 3
        item = CATALOGUE[category][n % 10]
        style = STYLES[n % len(STYLES)]
        color = color_names[(n * 7 + i % 3) % len(color_names)]
        name = f"{style} {color} {item}"
        photo = PHOTO_DIR / photo_name(name)
        products.append(
            {
                "name": name,
                "description": f"{style} {item.lower()} in {color.lower()}. {TAGLINES[n % len(TAGLINES)]}",
                "price": rng.randrange(399, 5000, 50),
                "category": category,
                "sizes": sorted(
                    rng.sample(SIZES, k=rng.randint(2, 4)), key=SIZES.index
                ),
                "colors": [color],
                "image": f"/images/products/{photo.name}"
                if photo.exists()
                else placeholder_image(ICONS[item], item, COLORS[color]),
            }
        )
    return products


def seed_if_empty(db: Database, count: int = 120) -> None:
    """On first start, fill an empty catalogue so the store never looks blank."""
    if db.products.count_documents({}) == 0:
        db.products.insert_many(demo_products(count))
