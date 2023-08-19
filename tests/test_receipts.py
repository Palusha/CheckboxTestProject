from datetime import datetime

import pytest
from sqlalchemy import select

from src.database import receipts, database
from src.receipts.utils import generate_receipt


@pytest.mark.asyncio
async def test_create_receipt_creates_receipt(client, access_token):
    data = {
        "products": [
            {"name": "Test table", "price": 500, "quantity": 1},
            {"name": "Test chair", "price": 299.99, "quantity": 3},
        ],
        "payment": {"type": "cashless", "amount": 2000},
    }

    response = await client.post(
        "/receipts/", headers={"authorization": f"Bearer {access_token}"}, json=data
    )

    response_data = response.json()

    assert response.status_code == 201
    assert "id" in response_data
    assert response_data["products"] == [
        {"name": "Test table", "price": 500.0, "quantity": 1, "total": 500.0},
        {"name": "Test chair", "price": 299.99, "quantity": 3, "total": 899.97},
    ]
    assert response_data["payment"] == {"type": "cashless", "amount": 2000.0}
    assert response_data["total"] == 1399.97
    assert response_data["rest"] == 600.03
    assert (
        datetime.strptime(response_data["created_at"], "%Y-%m-%dT%H:%M:%S.%f").date()
        == datetime.utcnow().date()
    )

    query = select(receipts).where(receipts.c.id == response_data["id"])
    receipt = await database.fetch_one(query)

    assert receipt is not None
    assert receipt["products"] == [
        {"name": "Test table", "price": 500.0, "quantity": 1, "total": 500.0},
        {"name": "Test chair", "price": 299.99, "quantity": 3, "total": 899.97},
    ]
    assert receipt["payment"] == {
        "type": "cashless",
        "amount": 2000.0,
    }
    assert receipt.total == 1399.97
    assert receipt.rest == 600.03
    assert receipt.created_at.date() == datetime.utcnow().date()


@pytest.mark.asyncio
async def test_create_receipt_does_not_create_receipt_if_required_data_is_missing(
    client, access_token
):
    data = {
        "products": [
            {"name": "Test table", "price": 500, "quantity": 1},
            {"name": "Test chair", "price": 299.99, "quantity": 3},
        ],
    }

    response = await client.post(
        "/receipts/", headers={"authorization": f"Bearer {access_token}"}, json=data
    )

    assert response.status_code == 422

    query = select(receipts).where(
        receipts.c.products
        == [
            {"name": "Test table", "price": 500, "quantity": 1},
            {"name": "Test chair", "price": 299.99, "quantity": 3},
        ]
    )

    assert await database.fetch_one(query) is None


@pytest.mark.asyncio
async def test_create_receipt_returns_an_error_if_payment_amout_is_less_then_total(
    client, access_token
):
    data = {
        "products": [
            {"name": "Test table", "price": 500, "quantity": 1},
            {"name": "Test chair", "price": 299.99, "quantity": 3},
        ],
        "payment": {"type": "cashless", "amount": 200},
    }

    response = await client.post(
        "/receipts/", headers={"authorization": f"Bearer {access_token}"}, json=data
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Payment amount can not be lower than total price."
    }


@pytest.mark.asyncio
async def test_create_receipt_returns_an_error_if_name_is_empty(client, access_token):
    data = {
        "products": [
            {"name": "", "price": 500, "quantity": 1},
            {"name": "Test chair", "price": 299.99, "quantity": 3},
        ],
        "payment": {"type": "cashless", "amount": 200},
    }

    response = await client.post(
        "/receipts/", headers={"authorization": f"Bearer {access_token}"}, json=data
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_receipt_returns_an_error_if_price_is_negative_number(
    client, access_token
):
    data = {
        "products": [
            {"name": "Test table", "price": -1, "quantity": 1},
            {"name": "Test chair", "price": 299.99, "quantity": 3},
        ],
        "payment": {"type": "cashless", "amount": 200},
    }

    response = await client.post(
        "/receipts/", headers={"authorization": f"Bearer {access_token}"}, json=data
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_receipt_returns_an_error_if_quantity_is_negative_number(
    client, access_token
):
    data = {
        "products": [
            {"name": "Test table", "price": 500, "quantity": 1},
            {"name": "Test chair", "price": 299.99, "quantity": -2},
        ],
        "payment": {"type": "cashless", "amount": 200},
    }

    response = await client.post(
        "/receipts/", headers={"authorization": f"Bearer {access_token}"}, json=data
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_receipts_returns_receipts(
    client, access_token, receipts_list, user
):
    response = await client.get(
        "/receipts/me/", headers={"authorization": f"Bearer {access_token}"}
    )

    first_receipt, second_receipt = response.json()

    assert response.status_code == 200
    assert "id" in first_receipt
    assert first_receipt["user_id"] == user.id
    assert first_receipt["products"] == [
        {"name": "Test table", "price": 500, "quantity": 1, "total": 500},
        {"name": "Test chair", "price": 299.99, "quantity": 3, "total": 899.97},
    ]
    assert first_receipt["payment"] == {"type": "cashless", "amount": 2000}
    assert first_receipt["total"] == 1399.97
    assert first_receipt["rest"] == 600.03
    assert (
        datetime.strptime(first_receipt["created_at"], "%Y-%m-%dT%H:%M:%S.%f").date()
        == datetime.utcnow().date()
    )

    assert "id" in second_receipt
    assert second_receipt["user_id"] == user.id
    assert second_receipt["products"] == [
        {"name": "Test headphone", "price": 1000, "quantity": 2, "total": 2000},
        {"name": "Test microphone", "price": 400.99, "quantity": 3, "total": 1202.97},
    ]
    assert second_receipt["payment"] == {"type": "cash", "amount": 3500}
    assert second_receipt["total"] == 3202.97
    assert second_receipt["rest"] == 297.03
    assert (
        datetime.strptime(second_receipt["created_at"], "%Y-%m-%dT%H:%M:%S.%f").date()
        == datetime.utcnow().date()
    )


@pytest.mark.asyncio
async def test_list_receipts_returns_empty_list_if_user_does_not_have_any_receipt(
    client, access_token
):
    response = await client.get(
        "/receipts/me/", headers={"authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_receipt_returns_plain_text_generated_receipt(client, receipt, user):
    response = await client.get(f"/receipts/{receipt.id}/")

    assert response.status_code == 200
    assert response.text == generate_receipt(receipt, user)


@pytest.mark.asyncio
async def test_get_receipt_returns_error_if_receipt_not_found(client):
    response = await client.get("/receipts/0/")

    assert response.status_code == 404
    assert response.json() == {"detail": "Receipt not found"}
