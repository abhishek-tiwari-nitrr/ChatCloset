# Low-Level Design

---

## 1. Repository layout

```
├── .env.example
├── .gitignore
├── .python-version
├── LICENSE
├── main.py                          uvicorn entry point
├── pyproject.toml
├── pytest.ini                       settings for the tests
├── README.md
├── uv.lock
├── requirements.txt
├── backend/                         the shop assistant (Python)
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── seed.py
│   └── routes/
│       ├── __init__.py
│       └── products.py
├── frontend/                        the shop window
│   ├── index.html
│   ├── images/products/*.webp
│   ├── css/style.css
│   └── js/app.js
├── scripts/                         Generate images
│   └── generate_product_images.py
└── tests/
    ├── conftest.py
    └── test_catalog.py
```

---

