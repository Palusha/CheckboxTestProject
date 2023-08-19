import pytest

from sqlalchemy import select

from src.database import database, auth_user


@pytest.mark.asyncio
async def test_register_user_creates_user(client):
    data = {
        "username": "test_username",
        "email": "test@example.com",
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "password": "secret_password",
    }

    response = await client.post("/auth/signup/", json=data)
    query = select(auth_user).where(auth_user.c.username == "test_username")
    user = await database.fetch_one(query)

    assert response.status_code == 201
    assert response.json() == {
        "username": "test_username",
        "email": "test@example.com",
        "first_name": "test_first_name",
        "last_name": "test_last_name",
    }
    assert user is not None
    assert user.username == "test_username"
    assert user.email == "test@example.com"
    assert user.first_name == "test_first_name"
    assert user.last_name == "test_last_name"


@pytest.mark.asyncio
async def test_register_user_returns_an_error_if_username_already_exists(client, user):
    data = {
        "username": "test_username",
        "email": "test2@example.com",
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "password": "secret_password",
    }

    response = await client.post("/auth/signup/", json=data)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "User with 'test_username' username already exists."
    }


@pytest.mark.asyncio
async def test_register_user_returns_an_error_if_email_already_exists(client, user):
    data = {
        "username": "test_username2",
        "email": "test@example.com",
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "password": "secret_password",
    }

    response = await client.post("/auth/signup/", json=data)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "User with 'test@example.com' email already exists."
    }


@pytest.mark.asyncio
async def test_register_user_does_not_create_user_if_required_data_is_missing(client):
    data = {
        "username": "test_username",
        "email": "test@example.com",
        "first_name": "test_first_name",
        "last_name": "test_last_name",
    }

    response = await client.post("/auth/signup/", json=data)
    query = select(auth_user).where(auth_user.c.username == "test_username")
    user = await database.fetch_one(query)

    assert response.status_code == 422
    assert user is None


@pytest.mark.asyncio
async def test_login_returns_auth_tokens(client, user):
    response = await client.post(
        "/auth/login/", json={"username": user.username, "password": "secret_password"}
    )

    response_data = response.json()

    assert response.status_code == 201
    assert "access_token" in response_data
    assert "refresh_token" in response_data


@pytest.mark.asyncio
async def test_login_returns_invalid_credentials_error(client, user):
    response = await client.post(
        "/auth/login/", json={"username": user.username, "password": "wrong_password"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid username or password"}


@pytest.mark.asyncio
async def test_refresh_creates_new_access_token(client, access_token, refresh_token):
    response = await client.post(
        "/auth/refresh/",
        headers={"authorization": f"Bearer {refresh_token}"},
    )

    response_data = response.json()

    assert response.status_code == 201
    assert access_token != response_data["access_token"]


@pytest.mark.asyncio
async def test_refresh_returns_error_message(client, access_token, refresh_token):
    response = await client.post(
        "/auth/refresh/",
        headers={"authorization": f"Bearer foo"},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Not enough segments"}


@pytest.mark.asyncio
async def test_user_returns_user_id(client, user, access_token):
    response = await client.get(
        "/auth/me/",
        headers={"authorization": f"Bearer {access_token}"},
    )

    response_data = response.json()

    assert response.status_code == 200
    assert response_data["user_id"] == user.id


@pytest.mark.asyncio
async def test_user_returns_invalid_token_message(client, access_token):
    response = await client.get(
        "/auth/me/",
        headers={"authorization": f"Bearer {access_token}123"},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Signature verification failed"}
