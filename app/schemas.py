from decimal import Decimal

from pydantic import BaseModel


class OrderDTO(BaseModel):
    id: int
    amount: Decimal
