from datetime import datetime

import pytest_asyncio
from async_fastapi_jwt_auth import AuthJWT
from databases.interfaces import Record
from sqlalchemy import insert

from src.auth.security import hash_password
from src.database import database, auth_user


@pytest_asyncio.fixture()
async def user() -> Record | None:
    insert_query = (
        insert(auth_user)
        .values(
            {
                "username": "test_username",
                "email": "test@example.com",
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "password": hash_password("secret_password"),
                "created_at": datetime.utcnow(),
            }
        )
        .returning(auth_user)
    )

    return await database.fetch_one(insert_query)


@pytest_asyncio.fixture()
async def access_token(user) -> str:
    return await AuthJWT().create_access_token(subject=user.id)


@pytest_asyncio.fixture()
async def refresh_token(user) -> str:
    return await AuthJWT().create_refresh_token(subject=user.id)
