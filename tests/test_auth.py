import pytest
from unittest.mock import MagicMock


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.data.decode() == "LMS is running"


def test_register_page_get(client):
    response = client.get("/register")
    assert response.status_code == 200

def test_register_json_success(client, mocker):
    mock_service = mocker.patch("controllers.authController.userService")

    mock_user = MagicMock()
    mock_user.toDict.return_value = {
        "id": 1,
        "name": "Jane Doe",
        "email": "jane@example.com"
    }

    mock_service.register.return_value = mock_user


    payload = {
        "name" : "Jane Doe",
        "email": "jane@example.com",
        "password": "SecurePass123!",
        "confirmPassword": "SecurePass123!"
    }
    headers = {"Accept": "application/json"}


    response = client.post("/register", json=payload, headers=headers)


    assert response.status_code == 201

    data = response.get_json()
    assert data["success"]  is True
    assert data["message"] == "Registration successful"
    assert data["user"]["email"] == "jane@example.com"


def test_login_json_invalid_credentials(client, mocker):
    mock_service = mocker.patch("controllers.authController.userService")
    mock_service.authenticate.return_value = None


    payload = {
        "email" : "nonexistant@example.com",
        "password": "WrongPassword"
    }

    headers = {"Accept": "application/json"}

    response = client.post("/login", json=payload, headers=headers)


    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert data["message"] == "Invalid email or password"



def test_logout(client):
    headers = {"Accept": "application/json"}
    response = client.get("/logout", headers=headers)


    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Logged Out"