from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Trade, TradeStatus, AuditEvent
from app.schemas.trade import TradeCreate, TradeResponse
from app.schemas.trade_validation import TradeValidationResponse
from app.schemas.trade_confirmation import TradeConfirmationResponse
from decimal import Decimal

from app.db.models import (
    Trade,
    TradeStatus,
    AuditEvent,
    Settlement,
    SettlementLeg,
    SettlementStatus,
    LegStatus,
    LegType,
    Direction,
)
from app.schemas.settlement import SettlementResponse


router = APIRouter(prefix="/api/v1/trades", tags=["Trades"])


@router.post(
    "",
    response_model=TradeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_trade(
    trade_data: TradeCreate,
    db: Session = Depends(get_db),
):
    # Check duplicate trade_id
    existing_trade = (
        db.query(Trade)
        .filter(Trade.trade_id == trade_data.trade_id)
        .first()
    )

    if existing_trade:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "DUPLICATE_TRADE",
                "message": f"Trade {trade_data.trade_id} already exists",
            },
        )

    # Create trade
    trade = Trade(
        trade_id=trade_data.trade_id,
        buyer=trade_data.buyer,
        seller=trade_data.seller,
        instrument=trade_data.instrument,
        quantity=trade_data.quantity,
        price=trade_data.price,
        currency=trade_data.currency,
        trade_date=trade_data.trade_date,
        settlement_date=trade_data.settlement_date,
        status=TradeStatus.CAPTURED,
    )

    db.add(trade)
    db.flush()

    # Create audit event
    audit_event = AuditEvent(
        trade_id=trade.id,
        event_type="TRADE_CREATED",
        details={},
    )

    db.add(audit_event)

    # Save everything
    db.commit()

    return TradeResponse(
        trade_id=trade.trade_id,
        status=trade.status.value,
        message="Trade captured successfully",
    )
    
@router.post(
    "/{trade_id}/validate",
    response_model=TradeValidationResponse,
)
def validate_trade(trade_id: str, db: Session = Depends(get_db)):
    trade = (
        db.query(Trade)
        .filter(Trade.trade_id == trade_id)
        .first()
    )

    if not trade:
        raise HTTPException(
            status_code=404,
            detail="Trade not found",
        )

    errors = []

    if not trade.buyer or not trade.buyer.strip():
        errors.append("Buyer is required")

    if not trade.seller or not trade.seller.strip():
        errors.append("Seller is required")

    if not trade.currency or not trade.currency.strip():
        errors.append("Currency is required")

    if trade.quantity <= 0:
        errors.append("Quantity must be greater than zero")

    if trade.price <= 0:
        errors.append("Price must be greater than zero")

    if errors:
        trade.status = TradeStatus.REJECTED

        db.add(
            AuditEvent(
                trade_id=trade.id,
                event_type="TRADE_VALIDATION_FAILED",
                details={
                    "errors": errors,
                },
            )
        )

        db.commit()

        return TradeValidationResponse(
            trade_id=trade.trade_id,
            status=trade.status.value,
            message="; ".join(errors),
        )

    trade.status = TradeStatus.VALIDATED

    db.add(
        AuditEvent(
            trade_id=trade.id,
            event_type="TRADE_VALIDATED",
            details={},
        )
    )

    db.commit()

    return TradeValidationResponse(
        trade_id=trade.trade_id,
        status=trade.status.value,
        message="Trade validated successfully",
    )
    
@router.get("")
def get_trades(db: Session = Depends(get_db)):
    trades = db.query(Trade).order_by(Trade.created_at.desc()).all()

    return [
        {
            "trade_id": trade.trade_id,
            "buyer": trade.buyer,
            "seller": trade.seller,
            "instrument": trade.instrument,
            "quantity": trade.quantity,
            "price": trade.price,
            "currency": trade.currency,
            "trade_date": trade.trade_date,
            "settlement_date": trade.settlement_date,
            "status": trade.status.value,
        }
        for trade in trades
    ]
    
