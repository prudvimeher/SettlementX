from pydantic import BaseModel


class TradeConfirmationResponse(BaseModel):
    trade_id: str
    status: str
    message: str