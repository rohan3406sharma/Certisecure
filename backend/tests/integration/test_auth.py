from __future__ import annotations
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.db.base import Base
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def registered_user(client):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "test@certisecure.io", "password": "securepass123", "full_name": "Test User", "role": "user"})
    assert resp.status_code == 201
    return resp.json()


@pytest_asyncio.fixture
async def auth_tokens(client, registered_user):
    resp = await client.post("/api/v1/auth/login",
        data={"username": "test@certisecure.io", "password": "securepass123"})
    assert resp.status_code == 200
    return resp.json()


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "new@certisecure.io", "password": "mypassword", "role": "user"})
    assert resp.status_code == 201
    assert resp.json()["data"]["email"] == "new@certisecure.io"

@pytest.mark.asyncio
async def test_register_duplicate_email(client, registered_user):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "test@certisecure.io", "password": "anotherpass", "role": "user"})
    assert resp.status_code == 400

@pytest.mark.asyncio
async def test_register_invalid_email(client):
    resp = await client.post("/api/v1/auth/register", json={"email": "bad", "password": "pass1234", "role": "user"})
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_register_short_password(client):
    resp = await client.post("/api/v1/auth/register", json={"email": "x@x.com", "password": "short", "role": "user"})
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_login_success(client, registered_user):
    resp = await client.post("/api/v1/auth/login",
        data={"username": "test@certisecure.io", "password": "securepass123"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client, registered_user):
    resp = await client.post("/api/v1/auth/login",
        data={"username": "test@certisecure.io", "password": "wrong"})
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_login_unknown_email(client):
    resp = await client.post("/api/v1/auth/login",
        data={"username": "nobody@x.com", "password": "pass1234"})
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token(client, auth_tokens):
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": auth_tokens["refresh_token"]})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

@pytest.mark.asyncio
async def test_refresh_invalid_token(client):
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": "garbage"})
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_me_authenticated(client, auth_tokens):
    resp = await client.get("/api/v1/auth/me",
        headers={"Authorization": f"Bearer {auth_tokens['access_token']}"})
    assert resp.status_code == 200
    assert resp.json()["data"]["email"] == "test@certisecure.io"

@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_me_invalid_token(client):
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer fake.token"})
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_update_own_profile(client, auth_tokens):
    resp = await client.patch("/api/v1/users/me",
        headers={"Authorization": f"Bearer {auth_tokens['access_token']}"},
        json={"full_name": "Updated Name"})
    assert resp.status_code == 200
    assert resp.json()["data"]["full_name"] == "Updated Name"

@pytest.mark.asyncio
async def test_user_cannot_self_escalate_role(client, auth_tokens):
    resp = await client.patch("/api/v1/users/me",
        headers={"Authorization": f"Bearer {auth_tokens['access_token']}"},
        json={"role": "admin"})
    assert resp.status_code == 403
