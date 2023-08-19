from datetime import datetime

from databases.interfaces import Record
from fastapi import status, HTTPException
from sqlalchemy import insert, select

from src.database import auth_user, database
from .schemas import RegisterUser
from .security import check_password, hash_password


async def create_user(user: RegisterUser) -> Record | None:
    insert_query = (
        insert(auth_user)
        .values(
            {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "password": hash_password(user.password),
                "created_at": datetime.utcnow(),
            }
        )
        .returning(auth_user)
    )

    return await database.fetch_one(insert_query)


async def get_user_by_id(user_id: int) -> Record | None:
    select_query = select(auth_user).where(auth_user.c.id == user_id)

    return await database.fetch_one(select_query)


async def get_user_by_username(username: str) -> Record | None:
    select_query = select(auth_user).where(auth_user.c.username == username)

    return await database.fetch_one(select_query)


async def get_user_by_email(email: str) -> Record | None:
    select_query = select(auth_user).where(auth_user.c.email == email)

    return await database.fetch_one(select_query)


async def authenticate_user(auth_data: RegisterUser) -> Record:
    user = await get_user_by_username(auth_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password",
        )

    if not check_password(auth_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password",
        )

    return user
