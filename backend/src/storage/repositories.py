from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select

from src.models.asset_allocation import AssetAllocation
from src.models.funds import Fund
from src.models.holdings import Holding
from sqlalchemy import delete
from src.storage.tables import (
    AnnualReturnsTable,
    AssetAllocationTable,
    FeeTable,
    FundChunkTable,
    FundTable,
    HoldingTable,
    PerformanceRecordTable,
)


class BaseRepository:
    def __init__(self, session):
        self.session = session


class FundRepository:

    def __init__(self, session):
        self.session = session

    def list_funds(self):
        rows = self.session.query(FundTable).order_by(FundTable.name).all()
        return [
            Fund(
                id=str(r.id),
                name=r.name,
                manager=r.manager,
                risk_profile=r.risk_profile,
                asisa_classification=r.asisa_classification,
                benchmark=r.benchmark,
                portfolio_launch_date=r.portfolio_launch_date,
                portfolio_size=r.portfolio_size,
                as_of_date=r.as_of_date,
            )
            for r in rows
        ]

    def create(
        self,
        *,
        name: str,
        manager: str | None,
        risk_profile: str | None,
        asisa_classification: str | None = None,
        benchmark: str | None = None,
        portfolio_launch_date: date | None = None,
        portfolio_size: str | None = None,
        as_of_date: date | None = None,
        fund_hash: str | None = None,
    ) -> FundTable:
        fund = FundTable(
            name=name,
            manager=manager,
            risk_profile=risk_profile,
            asisa_classification=asisa_classification,
            benchmark=benchmark,
            portfolio_launch_date=portfolio_launch_date,
            portfolio_size=portfolio_size,
            as_of_date=as_of_date,
            fund_hash=fund_hash,
        )
        self.session.add(fund)
        return fund

    def get_by_fund_name(self, name) -> Optional[FundTable]:
        stmt = select(FundTable).where(FundTable.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_id(self, fund_id: UUID) -> Optional[FundTable]:
        stmt = select(FundTable).where(FundTable.id == fund_id)
        return self.session.execute(stmt).scalar_one_or_none()


class FeeRepository:

    def __init__(self, session):
        self.session = session

    def create(
        self,
        *,
        fund_id: UUID,
        advice_initial_fee_max_pct: Decimal | None = None,
        manager_initial_fee_pct: Decimal | None = None,
        advice_annual_fee_max_pct: Decimal | None = None,
        manager_annual_fee_pct: Decimal | None = None,
        ter: Decimal | None,
        transaction_cost_pct: Decimal | None = None,
        total_investment_charge_pct: Decimal | None = None,
        currency: str,
        effective_date: date,
        as_of_date: date,
    ) -> FeeTable:
        row = FeeTable(
            fund_id=fund_id,
            advice_initial_fee_max_pct=advice_initial_fee_max_pct,
            manager_initial_fee_pct=manager_initial_fee_pct,
            advice_annual_fee_max_pct=advice_annual_fee_max_pct,
            manager_annual_fee_pct=manager_annual_fee_pct,
            ter=ter,
            transaction_cost_pct=transaction_cost_pct,
            total_investment_charge_pct=total_investment_charge_pct,
            currency=currency,
            effective_date=effective_date,
            as_of_date=as_of_date,
        )
        self.session.add(row)
        return row

    def get_latest_by_fund(self, fund_id: UUID) -> Optional[FeeTable]:
        stmt = (
            select(FeeTable)
            .where(FeeTable.fund_id == fund_id)
            .order_by(FeeTable.as_of_date.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_fund(self, fund_id: UUID) -> list[FeeTable]:
        stmt = (
            select(FeeTable)
            .where(FeeTable.fund_id == fund_id)
            .order_by(FeeTable.as_of_date.desc())
        )
        return list(self.session.execute(stmt).scalars().all())


class HoldingsRepository:

    def __init__(self, session):
        self.session = session

    def create(self, *, fund_id: UUID, holding: Holding) -> HoldingTable:
        row = HoldingTable(
            fund_id=fund_id,
            instrument_name=holding.instrument_name,
            weight_pct=holding.weight,
            as_of_date=holding.as_of_date,
        )
        self.session.add(row)
        return row

    def bulk_create(self, *, fund_id: UUID, holdings: list[Holding]) -> list[HoldingTable]:
        rows = [
            HoldingTable(
                fund_id=fund_id,
                instrument_name=h.instrument_name,
                weight_pct=h.weight,
                as_of_date=h.as_of_date,
            )
            for h in holdings
        ]
        self.session.add_all(rows)
        return rows

    def list_by_fund_and_date(self, fund_id: UUID, as_of_date: date) -> list[HoldingTable]:
        stmt = (
            select(HoldingTable)
            .where(
                HoldingTable.fund_id == fund_id,
                HoldingTable.as_of_date == as_of_date,
            )
            .order_by(HoldingTable.weight_pct.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_latest_date_by_fund(self, fund_id: UUID) -> Optional[date]:
        stmt = (
            select(HoldingTable.as_of_date)
            .where(HoldingTable.fund_id == fund_id)
            .order_by(HoldingTable.as_of_date.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()


class AssetAllocationRepository:

    def __init__(self, session):
        self.session = session

    def create(self, *, fund_id: UUID, allocation: AssetAllocation) -> AssetAllocationTable:
        row = AssetAllocationTable(
            fund_id=fund_id,
            asset_class=allocation.asset_class,
            weight_pct=allocation.weight,
            as_of_date=allocation.as_of_date,
        )
        self.session.add(row)
        return row

    def bulk_create(self, *, fund_id: UUID, allocations: list[AssetAllocation]) -> list[AssetAllocationTable]:
        rows = [
            AssetAllocationTable(
                fund_id=fund_id,
                asset_class=a.asset_class,
                weight_pct=a.weight,
                as_of_date=a.as_of_date,
            )
            for a in allocations
        ]
        self.session.add_all(rows)
        return rows

    def list_by_fund_and_date(self, fund_id: UUID, as_of_date: date) -> list[AssetAllocationTable]:
        stmt = (
            select(AssetAllocationTable)
            .where(
                AssetAllocationTable.fund_id == fund_id,
                AssetAllocationTable.as_of_date == as_of_date,
            )
            .order_by(AssetAllocationTable.weight_pct.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_latest_date_by_fund(self, fund_id: UUID) -> Optional[date]:
        stmt = (
            select(AssetAllocationTable.as_of_date)
            .where(AssetAllocationTable.fund_id == fund_id)
            .order_by(AssetAllocationTable.as_of_date.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()


class PerformanceRepository:

    def __init__(self, session):
        self.session = session

    def bulk_create(self, *, fund_id: UUID, records: list[dict]) -> list[PerformanceRecordTable]:
        rows = [
            PerformanceRecordTable(
                fund_id=fund_id,
                period=r["period"],
                fund_return_pct=r.get("fund_return_pct"),
                benchmark_return_pct=r.get("benchmark_return_pct"),
                tracking_difference_pct=r.get("tracking_difference_pct"),
                as_of_date=r.get("as_of_date"),
            )
            for r in records
        ]
        self.session.add_all(rows)
        return rows

    def list_by_fund(self, fund_id: UUID) -> list[PerformanceRecordTable]:
        stmt = (
            select(PerformanceRecordTable)
            .where(PerformanceRecordTable.fund_id == fund_id)
            .order_by(PerformanceRecordTable.as_of_date.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_latest_date_by_fund(self, fund_id: UUID) -> Optional[date]:
        stmt = (
            select(PerformanceRecordTable.as_of_date)
            .where(PerformanceRecordTable.fund_id == fund_id)
            .order_by(PerformanceRecordTable.as_of_date.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_fund_and_date(self, fund_id: UUID, as_of_date: date) -> list[PerformanceRecordTable]:
        stmt = (
            select(PerformanceRecordTable)
            .where(
                PerformanceRecordTable.fund_id == fund_id,
                PerformanceRecordTable.as_of_date == as_of_date,
            )
        )
        return list(self.session.execute(stmt).scalars().all())


class AnnualReturnsRepository:

    def __init__(self, session):
        self.session = session

    def create(
        self,
        *,
        fund_id: UUID,
        highest_pct: Decimal | None,
        lowest_pct: Decimal | None,
        as_of_date: date,
    ) -> AnnualReturnsTable:
        row = AnnualReturnsTable(
            fund_id=fund_id,
            highest_pct=highest_pct,
            lowest_pct=lowest_pct,
            as_of_date=as_of_date,
        )
        self.session.add(row)
        return row

    def get_latest_by_fund(self, fund_id: UUID) -> Optional[AnnualReturnsTable]:
        stmt = (
            select(AnnualReturnsTable)
            .where(AnnualReturnsTable.fund_id == fund_id)
            .order_by(AnnualReturnsTable.as_of_date.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()


class FundChunkRepository:

    def __init__(self, session):
        self.session = session

    def bulk_create(self, *, fund_id: UUID, rows: list[dict]) -> list[FundChunkTable]:
        chunks = [
            FundChunkTable(
                fund_id=fund_id,
                text=r["text"],
                headings=r.get("headings"),
                page_no=r.get("page_no"),
                content_hash=r["content_hash"],
                embedding=r.get("embedding"),
            )
            for r in rows
        ]
        self.session.add_all(chunks)
        return chunks

    def delete_by_fund(self, fund_id: UUID) -> None:
        self.session.execute(
            delete(FundChunkTable).where(FundChunkTable.fund_id == fund_id)
        )

    def find_similar(
        self,
        embedding: list[float],
        limit: int = 10,
        fund_id: Optional[UUID] = None,
    ) -> list[FundChunkTable]:
        stmt = (
            select(FundChunkTable)
            .order_by(FundChunkTable.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        if fund_id is not None:
            stmt = stmt.where(FundChunkTable.fund_id == fund_id)
        return list(self.session.execute(stmt).scalars().all())