@router.post(
    "/{trade_id}/confirm",
    response_model=TradeConfirmationResponse,
)
def confirm_trade(trade_id: str, db: Session = Depends(get_db)):
    trade = (
        db.query(Trade)
        .filter(Trade.trade_id == trade_id)
        .first()
    )

    if not trade:
        raise HTTPException(
            status_code=404,
            detail="Trade not found",
        )

    if trade.status != TradeStatus.VALIDATED:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "INVALID_TRADE_STATUS",
                "message": (
                    f"Trade must be VALIDATED before confirmation. "
                    f"Current status: {trade.status.value}"
                ),
            },
        )

    trade.status = TradeStatus.CONFIRMED

    db.add(
        AuditEvent(
            trade_id=trade.id,
            event_type="TRADE_CONFIRMED",
            details={},
        )
    )

    db.commit()

    return TradeConfirmationResponse(
        trade_id=trade.trade_id,
        status=trade.status.value,
        message="Trade confirmed successfully",
    )

@router.post(
    "/{trade_id}/settlement",
    response_model=SettlementResponse,
)
def create_settlement(
    trade_id: str,
    db: Session = Depends(get_db),
):
    trade = (
        db.query(Trade)
        .filter(Trade.trade_id == trade_id)
        .first()
    )

    if not trade:
        raise HTTPException(
            status_code=404,
            detail="Trade not found",
        )

    if trade.status != TradeStatus.CONFIRMED:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "INVALID_TRADE_STATUS",
                "message": (
                    "Settlement can only be created for CONFIRMED trades. "
                    f"Current status: {trade.status.value}"
                ),
            },
        )

    existing_settlement = (
        db.query(Settlement)
        .filter(Settlement.trade_id == trade.id)
        .first()
    )

    if existing_settlement:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "SETTLEMENT_ALREADY_EXISTS",
                "message": (
                    f"Settlement already exists for trade {trade.trade_id}"
                ),
            },
        )

    settlement_number = (
        db.query(Settlement).count() + 1
    )

    settlement = Settlement(
        settlement_id=f"S{settlement_number:04d}",
        trade_id=trade.id,
        status=SettlementStatus.INSTRUCTED,
        cash_status=LegStatus.PENDING,
        asset_status=LegStatus.PENDING,
        retry_count=0,
    )

    db.add(settlement)
    db.flush()

    settlement_value = trade.quantity * trade.price

    cash_leg = SettlementLeg(
        settlement_id=settlement.id,
        leg_type=LegType.CASH,
        direction=Direction.BUYER_TO_SELLER,
        amount=settlement_value,
        quantity=None,
        currency=trade.currency,
        instrument=None,
        status=LegStatus.PENDING,
    )

    asset_leg = SettlementLeg(
        settlement_id=settlement.id,
        leg_type=LegType.ASSET,
        direction=Direction.SELLER_TO_BUYER,
        amount=None,
        quantity=trade.quantity,
        currency=None,
        instrument=trade.instrument,
        status=LegStatus.PENDING,
    )

    db.add(cash_leg)
    db.add(asset_leg)

    db.add(
        AuditEvent(
            trade_id=trade.id,
            settlement_id=settlement.id,
            event_type="SETTLEMENT_CREATED",
            details={
                "settlement_id": settlement.settlement_id,
                "cash_amount": str(settlement_value),
                "currency": trade.currency,
                "asset_quantity": str(trade.quantity),
                "instrument": trade.instrument,
            },
        )
    )

    db.commit()

    return SettlementResponse(
        settlement_id=settlement.settlement_id,
        trade_id=trade.trade_id,
        status=settlement.status.value,
        cash_status=settlement.cash_status.value,
        asset_status=settlement.asset_status.value,
        cash_amount=str(settlement_value),
        currency=trade.currency,
        asset_quantity=str(trade.quantity),
        instrument=trade.instrument,
        message="Settlement created successfully",
    )    