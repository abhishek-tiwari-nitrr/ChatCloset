"""v3 tests: health check, admin protection and the AI shopping assistant."""
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import FunctionModel

from backend import config
from backend.routes.chat import agent, parse_query
from backend.seed import seed_if_empty

FORM = {"name": "Linen Shirt", "description": "Breathable summer shirt", "price": "1299", "category": "men"}


def test_health_reports_database_ok(client):
    assert client.get("/api/health").json() == {"status": "ok", "database": "ok"}


def test_admin_routes_need_the_right_key(client):
    assert client.post("/api/products", data=FORM).status_code == 401
    assert client.post("/api/products", data=FORM, headers={"X-Admin-Key": "wrong"}).status_code == 401
    assert client.post("/api/products", data=FORM, headers={"X-Admin-Key": "test-key"}).status_code == 201


def test_parse_query_understands_plain_english():
    assert parse_query("Show me men's shirts under ₹2,000") == {"category": "men", "keyword": "shirt", "max_price": 2000}
    assert parse_query("hello there") == {}


def test_chat_falls_back_to_keyword_search_without_llm(client, db):
    seed_if_empty(db)
    body = client.post("/api/chat", json={"message": "kids hoodies under 5000"}).json()
    assert body["products"]
    assert all(p["category"] == "kids" and "Hoodie" in p["name"] for p in body["products"])


def test_agent_tool_call_returns_products(client, db, monkeypatch):
    seed_if_empty(db)

    def fake_llm(messages, info):  # turn 1: ask for the tool; turn 2: answer in text
        if len(messages) == 1:
            return ModelResponse(parts=[ToolCallPart("search_products", {"category": "women", "max_price": 1500})])
        return ModelResponse(parts=[TextPart("Here are some women's picks under ₹1500!")])

    monkeypatch.setattr(config, "LLM_MODEL", "function")
    with agent.override(model=FunctionModel(fake_llm)):
        body = client.post("/api/chat", json={"message": "something nice for my sister"}).json()
    assert body["reply"] == "Here are some women's picks under ₹1500!"
    assert body["products"] and all(p["category"] == "women" and p["price"] <= 1500 for p in body["products"])
