from pydantic import BaseModel


class TradeValidationResponse(BaseModel):
    trade_id: str
    status: str
    message: str