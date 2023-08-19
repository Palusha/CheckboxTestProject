from datetime import datetime
from enum import Enum

from pydantic import BaseModel, computed_field, Field


class PaymentType(str, Enum):
    CASH = "cash"
    CASHLESS = "cashless"


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    price: float = Field(ge=1)
    quantity: int = Field(ge=1)

    @computed_field
    def total(self) -> float:
        return self.price * self.quantity


class Payment(BaseModel):
    type: PaymentType
    amount: float = Field(ge=1)


class Receipt(BaseModel):
    products: list[Product] = Field(min_length=1)
    payment: Payment


class ReceiptResponse(Receipt):
    id: int
    total: float = Field(ge=1)
    rest: float = Field(ge=0)
    created_at: datetime = datetime.utcnow()
