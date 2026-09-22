import uuid

from fastapi import APIRouter

from app.schemas.external import (
    ExternalTransferRequest,
    ExternalTransferResponse,
)

router = APIRouter(
    prefix="/api/v1/external",
    tags=["External Settlement Simulator"],
)


def simulate_transfer(
    request: ExternalTransferRequest,
    transfer_type: str,
):
    external_reference = f"EXT-{uuid.uuid4().hex[:10].upper()}"

    if request.scenario == "success":
        return ExternalTransferResponse(
            external_reference=external_reference,
            status="SUCCESS",
            message=f"{transfer_type} completed successfully",
        )

    if request.scenario == "failure":
        return ExternalTransferResponse(
            external_reference=external_reference,
            status="FAILURE",
            message=f"{transfer_type} failed",
        )

    if request.scenario == "timeout":
        return ExternalTransferResponse(
            external_reference=external_reference,
            status="TIMEOUT",
            message=f"{transfer_type} timed out",
        )

    if request.scenario == "duplicate":
        return ExternalTransferResponse(
            external_reference=external_reference,
            status="DUPLICATE",
            message=f"{transfer_type} was already processed",
        )


@router.post(
    "/cash-transfer",
    response_model=ExternalTransferResponse,
)
def cash_transfer(request: ExternalTransferRequest):
    return simulate_transfer(request, "Cash transfer")


@router.post(
    "/asset-transfer",
    response_model=ExternalTransferResponse,
)
def asset_transfer(request: ExternalTransferRequest):
    return simulate_transfer(request, "Asset transfer")