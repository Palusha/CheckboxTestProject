from datetime import datetime, date, time

from databases.interfaces import Record
from sqlalchemy import insert, select
from typing import Optional

from src.database import database, receipts
from .schemas import Receipt, ReceiptResponse


async def create_receipt(
    receipt: Receipt, user_id: int, total: float, rest: float
) -> ReceiptResponse | None:
    products_json = [product.model_dump() for product in receipt.products]
    payment_json = receipt.payment.model_dump()

    insert_query = (
        insert(receipts)
        .values(
            {
                "user_id": user_id,
                "products": products_json,
                "payment": payment_json,
                "total": total,
                "rest": rest,
            }
        )
        .returning(receipts)
    )
    receipt = await database.fetch_one(insert_query)

    return ReceiptResponse(
        products=receipt["products"],
        payment=receipt["payment"],
        id=receipt.id,
        total=receipt.total,
        rest=receipt.rest,
        created_at=receipt.created_at,
    )


async def get_receipts(
    user_id: int,
    from_date: Optional[datetime | date | time],
    end_date: Optional[datetime | date | time],
    min_total: Optional[str],
    max_total: Optional[str],
    payment_type: Optional[str],
    limit: int,
    offset: int,
) -> Record:
    select_query = select(receipts).where(receipts.c.user_id == user_id)

    if from_date is not None:
        select_query = select_query.where(receipts.c.created_at >= from_date)

    if end_date is not None:
        select_query = select_query.where(receipts.c.created_at <= end_date)

    if min_total is not None:
        select_query = select_query.where(receipts.c.total >= min_total)

    if max_total is not None:
        select_query = select_query.where(receipts.c.total <= max_total)

    if payment_type is not None:
        select_query = select_query.where(
            receipts.c.payment["type"].astext == payment_type
        )

    select_query = select_query.limit(limit).offset(offset)

    return await database.fetch_all(select_query)


async def get_receipt_by_id(receipt_id: int) -> Record | None:
    select_query = select(receipts).where(receipts.c.id == receipt_id)

    return await database.fetch_one(select_query)
