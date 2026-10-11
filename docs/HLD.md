# High-Level Design

---

## 1. Purpose and scope

ClothStore demonstrates a complete, production-shaped web application that a single engineer can run, read and explain end to end: catalogue browsing, cart, checkout, order history, an admin back office, and an LLM shopping assistant that converts natural language into a safe, structured database query.

---

## 2. System context

```mermaid
flowchart LR
    shopper([Shopper<br/>browser]) -->|HTTP 127.0.0.1:8000| app[ChatCloset v1<br/>FastAPI app]
    app -->|pymongo| db[(MongoDB<br/>local or Atlas)]
    dev([One-Off]) -.->|scripts/generate_product_images.py| openai[OpenAI Image API]
    openai -.->|WebP photos| files[(frontend/images/products)]
    app --> files
```

The OpenAI Image API is used **once, offline from the app**, to create the photos. The running store never calls it.

---

## 3. Architecture

```mermaid
flowchart TB
    subgraph Browser
        page[index.html<br/>header · tabs · price filter · grid]
        js[app.js<br/>fetch + escaped render]
    end
    subgraph Server [Python process: uvicorn]
        static[StaticFiles mount /<br/>html, css, js, product photos]
        router[products router<br/>GET /api/products]
        dbmod[database.py<br/>client · get_db · serialize]
        seed[seed.py<br/>demo catalogue · photo lookup · SVG]
        life[lifespan<br/>seed_if_empty]
    end
    mongo[(MongoDB<br/>products)]
    page --> js -->|GET /api/products?…| router --> dbmod --> mongo
    page -.->|GET /, /css, /js, /images| static
    life --> seed --> mongo
```

**One process, one origin.** FastAPI serves the API under `/api` and the storefront and photos under `/`. There is no CORS configuration and the frontend uses relative URLs.

## 4. Key flow: filter the catalogue

```mermaid
sequenceDiagram
    participant U as Shopper
    participant B as app.js
    participant A as FastAPI
    participant M as MongoDB
    U->>B: clicks "Men" (hash → #men) or picks "Under ₹1,000"
    B->>B: read hash + dropdown, build query string
    B->>A: GET /api/products?category=men&min_price=0&max_price=999
    A->>A: validate (Category literal, int ≥ 0), else 422
    A->>A: build_filter → {"category":"men","price":{"$gte":0,"$lte":999}}
    A->>M: find(filter)
    M-->>A: matching documents
    A-->>B: JSON array of Product (id instead of _id)
    B->>B: escape + render cards, update title, count, active tab
```

---

## 5. Data design

A single collection, `products`, holds one document per product:
`{_id, name, description, price:int, category, sizes[], colors[], image}`.

* Prices are whole rupees (`int`), so there are no floating-point rounding issues.
* `image` is a short URL path to a static WebP photo (`/images/products/casual-mustard-frock.webp`), or an inline SVG data URL when no photo exists.

---

## 6. Technology decisions

| Concern   | Choice                           | Rationale                                                                                             |
| --------- | -------------------------------- | ----------------------------------------------------------------------------------------------------- |
| API       | FastAPI                          | Typed parameters give validation and OpenAPI docs. Dependency injection makes the database swappable. |
| Database  | MongoDB (pymongo)                | Products are natural documents with embedded lists. Atlas or local through one URI.                   |
| Frontend  | Vanilla JS + CSS grid            | No toolchain. About 50 lines cover fetch, render and events.                                          |
| Images    | Static WebP files + SVG fallback | Small documents, cacheable files, offline-capable.                                                    |
| Packaging | uv + pyproject.toml + uv.lock    | Reproducible installs with pinned versions.                                                           |
| Tests     | pytest + TestClient + mongomock  | Real HTTP semantics without a database server.                                                        |

---

