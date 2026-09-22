from pydantic import BaseModel


class SettlementResponse(BaseModel):
    settlement_id: str
    trade_id: str
    status: str
    cash_status: str
    asset_status: str
    cash_amount: str
    currency: str
    asset_quantity: str
    instrument: str
    message: str