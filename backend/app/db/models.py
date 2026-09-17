import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# -------------------------
# ENUMS
# -------------------------

class TradeStatus(str, enum.Enum):
    CAPTURED = "CAPTURED"
    VALIDATED = "VALIDATED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


class SettlementStatus(str, enum.Enum):
    INSTRUCTED = "INSTRUCTED"
    PARTIALLY_SETTLED = "PARTIALLY_SETTLED"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    PENDING_RETRY = "PENDING_RETRY"
    EXCEPTION = "EXCEPTION"


class LegStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TIMEOUT = "TIMEOUT"


class LegType(str, enum.Enum):
    CASH = "CASH"
    ASSET = "ASSET"


class Direction(str, enum.Enum):
    BUYER_TO_SELLER = "BUYER_TO_SELLER"
    SELLER_TO_BUYER = "SELLER_TO_BUYER"


class TransactionType(str, enum.Enum):
    CASH_TRANSFER = "CASH_TRANSFER"
    ASSET_TRANSFER = "ASSET_TRANSFER"


class ExternalTransactionStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TIMEOUT = "TIMEOUT"
    DUPLICATE = "DUPLICATE"


class ExceptionStatus(str, enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    MANUAL_INTERVENTION_REQUIRED = "MANUAL_INTERVENTION_REQUIRED"


# -------------------------
# TRADE
# -------------------------

class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    trade_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    buyer: Mapped[str] = mapped_column(String(100), nullable=False)
    seller: Mapped[str] = mapped_column(String(100), nullable=False)
    instrument: Mapped[str] = mapped_column(String(100), nullable=False)

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 4),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(20, 4),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    trade_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    settlement_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[TradeStatus] = mapped_column(
        Enum(TradeStatus),
        nullable=False,
        default=TradeStatus.CAPTURED,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    settlement: Mapped["Settlement | None"] = relationship(
        back_populates="trade",
        uselist=False,
    )

    audit_events: Mapped[list["AuditEvent"]] = relationship(
        back_populates="trade",
    )

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_trade_quantity_positive"),
        CheckConstraint("price > 0", name="check_trade_price_positive"),
    )


# -------------------------
# SETTLEMENT
# -------------------------

class Settlement(Base):
    __tablename__ = "settlements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    settlement_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trades.id"),
        unique=True,
        nullable=False,
    )

    status: Mapped[SettlementStatus] = mapped_column(
        Enum(SettlementStatus),
        nullable=False,
        default=SettlementStatus.INSTRUCTED,
    )

    cash_status: Mapped[LegStatus] = mapped_column(
        Enum(LegStatus),
        nullable=False,
        default=LegStatus.PENDING,
    )

    asset_status: Mapped[LegStatus] = mapped_column(
        Enum(LegStatus),
        nullable=False,
        default=LegStatus.PENDING,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    trade: Mapped["Trade"] = relationship(
        back_populates="settlement",
    )

    legs: Mapped[list["SettlementLeg"]] = relationship(
        back_populates="settlement",
        cascade="all, delete-orphan",
    )

    exceptions: Mapped[list["ExceptionRecord"]] = relationship(
        back_populates="settlement",
        cascade="all, delete-orphan",
    )

    audit_events: Mapped[list["AuditEvent"]] = relationship(
        back_populates="settlement",
    )


# -------------------------
# SETTLEMENT LEG
# -------------------------

class SettlementLeg(Base):
    __tablename__ = "settlement_legs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    settlement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("settlements.id"),
        nullable=False,
    )

    leg_type: Mapped[LegType] = mapped_column(
        Enum(LegType),
        nullable=False,
    )

    direction: Mapped[Direction] = mapped_column(
        Enum(Direction),
        nullable=False,
    )

    amount: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 4),
        nullable=True,
    )

    quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 4),
        nullable=True,
    )

    currency: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    instrument: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[LegStatus] = mapped_column(
        Enum(LegStatus),
        nullable=False,
        default=LegStatus.PENDING,
    )

    external_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    settlement: Mapped["Settlement"] = relationship(
        back_populates="legs",
    )

    external_transactions: Mapped[list["ExternalTransaction"]] = relationship(
        back_populates="leg",
        cascade="all, delete-orphan",
    )


# -------------------------
# EXTERNAL TRANSACTION
# -------------------------

class ExternalTransaction(Base):
    __tablename__ = "external_transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    settlement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("settlements.id"),
        nullable=False,
    )

    leg_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("settlement_legs.id"),
        nullable=False,
    )

    external_reference: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType),
        nullable=False,
    )

    status: Mapped[ExternalTransactionStatus] = mapped_column(
        Enum(ExternalTransactionStatus),
        nullable=False,
    )

    cash_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 4),
        nullable=True,
    )

    asset_quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 4),
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    leg: Mapped["SettlementLeg"] = relationship(
        back_populates="external_transactions",
    )


# -------------------------
# EXCEPTION
# -------------------------

class ExceptionRecord(Base):
    __tablename__ = "exceptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    settlement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("settlements.id"),
        nullable=False,
    )

    exception_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[ExceptionStatus] = mapped_column(
        Enum(ExceptionStatus),
        nullable=False,
        default=ExceptionStatus.OPEN,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    settlement: Mapped["Settlement"] = relationship(
        back_populates="exceptions",
    )


# -------------------------
# AUDIT EVENT
# -------------------------

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    trade_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trades.id"),
        nullable=True,
    )

    settlement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("settlements.id"),
        nullable=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    details: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    trade: Mapped["Trade | None"] = relationship(
        back_populates="audit_events",
    )

    settlement: Mapped["Settlement | None"] = relationship(
        back_populates="audit_events",
    )