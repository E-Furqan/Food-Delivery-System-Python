import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)

def test_refresh_token_success(mocker):
    mock_response = {
        "access_token": "new_access_token",
        "token_type": "bearer"
    }

    mocker.patch("Client.authClient.requests.post", return_value=mocker.Mock(status_code=200, json=lambda: mock_response))

    response = client.post("/user/refresh/token", json={"refresh_token": "valid_refresh_token"})

    assert response.status_code == 200
    assert response.json()["access_token"] == "new_access_token"
    assert response.json()["token_type"] == "bearer"


def test_refresh_token_invalid_token(mocker):
    mocker.patch("Client.authClient.requests.post", return_value=mocker.Mock(status_code=401, json=lambda: {"detail": "Invalid token"}))

    response = client.post("/user/refresh/token", json={"refresh_token": "invalid_refresh_token"})

    assert response.status_code == 500
    assert "error in authentication service" in response.json()["detail"]



def test_refresh_token_missing_token():
    response = client.post("/user/refresh/token", json={})
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]
