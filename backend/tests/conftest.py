import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database.base import Base
from app.dependencies.database import get_db
from app.main import app


# ---------------------------------------------------------
# Test database
# ---------------------------------------------------------

test_database_url = settings.database_url.rsplit("/", 1)[0] + "/mycropai_test"

test_engine = create_engine(
    test_database_url,
    echo=False,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


# ---------------------------------------------------------
# Override FastAPI database dependency
# ---------------------------------------------------------

def override_get_db():
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ---------------------------------------------------------
# Test client
# ---------------------------------------------------------

@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------
# Clean test database after each test
# ---------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_database():
    yield

    with test_engine.begin() as connection:
        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    farms,
                    refresh_sessions,
                    users
                RESTART IDENTITY
                CASCADE
                """
            )
        )


# ---------------------------------------------------------
# Authenticated client
# ---------------------------------------------------------

class AuthenticatedClient:
    def __init__(self, client, user):
        self.client = client
        self.user = user

    def get(self, *args, **kwargs):
        return self.client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.client.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self.client.put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.client.delete(*args, **kwargs)


@pytest.fixture
def authenticated_client(client):
    client = TestClient(app)

    email = f"test-{uuid.uuid4()}@example.com"
    password = "TestPassword123!"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Farmer",
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    user = register_response.json()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    client.headers.update(
        {
            "Authorization": f"Bearer {access_token}"
        }
    )

    return AuthenticatedClient(
        client=client,
        user=type(
            "TestUser",
            (),
            {"id": user["id"]},
        )(),
    )

@pytest.fixture
def second_authenticated_client(client):
    client = TestClient(app)
    
    email = f"test-{uuid.uuid4()}@example.com"
    password = "TestPassword123!"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Second Farmer",
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    user = register_response.json()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    client.headers.update(
        {
            "Authorization": f"Bearer {access_token}"
        }
    )

    return AuthenticatedClient(
        client=client,
        user=type(
            "TestUser",
            (),
            {"id": user["id"]},
        )(),
    )