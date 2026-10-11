"""One-off helper: generate real product photos for the demo catalogue with the OpenAI Image API.

Run from anywhere:  python scripts/generate_product_images.py [--count 50] [--quality low] [--dry-run]
"""

import argparse
import base64
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
from backend.seed import PHOTO_DIR, demo_products, photo_name

TARGETS = [PHOTO_DIR, Path("versions/v1") / PHOTO_DIR, Path("versions/v2") / PHOTO_DIR]
PRICE_PER_IMAGE = {"low": 0.005, "medium": 0.041, "high": 0.165}
AUDIENCE = {"men": "men", "women": "women", "kids": "children"}


def prompt_for(product: dict) -> str:
    """Describe one product as a studio catalogue photo, worded the same way for every product."""
    style, color, item = product["name"].split(" ", 2)
    return (
        f"Professional e-commerce catalogue photo of a single {color.lower()} {item.lower()} for "
        f"{AUDIENCE[product['category']]}, {style.lower()} style, shown on an invisible mannequin, front view, centered, plain light grey studio background, soft even lighting, realistic fabric texture. No text, no logos, no watermark."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate product photos with the OpenAI Image API."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="how many products get a photo (the newest, shown first)",
    )
    parser.add_argument("--model", default="gpt-image-2")
    parser.add_argument("--quality", default="low", choices=list(PRICE_PER_IMAGE))
    parser.add_argument(
        "--dry-run", action="store_true", help="only print the prompts and the cost"
    )
    args = parser.parse_args()
    load_dotenv()

    newest = demo_products()[-args.count :]
    todo = [p for p in newest if not (PHOTO_DIR / photo_name(p["name"])).exists()]
    cost = len(todo) * PRICE_PER_IMAGE[args.quality]
    print(
        f"{len(todo)} photos to make with {args.model} ({args.quality}), about ${cost:.2f}. "
        f"{len(newest) - len(todo)} already exist."
    )
    if args.dry_run or not todo:
        for product in todo:
            print(f"  {photo_name(product['name'])}: {prompt_for(product)}")
        return
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit(
            "Set OPENAI_API_KEY in .env first (https://platform.openai.com/api-keys)."
        )
    if input("Continue? [y/N] ").strip().lower() != "y":
        return

    client = OpenAI()
    for number, product in enumerate(todo, 1):
        filename = photo_name(product["name"])
        try:
            result = client.images.generate(
                model=args.model,
                prompt=prompt_for(product),
                size="1024x1536",
                quality=args.quality,
                output_format="webp",
                output_compression=80,
            )
        except Exception as exc:
            print(f"[{number}/{len(todo)}] {filename}: FAILED ({exc})")
            continue
        data = base64.b64decode(result.data[0].b64_json)
        for folder in TARGETS:
            if folder.parent.parent.exists():
                folder.mkdir(parents=True, exist_ok=True)
                (folder / filename).write_bytes(data)
        print(f"[{number}/{len(todo)}] {filename}: saved ({len(data) // 1024} KB)")
    print("Done")


if __name__ == "__main__":
    main()
