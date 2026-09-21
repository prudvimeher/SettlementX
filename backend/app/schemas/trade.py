from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class TradeCreate(BaseModel):
    trade_id: str = Field(min_length=1, max_length=50)
    buyer: str = Field(min_length=1, max_length=100)
    seller: str = Field(min_length=1, max_length=100)
    instrument: str = Field(min_length=1, max_length=100)
    quantity: Decimal = Field(gt=0)
    price: Decimal = Field(gt=0)
    currency: str = Field(min_length=1, max_length=10)
    trade_date: date
    settlement_date: date


class TradeResponse(BaseModel):
    trade_id: str
    status: str
    message: str