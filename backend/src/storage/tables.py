from datetime import datetime, date
from typing import Optional
import uuid

from sqlalchemy import (
    String,
    Text,
    Integer,
    Date,
    func,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    pass


class FundTable(Base):
    __tablename__ = "funds"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    manager: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    risk_profile: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    asisa_classification: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    benchmark: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    portfolio_launch_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    portfolio_size: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    fund_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    as_of_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    holdings: Mapped[list["HoldingTable"]] = relationship(back_populates="fund", cascade="all, delete-orphan")
    fees: Mapped[list["FeeTable"]] = relationship(back_populates="fund", cascade="all, delete-orphan")
    asset_allocations: Mapped[list["AssetAllocationTable"]] = relationship(back_populates="fund", cascade="all, delete-orphan")
    performance_records: Mapped[list["PerformanceRecordTable"]] = relationship(back_populates="fund", cascade="all, delete-orphan")
    annual_returns: Mapped[list["AnnualReturnsTable"]] = relationship(back_populates="fund", cascade="all, delete-orphan")
    chunks: Mapped[list["FundChunkTable"]] = relationship(back_populates="fund", cascade="all, delete-orphan")

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}"


class HoldingTable(Base):
    __tablename__ = "holdings"
    __table_args__ = (
        UniqueConstraint(
            "fund_id", "instrument_name", "as_of_date",
            name="uq_holding_fund_instrument_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fund_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    instrument_name: Mapped[str] = mapped_column(String, nullable=False)
    weight_pct: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    fund: Mapped["FundTable"] = relationship(back_populates="holdings")

    def __repr__(self):
        return f"Holding(fund_id={self.fund_id}, instrument={self.instrument_name}, weight={self.weight_pct}%)"


class FeeTable(Base):
    __tablename__ = "fees"
    __table_args__ = (
        UniqueConstraint(
            "fund_id", "as_of_date",
            name="uq_fee_fund_as_of_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fund_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    advice_initial_fee_max_pct: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    manager_initial_fee_pct: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    advice_annual_fee_max_pct: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    manager_annual_fee_pct: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    ter: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    transaction_cost_pct: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    total_investment_charge_pct: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="ZAR")
    effective_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    fund: Mapped["FundTable"] = relationship(back_populates="fees")

    def __repr__(self):
        return f"Fee(fund_id={self.fund_id}, ter={self.ter}, effective={self.effective_date})"


class AssetAllocationTable(Base):
    __tablename__ = "asset_allocations"
    __table_args__ = (
        UniqueConstraint(
            "fund_id", "asset_class", "as_of_date",
            name="uq_asset_allocation_fund_class_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fund_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    asset_class: Mapped[str] = mapped_column(String, nullable=False)
    weight_pct: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    fund: Mapped["FundTable"] = relationship(back_populates="asset_allocations")

    def __repr__(self):
        return f"AssetAllocation(fund_id={self.fund_id}, asset_class={self.asset_class}, weight={self.weight_pct}%)"


class PerformanceRecordTable(Base):
    __tablename__ = "performance_records"
    __table_args__ = (
        UniqueConstraint(
            "fund_id", "period", "as_of_date",
            name="uq_performance_fund_period_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fund_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period: Mapped[str] = mapped_column(String(20), nullable=False)
    fund_return_pct: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    benchmark_return_pct: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    tracking_difference_pct: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    as_of_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    fund: Mapped["FundTable"] = relationship(back_populates="performance_records")

    def __repr__(self):
        return f"PerformanceRecord(fund_id={self.fund_id}, period={self.period}, fund_return={self.fund_return_pct}%)"


class AnnualReturnsTable(Base):
    __tablename__ = "annual_returns"
    __table_args__ = (
        UniqueConstraint(
            "fund_id", "as_of_date",
            name="uq_annual_returns_fund_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fund_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    highest_pct: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    lowest_pct: Mapped[Optional[float]] = mapped_column(Numeric(7, 4), nullable=True)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    fund: Mapped["FundTable"] = relationship(back_populates="annual_returns")

    def __repr__(self):
        return f"AnnualReturns(fund_id={self.fund_id}, highest={self.highest_pct}%, lowest={self.lowest_pct}%)"


class FundChunkTable(Base):
    __tablename__ = "fund_chunks"
    __table_args__ = (
        UniqueConstraint(
            "fund_id", "content_hash",
            name="uq_fund_chunk_fund_content_hash",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fund_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    headings: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True)
    page_no: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    fund: Mapped["FundTable"] = relationship(back_populates="chunks")

    def __repr__(self):
        return f"FundChunk(fund_id={self.fund_id}, headings={self.headings}, page={self.page_no})"
