# High-Level Design

---

## 1. Purpose and scope

ClothStore demonstrates a complete, production-shaped web application that a single engineer can run, read and explain end to end: catalogue browsing, cart, checkout, order history, an admin back office, and an LLM shopping assistant that converts natural language into a safe, structured database query.

---

## 2. System context

```mermaid
flowchart LR
    shopper([Shopper<br/>browser]) -->|HTTP 127.0.0.1:8000| app[ClothStore<br/>FastAPI app]
    admin([Store admin<br/>same browser]) -->|HTTP, no auth yet| app
    app -->|pymongo| db[(MongoDB)]
    app -->|read/write| fs[(uploads/ folder)]
```

The OpenAI Image API is used **once, offline from the app**, to create the photos. The running store never calls it.

---

## 3. Architecture

```mermaid
flowchart TB
    subgraph Browser [Browser: single-page app]
        main[main.js<br/>boot + delegated Add handler]
        router[router.js<br/>hash → page]
        pages[pages/<br/>home · product · cart · orders · admin]
        api[api.js<br/>request + endpoints]
        state[state.js<br/>sessionId in localStorage]
    end
    subgraph Server [Python process: uvicorn]
        static[StaticFiles / and /uploads]
        products[products router]
        cart[cart router]
        orders[orders router]
        dbmod[database.py]
        seed[seed.py]
    end
    mongo[(MongoDB<br/>products · cart · orders)]
    fs[(uploads/)]

    main --> router --> pages --> api
    api --> state
    api -->|JSON / multipart| products & cart & orders
    products --> fs
    static --> fs
    products & cart & orders --> dbmod --> mongo
    orders -->|load_cart| cart
    seed --> mongo
```

**One process, one origin.** FastAPI serves the API under `/api` and the storefront and photos under `/`. There is no CORS configuration and the frontend uses relative URLs.

## 4. Key flow

### 4.1 Browse → product → cart

```mermaid
sequenceDiagram
    participant B as Browser
    participant P as /api/products
    participant C as /api/cart
    participant M as MongoDB
    B->>P: GET ?q=jacket&sort=price_asc&page=1&limit=12
    P->>M: count_documents(f) + find(f).sort().skip().limit()
    P-->>B: {items, total, page, pages}
    B->>P: GET /{id} (product page)
    P-->>B: Product
    B->>C: POST /{session}/items {product_id, size, quantity}
    C->>M: product exists? size offered? (404/400)
    C->>M: read line, new qty = min(old + q, 10), upsert
    C->>M: lines + products($in)
    C-->>B: {items, total, count}
```

### 4.2 Checkout

```mermaid
sequenceDiagram
    participant B as Browser
    participant O as /api/orders
    participant M as MongoDB
    B->>O: POST /{session}/checkout
    O->>M: load_cart (live prices)
    alt cart empty
        O-->>B: 400 "Your cart is empty"
    else
        O->>M: insert order {items snapshot, total, status: placed, created_at UTC}
        O->>M: delete cart lines
        O-->>B: 201 Order
    end
```

---

## 5. Data design

| Collection   | Document                                                                                      | Written by                           | Read by                        |
| ------------ | --------------------------------------------------------------------------------------------- | ------------------------------------ | ------------------------------ |
| `products` | `{name, description, price, category, sizes[], colors[], image}`                            | seed, admin create/update/reset      | list, detail, cart join, admin |
| `cart`     | `{session_id, product_id, size, quantity}`                                                  | add, set-quantity, checkout (delete) | cart, checkout                 |
| `orders`   | `{session_id, items[{product_id, name, price, size, quantity}], total, status, created_at}` | checkout                             | order history                  |

---

## 6. Technology decisions

| Concern          | Choice                                                      | Reason                                                                                                   |
| ---------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| File uploads     | `python-multipart` + local `uploads/` + `StaticFiles` | Standard browser form uploads. Files stay outside the database, so documents stay small. Works offline.  |
| Image validation | Magic-byte sniffing                                         | The client's filename and `Content-Type` are untrusted, while the file's first bytes are hard to fake. |
| Shopper identity | Random UUID in `localStorage`                             | Lets the shop run without accounts. Enough for a single-machine demo.                                    |
| Client routing   | Hash routes (`#/cart`)                                    | No server routing needed, and Back/Forward and deep links work.                                          |
| Pagination       | `skip`/`limit` with a total count                       | Simple, and adequate for small catalogues.                                                               |

---
