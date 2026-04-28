"""
Rebate and incentive lookups for EV vehicles and chargers.
"""
from sqlalchemy.orm import Session
from app.models.reference_data import EVProvincialRebate, ChargerIncentive, CarbonCredit, EVVehicle
from app.engine.constants import ICE_CO2_TONNE_PER_KM, EV_CO2_TONNE_PER_KM


def ev_provincial_rebate(db: Session, ev_vehicle_id: int, province: str) -> float:
    row = (
        db.query(EVProvincialRebate)
        .filter(
            EVProvincialRebate.ev_vehicle_id == ev_vehicle_id,
            EVProvincialRebate.province == province,
        )
        .first()
    )
    return row.rebate_amount_cad if row else 0.0


def charger_rebate(db: Session, province: str, charger_type: str, power_kw: float) -> float:
    row = (
        db.query(ChargerIncentive)
        .filter(
            ChargerIncentive.province == province,
            ChargerIncentive.charger_type == charger_type,
        )
        .first()
    )
    return row.rebate_amount_cad if row else 0.0


def carbon_credit_value(db: Session, province: str, year: int) -> float:
    """Return average annual CFR credit value in $/tonne for the given province/year."""
    row = (
        db.query(CarbonCredit)
        .filter(
            CarbonCredit.province == province,
            CarbonCredit.year == year,
            CarbonCredit.month.is_(None),
        )
        .first()
    )
    if row:
        return row.credit_value_per_tonne
    # Fall back to any month for that year
    rows = (
        db.query(CarbonCredit)
        .filter(CarbonCredit.province == province, CarbonCredit.year == year)
        .all()
    )
    if rows:
        return sum(r.credit_value_per_tonne for r in rows) / len(rows)
    return 0.0


def annual_carbon_credit_revenue(
    db: Session,
    province: str,
    year: int,
    annual_km: float,
    fleet_size: int,
    efficiency_kwh_per_km: float,
) -> float:
    """
    EV earns CFR carbon credits per kWh dispensed.
    Revenue = efficiency_kwh_per_km * annual_km * fleet_size * cfr_$/kWh
    """
    cfr_rate = carbon_credit_value(db, province, year)
    if cfr_rate == 0:
        return 0.0
    total_kwh = efficiency_kwh_per_km * annual_km * fleet_size
    return total_kwh * cfr_rate
