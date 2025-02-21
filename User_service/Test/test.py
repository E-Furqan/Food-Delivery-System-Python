import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from DatabaseConfig.databaseConfig import get_db,Base
from Model.model import User,user_roles,Role
from main import app


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
    headers = {"Content-Type": "application/json"}

    response = client.post("/user/register/user", json=user_data)
    print("helloooo:",response)
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
    credentials = {
        "email": "jane.doe@example.com",
        "password": "SecurePass123!"
    }

    response = client.post("/user/login", json=credentials)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_user_invalid_credentials(db_session):
    invalid_credentials = {
        "email": "jane.doe@example.com",
        "password": "WrongPassword!"
    }

    response = client.post("/user/login", json=invalid_credentials)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect password"