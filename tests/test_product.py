"""catalogue and the category / price filters."""

from backend.seed import seed_if_empty


def product(name, price, category):
    return {
        "name": name,
        "description": "",
        "price": price,
        "category": category,
        "sizes": ["M"],
        "colors": ["Black"],
        "image": "",
    }


def test_list_returns_the_seeded_catalogue(client, db):
    seed_if_empty(db, count=9)
    products = client.get("/api/products").json()
    assert len(products) == 9
    assert "id" in products[0] and "_id" not in products[0]


def test_filter_by_category_and_price(client, db):
    db.products.insert_many(
        [
            product("Cheap Men Tee", 499, "men"),
            product("Pricey Men Blazer", 5999, "men"),
            product("Cheap Kids Tee", 299, "kids"),
        ]
    )
    found = client.get(
        "/api/products", params={"category": "men", "max_price": 1000}
    ).json()
    assert [p["name"] for p in found] == ["Cheap Men Tee"]


def test_unknown_category_is_rejected(client):
    assert client.get("/api/products", params={"category": "aliens"}).status_code == 422
