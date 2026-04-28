"""Charger count and capex calculations."""
import math
from sqlalchemy.orm import Session
from app.models.reference_data import Charger
from app.schemas.inputs import FleetParams


def get_charger(db: Session, charger_type_id: int | None) -> Charger | None:
    if charger_type_id:
        return db.query(Charger).filter(Charger.id == charger_type_id).first()
    return db.query(Charger).order_by(Charger.unit_cost_cad.asc()).first()


def compute_charger_count(fleet: FleetParams) -> int:
    """Mirrors Excel: ROUNDUP((ev_fleet / vehicles_per_charger) * depot_pct, 0)"""
    if fleet.depot_charging_pct == 0:
        return 0
    return math.ceil(
        (fleet.ev_fleet_size / fleet.ev_vehicles_per_charger) * fleet.depot_charging_pct
    )


def compute_charger_capex(charger: Charger, charger_count: int) -> float:
    if charger is None or charger_count == 0:
        return 0.0
    return (charger.unit_cost_cad + charger.installation_cost_cad) * charger_count
