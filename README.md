# ChatCloset - an AI-assisted clothing store

ClothStore is a full-stack e-commerce showcase: a **FastAPI** backend, a **MongoDB** database, a framework-free **JavaScript** storefront, and an **AI shopping assistant** built with **Pydantic AI** that turns plain English ("men's jackets under 3000") into a safe database search.

![Python 3.14](https://img.shields.io/badge/python-3.14-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.143-009688?logo=fastapi&logoColor=white)
![MongoDB](<https://img.shields.io/badge/MongoDB-local%20or%20Atlas-47A248?logo=mongodb&logoColor=white>)
![Docker](https://img.shields.io/badge/Docker-compose%20ready-2496ED?logo=docker&logoColor=white)
![Pydantic AI](https://img.shields.io/badge/Pydantic%20AI-agents-E92063?logo=pydantic&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM%20inference-F55036?logoColor=white)
![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)

---

## Quick start (Windows, macOS, Linux)

You need **Python 3.14+** and **MongoDB** running locally.

```bash
# 1. MongoDB: install the free Community Server once (or use Docker, see below)
#    Windows:  winget install MongoDB.Server      (starts as a Windows service)
#    macOS:    brew tap mongodb/brew && brew install mongodb-community && brew services start mongodb-community
#    Linux:    https://www.mongodb.com/docs/manual/administration/install-on-linux/

# 2. Python environment
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt   # or: pip install -e ".[dev]"   (uses pyproject.toml, also installs the test tools)

# 3. Settings (all optional — defaults work)
copy .env.example .env            # macOS/Linux: cp .env.example .env

# 4. Run
python main.py
```

Open **http://127.0.0.1:8000**. On first start the store fills itself with 120 demo products, with drawn pictures, or real photos for the 50 newest once you have [generated them](#product-photos-optional).

* Admin page: **http://127.0.0.1:8000/#/admin**, unlocked with `ADMIN_API_KEY` from `.env` (default `change-me`, please change it).
* Interactive API docs: **http://127.0.0.1:8000/docs**
* Health check: **http://127.0.0.1:8000/api/health**

### Or: one command with Docker

```bash
docker compose up --build
```

This starts MongoDB and the app together. The app is published on `127.0.0.1:8000` only, and MongoDB is not published at all.

---


## The AI assistant

Set `LLM_MODEL` in `.env` to any [Pydantic AI](https://ai.pydantic.dev/) model string:

| Mode             | `.env`                                                                      | Notes                                                                                                                      |
| ---------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Groq (free tier) | `LLM_MODEL=groq:llama-3.3-70b-versatile` + `GROQ_API_KEY=...`             | Fast and accurate. Only the chat message is sent to Groq.                                                                  |
| No LLM           | `LLM_MODEL=off`                                                             | Rule-based keyword search, works offline.                                                                                  |

The LLM never writes database queries. It can only call one tool, `search_products(category, keyword, min_price, max_price)`, and the backend builds an escaped MongoDB filter from those typed arguments. If the LLM is unreachable, or answers without searching even though the message clearly asks for products, the backend runs the same search using a rule-based parser.

---

## Product photos (optional)

The demo products show drawn pictures that work offline. To give the **50 newest** products real photos, which every version lists first, add `OPENAI_API_KEY` to `.env` and run the one-off generator once. It costs about **$0.25** with `gpt-image-2` at low quality:

```bash
python scripts/generate_product_images.py --dry-run   # preview prompts and cost, no API call
python scripts/generate_product_images.py             # asks before spending; skips photos that exist
```

The photos are saved into `frontend/images/products/` of v1, v2 and v3. Then re-seed: Admin → **Reset demo catalogue**. Details: [product photos guide](docs/build-from-scratch/product-photos.md).

---

## Tests

Every version has a small, focused test suite (2–5 tests) that runs against an in-memory MongoDB, so no database or LLM is needed:

```bash
pip install -r requirements-dev.txt
pytest                      # final version (v3): health, admin key, AI assistant
cd versions/v1 && pytest    # v1: catalogue + filters
cd versions/v2 && pytest    # v2: search, cart, checkout, upload validation
```

---

## Documentation

- [High-Level Design](docs/HLD.md)
- [Low-Level Design](docs/LLD.md)
