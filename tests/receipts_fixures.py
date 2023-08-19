import pytest_asyncio
from databases.interfaces import Record
from sqlalchemy import insert

from src.database import database, receipts


@pytest_asyncio.fixture()
async def receipts_list(user) -> list[Record] | None:
    insert_query = (
        insert(receipts)
        .values(
            [
                {
                    "user_id": user.id,
                    "products": [
                        {
                            "name": "Test table",
                            "price": 500,
                            "quantity": 1,
                            "total": 500,
                        },
                        {
                            "name": "Test chair",
                            "price": 299.99,
                            "quantity": 3,
                            "total": 899.97,
                        },
                    ],
                    "payment": {"type": "cashless", "amount": 2000},
                    "total": 1399.97,
                    "rest": 600.03,
                },
                {
                    "user_id": user.id,
                    "products": [
                        {
                            "name": "Test headphone",
                            "price": 1000,
                            "quantity": 2,
                            "total": 2000,
                        },
                        {
                            "name": "Test microphone",
                            "price": 400.99,
                            "quantity": 3,
                            "total": 1202.97,
                        },
                    ],
                    "payment": {"type": "cash", "amount": 3500},
                    "total": 3202.97,
                    "rest": 297.03,
                },
            ]
        )
        .returning(receipts)
    )

    return await database.fetch_all(insert_query)


@pytest_asyncio.fixture()
async def receipt(user) -> list[Record] | None:
    insert_query = (
        insert(receipts)
        .values(
            {
                "user_id": user.id,
                "products": [
                    {"name": "Test table", "price": 500, "quantity": 1, "total": 500},
                    {
                        "name": "Test chair",
                        "price": 299.99,
                        "quantity": 3,
                        "total": 899.97,
                    },
                ],
                "payment": {"type": "cashless", "amount": 2000},
                "total": 1399.97,
                "rest": 600.03,
            }
        )
        .returning(receipts)
    )

    return await database.fetch_one(insert_query)
