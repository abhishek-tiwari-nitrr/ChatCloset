# ChatCloset

**A clothing catalogue built with FastAPI and MongoDB: 120 products with real photos, filtered by category and price.**

![Python 3.14](https://img.shields.io/badge/python-3.14-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.143-009688?logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-local%20or%20Atlas-47A248?logo=mongodb&logoColor=white)
![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)


---

## Features

- **Product API**: `GET /api/products` with optional `category` (`men` / `women` / `kids`), `min_price` and `max_price`. Inputs are validated (an invalid category or negative price gives `422`), and interactive docs are at `/docs`.
- **Self-seeding catalogue**: on first start an empty database is filled with 120 deterministic demo products (40 per category, unique names, sizes, prices from ₹399 to ₹4,999).
- **Real product photos**: 120 consistent studio-style WebP photos, generated once with the OpenAI Image API and shipped in the repository. Without them the store falls back to drawn SVG pictures, so it still works offline.

## Tech stack

| Layer | Technology |
| --- | --- |
| API | [FastAPI](https://fastapi.tiangolo.com/) & [Pydantic](https://docs.pydantic.dev/) & [uvicorn](https://www.uvicorn.org/) |
| Database | [MongoDB](https://www.mongodb.com/) (local server or Atlas) via [pymongo](https://pymongo.readthedocs.io/) |
| Frontend | HTML & CSS (grid) & vanilla ES modules |
| Images | WebP photos made with the [OpenAI Image API](https://developers.openai.com/api/docs/guides/image-generation), SVG fallback |
| Tooling | Python 3.14 & [uv](https://docs.astral.sh/uv/) & pytest & mongomock |

---

## Getting started

### Prerequisites

- **Python 3.14+** and **[uv](https://docs.astral.sh/uv/)** (or plain `pip`)
- **MongoDB**: either a local server (`winget install MongoDB.Server` on Windows) or a free
  [MongoDB Atlas](https://www.mongodb.com/atlas) cluster

### Install

```bash
git clone https://github.com/abhishek-tiwari-nitrr/ChatCloset.git
cd ChatCloset
uv sync --extra dev          # or: pip install -e ".[dev]"
```

### Configure

Copy `.env.example` to `.env` and set:

| Variable | Default | Purpose |
| --- | --- | --- |
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection string (local or `mongodb+srv://…` for Atlas) |
| `MONGO_DB` | `clothstore` | Database name |
| `OPENAI_API_KEY` | – | Only needed to (re)generate product photos |

`.env` is git-ignored. Never commit real credentials.

### Run

```bash
uv run python main.py
```

Open **http://127.0.0.1:8000** for the storefront, or **http://127.0.0.1:8000/docs** for the interactive API.

---

## API

`GET /api/products`

| Query parameter | Type | Example |
| --- | --- | --- |
| `category` | `men` · `women` · `kids` | `?category=women` |
| `min_price` | integer ≥ 0 (₹) | `?min_price=1000` |
| `max_price` | integer ≥ 0 (₹) | `?max_price=2499` |

```http
GET /api/products?category=kids&max_price=999

200 OK
[{"id": "…", "name": "Casual Mustard Frock", "description": "…", "price": 799, "category": "kids",
  "sizes": ["M", "L", "XL", "XXL"], "colors": ["Mustard"], "image": "/images/products/casual-mustard-frock.webp"}, …]
```

Errors follow FastAPI's format. An invalid parameter gives `422` with a `detail` list.

---

## Product photos

The 120 photos in `frontend/images/products/` are committed, so **you don't need an OpenAI key** to run the store. To regenerate or extend them:

```bash
python scripts/generate_product_images.py --count 120 --dry-run   # preview prompts and cost, no API call
python scripts/generate_product_images.py --count 120             # asks before spending; skips existing photos
```

Uses `gpt-image-2` at low quality (about $0.005 per photo). Delete a `.webp` to regenerate just that product.

---

## Testing

```bash
uv run pytest -v
```

The tests replace the database with mongomock through FastAPI's `dependency_overrides`, so they need neither MongoDB nor the internet.

## Documentation

- [High-Level Design](docs/HLD.md)
- [Low-Level Design](docs/LLD.md)
