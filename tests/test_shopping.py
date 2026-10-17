"""search with pagination, the cart, checkout and image-upload validation."""

from backend.seed import seed_if_empty


def first_product(client, db):
    seed_if_empty(db, count=30)
    return client.get("/api/products").json()["items"][0]


def test_search_returns_one_page_of_matches(client, db):
    seed_if_empty(db, count=30)
    page = client.get("/api/products", params={"q": "jacket", "limit": 2}).json()
    assert page["total"] == 3 and page["pages"] == 2 and len(page["items"]) == 2
    assert all("Jacket" in p["name"] for p in page["items"])


def test_adding_the_same_item_twice_increases_quantity(client, db):
    product = first_product(client, db)
    url = "/api/cart/test-session-1/items"
    client.post(url, json={"product_id": product["id"], "size": product["sizes"][0]})
    cart = client.post(
        url,
        json={"product_id": product["id"], "size": product["sizes"][0], "quantity": 2},
    ).json()
    assert len(cart["items"]) == 1 and cart["items"][0]["quantity"] == 3
    assert cart["total"] == product["price"] * 3


def test_checkout_creates_order_and_empties_cart(client, db):
    product = first_product(client, db)
    client.post(
        "/api/cart/test-session-2/items",
        json={"product_id": product["id"], "size": product["sizes"][0], "quantity": 2},
    )
    order = client.post("/api/orders/test-session-2/checkout")
    assert order.status_code == 201 and order.json()["total"] == product["price"] * 2
    assert client.get("/api/cart/test-session-2").json()["items"] == []
    assert (
        client.post("/api/orders/test-session-2/checkout").status_code == 400
    )  # the cart is empty now


def test_upload_rejects_a_file_that_is_not_an_image(client):
    form = {
        "name": "Plain Tee",
        "description": "Cotton tee",
        "price": "499",
        "category": "men",
    }
    fake_png = (
        "evil.png",
        b"<script>alert(1)</script>",
        "image/png",
    )  # says PNG, but the bytes are not
    assert (
        client.post("/api/products", data=form, files={"image": fake_png}).status_code
        == 400
    )
