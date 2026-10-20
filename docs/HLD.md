# High-Level Design

---

## 1. Purpose and scope

ClothStore demonstrates a complete, production-shaped web application that a single engineer can run, read and explain end to end: catalogue browsing, cart, checkout, order history, an admin back office, and an LLM shopping assistant that converts natural language into a safe, structured database query.

---

## 2. System context

```mermaid
flowchart LR
    shopper([Shopper<br/>browser]) -->|HTTP, port 8000| app
    admin([Store admin<br/>browser]) -->|HTTP + X-Admin-Key| app
    subgraph machine [Your computer]
        app[ClothStore app<br/>FastAPI + static website]
        db[(MongoDB)]
    end
    app -->|pymongo| db
    app -.->|optional, HTTPS| groq[Groq cloud LLM]
```

The OpenAI Image API is used **once, offline from the app**, to create the photos. The running store never calls it.

---

## 3. Architecture

### 3.1 Container view

```mermaid
flowchart TB
    subgraph Browser
        spa[Single-page app<br/>vanilla ES modules<br/>hash router]
    end
    subgraph Server [Python process: uvicorn]
        static[StaticFiles<br/> and /uploads]
        mw[Middleware<br/>request log, JSON 500 handler]
        subgraph Routers ["/api"]
            products[products]
            cart[cart]
            orders[orders]
            chat[chat + Pydantic AI agent]
            health[health]
        end
        sec[security<br/>require_admin]
        dbmod[database<br/>get_db, helpers]
        seed[seed<br/>demo data + SVG]
    end
    mongo[(MongoDB<br/>products, cart, orders)]
    fs[(uploads/ folder)]
    llm[LLM provider]

    spa -->|fetch JSON| mw --> Routers
    spa -->|GET html/js/css/images| static
    products --> sec
    Routers --> dbmod --> mongo
    products --> fs
    static --> fs
    chat --> llm
    chat -->|search_products tool| products
    seed --> mongo
```

**One process, one origin.** FastAPI serves the API under `/api` and the storefront and photos under `/`. There is no CORS configuration and the frontend uses relative URLs.


### 3.2 Components and responsibilities

| Component                                       | Responsibility                                                | Key design choice                                                                                                                                                                                   |
| ----------------------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontend SPA** (`frontend/`)          | Rendering, routing, user interaction                          | No framework or build step. Pages are functions that render template strings. Every interpolated value passes through `escapeHtml`. One delegated click handler serves all "Add to cart" buttons. |
| **API layer** (`backend/routes/*`)      | HTTP contracts, validation, business rules                    | FastAPI and Pydantic models validate every input. Routers are thin, with business rules in small pure helpers (`build_filter`, `load_cart`, `parse_query`).                                   |
| **Data access** (`backend/database.py`) | MongoDB client, `get_db` dependency, id conversion, indexes | The database is injected per request (`Depends(get_db)`), so tests replace it with mongomock in one line.                                                                                         |
| **Security** (`backend/security.py`)    | Admin authorisation                                           | A shared-secret header (`X-Admin-Key`) compared in constant time and applied declaratively to write routes.                                                                                       |
| **AI agent** (`backend/routes/chat.py`) | Natural language to product search                            | The LLM gets exactly one typed tool and no raw query access. A deterministic parser is the fallback and safety net.                                                                                 |
| **Seeder** (`backend/seed.py`)          | First-run demo catalogue                                      | Deterministic (fixed RNG seed). Real photos (generated once, stored as files) where present, else self-contained SVG data URLs, so it needs no network.                                             |
| **Configuration** (`backend/config.py`) | Environment-driven settings                                   | 12-factor style: env vars, optional `.env`, a safe default for every value.

---

## 4. Key flow

### 4.1 Browse and add to cart

```mermaid
sequenceDiagram
    participant B as Browser
    participant A as FastAPI
    participant M as MongoDB
    B->>A: GET /api/products?category=men&q=jacket&page=1
    A->>A: validate query params, build escaped filter
    A->>M: count_documents(filter), find(filter).sort().skip().limit()
    M-->>A: 12 documents
    A-->>B: {items, total, page, pages}
    B->>A: POST /api/cart/{session}/items {product_id, size, quantity}
    A->>M: find product, check size is offered
    A->>M: upsert cart line, quantity capped at 10
    A->>M: load cart lines + products ($in)
    A-->>B: {items, total, count} with totals computed on the server
```

### 4.2 Checkout

The server re-reads the cart and live prices, copies a snapshot of each line into the order, writes the order, then clears the cart. The client never sends prices.

### 4.3 AI assistant with fallback

```mermaid
flowchart TD
    msg[POST /api/chat message] --> llmq{LLM_MODEL off?}
    llmq -- no --> run[agent.run with ShopDeps]
    run -->|tool call| tool[search_products<br/>category, keyword, min, max]
    tool --> filter[build_filter: escaped, typed] --> mongo[(MongoDB)]
    run -->|error: no key, network, rate limit| fail[reply = None]
    llmq -- yes --> fail
    run --> done{did the agent search?}
    fail --> done
    done -- yes --> respond[reply + products]
    done -- no --> parse[parse_query rules]
    parse -->|filters found| search[same search] --> respond
    parse -->|nothing found| respond2[LLM reply or help text]
```

---

## 5. Data design

| Collection   | One document per              | Key fields                                                            | Indexes                                   |
| ------------ | ----------------------------- | --------------------------------------------------------------------- | ----------------------------------------- |
| `products` | product                       | name, description, price (int ₹), category, sizes[], colors[], image | `{category, price}`                     |
| `cart`     | (session, product, size) line | session_id, product_id, size, quantity                                | unique `{session_id, product_id, size}` |
| `orders`   | order                         | session_id, items[] (price snapshot), total, status, created_at       | `{session_id, created_at desc}`         |


---

## 6. Technology decisions

| Concern           | Choice                                                                         | Alternatives considered                     | Why                                                                                                                                                                          |
| ----------------- | ------------------------------------------------------------------------------ | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Web framework     | FastAPI                                                                        | Flask, Django                               | Type-driven validation, automatic OpenAPI docs at `/docs`, async support for the LLM call, dependency injection used by the tests.                                         |
| Database          | MongoDB (pymongo)                                                              | PostgreSQL, SQLite                          | Matches the document-shaped data, flexible during iteration, and the "text-to-NoSQL" theme of the project. SQLite would remove the install step but lose that learning goal. |
| Frontend          | Vanilla ES modules                                                             | React, Vue                                  | No toolchain to install or explain. About 600 lines of JS. Modules give structure without a framework.                                                                       |
| LLM orchestration | Pydantic AI                                                                    | LangChain, raw SDK                          | Typed tools from Python signatures, dependency injection into tools, provider-agnostic model strings (Groq, Ollama, OpenAI…), and first-class test models.                  |
| Images            | Local `uploads/` folder, `frontend/images/products/` photos, SVG data URLs | Base64 in MongoDB (the original design), S3 | Keeps documents small, works offline, and is simple to back up.                                                                                                              |

