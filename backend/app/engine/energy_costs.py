"""Fetch provincial fuel and electricity costs by year from DB."""
from sqlalchemy.orm import Session
from app.models.reference_data import ProvincialFuelCost
from app.engine.constants import (
    DEFAULT_ELECTRICITY_RATE,
    DEFAULT_GASOLINE_PRICE,
    DEFAULT_DIESEL_PRICE,
)


def _get_fuel_row(db: Session, province: str, year: int) -> ProvincialFuelCost | None:
    return (
        db.query(ProvincialFuelCost)
        .filter(ProvincialFuelCost.province == province, ProvincialFuelCost.year == year)
        .first()
    )


def electricity_rate(db: Session, province: str, year: int) -> float:
    row = _get_fuel_row(db, province, year)
    return row.electricity_rate_kwh if row else DEFAULT_ELECTRICITY_RATE


def fuel_price(db: Session, province: str, year: int, fuel_type: str) -> float:
    row = _get_fuel_row(db, province, year)
    if row is None:
        return DEFAULT_DIESEL_PRICE if fuel_type == "Diesel" else DEFAULT_GASOLINE_PRICE
    if fuel_type == "Diesel":
        return row.diesel_price_l
    return row.gasoline_price_l


def blended_electricity_rate(
    db: Session,
    province: str,
    year: int,
    depot_pct: float,
    public_rate: float,
) -> float:
    """Weighted average of depot (provincial) and public charging rates."""
    depot_rate = electricity_rate(db, province, year)
    return depot_pct * depot_rate + (1 - depot_pct) * public_rate
