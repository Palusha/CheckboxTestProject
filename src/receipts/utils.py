import json

from databases.interfaces import Record

RECEIPT_WIDTH = 36


def generate_recipt_line(character: str):
    return character * RECEIPT_WIDTH


def format_num(num: int | float):
    return f"{num:,.2f}".replace(",", " ")


def generate_receipt(receipt: Record, user: Record):
    payment = json.loads(receipt.payment)
    products = json.loads(receipt.products)
    payment_type = "Картка" if payment["type"] == "Картка" else "Готівка"

    products_text = ""
    for i, product in enumerate(products):
        products_text += f"""{format_num(product['quantity'])} x {format_num(product['price'])}
{product['name']} {format_num(product['total']).rjust(RECEIPT_WIDTH - len(product['name']) - 1)}
{generate_recipt_line('-') if i != len(products) - 1 else ''}
"""
    receipt_text = f"""{f'ФОП  {user.first_name}'.center(RECEIPT_WIDTH)}
{generate_recipt_line('=')}
{products_text.strip()}
{generate_recipt_line('=')}
{'СУМА'} {format_num(receipt.total).rjust(RECEIPT_WIDTH - 5)}
{payment_type} {format_num(payment['amount']).rjust(RECEIPT_WIDTH - len(payment_type) - 1)}
{'Решта'} {format_num(receipt.rest).rjust(RECEIPT_WIDTH - 6)}
{generate_recipt_line('=')}
{receipt.created_at.strftime('%Y.%m.%d %H:%M').center(RECEIPT_WIDTH)}
{'Дякуємо за покупку!'.center(RECEIPT_WIDTH)}
"""
    return receipt_text
