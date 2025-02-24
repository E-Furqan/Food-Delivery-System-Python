import pytest
import json
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from DatabaseConfig.databaseConfig import get_db,Base
from Model.model import User,user_roles,Role
from main import app
from Test.utils_of_test import create_user_for_test
from EnviornmentVariable import enVVar

# Test database (SQLite in-memory)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Create tables for testing
Base.metadata.create_all(bind=engine)

# Override get_db for testing
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module", autouse=True)
def create_test_roles():
    db = TestingSessionLocal()
    db.add(Role(role_type="customer"))
    db.add(Role(role_type="admin"))
    db.add(Role(role_type="deliverydriver"))
    db.commit()
    db.close()

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_user_success(create_test_roles):
    user_data = {
        "full_name": "John Doe",
        "user_name": "johndoe123",
        "email": "john.doe@example.com",
        "password": "StrongPassword123!",
        "phoneNumber": "1234567890",
        "address": "123 Main Street, Springfield",
        "roleStatus": "active",
        "activeRole": "customer",
        "roles": [
            {
                "role_id": 1
            }
        ]
    }

    response = client.post("/user/register/user", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == "john.doe@example.com"
    assert response.json()["activeRole"] == "customer"

def test_create_user_invalid_role():
    user_data = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "password": "password123",
        "user_name": "janedoe",
        "phoneNumber": "9876543210",
        "address": "456 Main St",
        "roleStatus": "active",
        "activeRole": "manager",  # Invalid role
        "roles": [{"role_type": "manager"}]
    }

    response = client.post("/user/register/user", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "At least one valid role is required."

def test_login_user_success(db_session):
    response = create_user_for_test(client)
    assert response.status_code == 200

    credentials = {
        "email": "john.doe@example.com",
        "password": "StrongPassword123!"
    }

    response = client.post("/user/login", json=credentials)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_user_invalid_credentials(db_session):
    response = create_user_for_test(client)
    assert response.status_code == 200

    invalid_credentials = {
        "email": "john.doe@example.com",
        "password": "WrongPassword!"
    }

    response = client.post("/user/login", json=invalid_credentials)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect password"

def test_login_user_invalid_credentials_user_not_found(db_session):
    response = create_user_for_test(client)
    assert response.status_code == 200

    invalid_credentials = {
        "email": "john123.doe@example.com",
        "password": "StrongPassword123!"
    }

    response = client.post("/user/login", json=invalid_credentials)
    assert response.status_code == 404
    assert response.json()["detail"] == "User with the email john123.doe@example.com is not available"



SECRET_KEY = enVVar.SECRET_KEY
ALGORITHM = enVVar.ALGORITHM

def generate_test_token():
    """Generate a JWT token for testing."""
    payload = {
        "id": 1,
        "role": "user",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@pytest.fixture
def test_token():
    return generate_test_token()

def test_delete_user_success(test_token, db_session):
    response = create_user_for_test(client)
    assert response.status_code == 200

    credentials = {
        "email": "john.doe@example.com",
        "password": "StrongPassword123!"
    }

    response = client.put(
        "/user/delete/user",
        json=credentials,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {test_token}"
        }
    )

    assert response.status_code == 200

def test_delete_user_invalid_password(test_token,db_session):
    response = create_user_for_test(client)
    assert response.status_code == 200


    credentials = {
        "email": "john.doe@example.com",
        "password": "WrongPassword!"
    }

    response = client.put(
        "/user/delete/user",
        json=credentials,
        headers={
            "Authorization": f"Bearer {test_token}"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect password"

def test_delete_user_user_not_found(test_token,db_session):

    credentials = {
        "email": "nonexistent@example.com",
        "password": "StrongPassword123!"
    }

    response = client.put(
        "/user/delete/user",
        json=credentials,
        headers={
            "Authorization": f"Bearer {test_token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User with the email nonexistent@example.com is not available"

def test_fetch_user_success(test_token,db_session):
    response = create_user_for_test(client)
    assert response.status_code == 200

    # Fetch the user
    response = client.get(
        "/user/fetch/user",
        headers={
            "Authorization": f"Bearer {test_token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["email"] == "john.doe@example.com"

def test_fetch_user_user_not_found(test_token,db_session):

    response = client.get(
        "/user/fetch/user",
        headers={
            "Authorization": f"Bearer {test_token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User with the id 1 is not available"






