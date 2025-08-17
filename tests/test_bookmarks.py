import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_all_bookmarks_unauthorized():
    response = client.get("/bookmarks/")
    assert response.status_code == 401

def test_get_bookmark_unauthorized():
    response = client.get("/bookmarks/1")
    assert response.status_code == 401

# Dodaj kolejne testy po zaimplementowaniu autoryzacji i tworzenia użytkownika/tokenu
