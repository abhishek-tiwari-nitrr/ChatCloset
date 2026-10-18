"""Shared test setup."""

import os

os.environ["LLM_MODEL"] = "off"  # tests must never call a real LLM
os.environ["ADMIN_API_KEY"] = "test-key"  # must be set BEFORE `from main import app`

import mongomock
import pytest
from fastapi.testclient import TestClient

from backend.database import get_db
from main import app


@pytest.fixture
def db():
    return mongomock.MongoClient().clothstore


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()
