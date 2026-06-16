import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_me_without_token_returns_401():
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_me_with_invalid_token_returns_401():
    with patch("dependencies.auth.verify_id_token", side_effect=Exception("invalid")):
        response = client.get("/auth/me", headers={"Authorization": "Bearer bad-token"})
    assert response.status_code == 401

def test_me_with_valid_token_returns_user():
    mock_decoded = {"uid": "abc123", "email": "user@test.com"}
    with patch("dependencies.auth.verify_id_token", return_value=mock_decoded):
        response = client.get("/auth/me", headers={"Authorization": "Bearer valid-token"})
    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == "abc123"
    assert data["email"] == "user@test.com"
