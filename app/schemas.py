from decimal import Decimal

from pydantic import BaseModel


class OrderDTO(BaseModel):
    id: int
    amount: Decimal


class Extra(BaseModel):
    thread: int
    connection: int


class OrderWithExtra(OrderDTO):
    extra: Extra
