from pydantic import BaseModel
from typing import Literal


class ExternalTransferRequest(BaseModel):
    settlement_id: str
    amount: str | None = None
    quantity: str | None = None
    currency: str | None = None
    instrument: str | None = None
    scenario: Literal[
        "success",
        "failure",
        "timeout",
        "duplicate",
    ] = "success"


class ExternalTransferResponse(BaseModel):
    external_reference: str
    status: str
    message: str