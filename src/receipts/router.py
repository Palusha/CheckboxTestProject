from datetime import datetime, date, time
from typing import Optional

from async_fastapi_jwt_auth import AuthJWT
from fastapi import status, APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from src.auth.service import get_user_by_id
from . import schemas, service, utils

router = APIRouter()


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.ReceiptResponse
)
async def create_receipt(receipt: schemas.Receipt, Authorize: AuthJWT = Depends()):
    await Authorize.jwt_required()
    user_id: int = await Authorize.get_jwt_subject()

    total = sum(product.total for product in receipt.products)

    if receipt.payment.amount < total:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount can not be lower than total price.",
        )

    rest = receipt.payment.amount - total

    receipt = await service.create_receipt(receipt, user_id, total, rest)
    return schemas.ReceiptResponse.model_validate(receipt, from_attributes=True)


@router.get("/me/")
async def list_receipts(
    from_date: Optional[datetime | date | time] = None,
    end_date: Optional[datetime | date | time] = None,
    min_total: Optional[int] = None,
    max_total: Optional[int] = None,
    payment_type: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    Authorize: AuthJWT = Depends(),
):
    await Authorize.jwt_required()
    user_id: int = await Authorize.get_jwt_subject()

    return await service.get_receipts(
        user_id, from_date, end_date, min_total, max_total, payment_type, limit, offset
    )


@router.get("/{receipt_id}/", response_class=PlainTextResponse)
async def get_receipt(receipt_id: int):
    receipt = await service.get_receipt_by_id(receipt_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found"
        )

    user = await get_user_by_id(receipt.user_id)

    return utils.generate_receipt(receipt, user)
