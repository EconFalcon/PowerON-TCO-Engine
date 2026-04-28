import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.scenario import Scenario
from app.schemas.inputs import TCOInputs
from app.schemas.outputs import TCOResult

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])


def _orm_to_inputs(s: Scenario) -> TCOInputs:
    from app.schemas.inputs import DutyCycle, FleetParams, VehicleSelection, LoanParams, LeaseParams
    return TCOInputs(
        duty_cycle=DutyCycle(
            daily_distance_km=s.daily_distance_km,
            max_payload_lbs=s.max_payload_lbs,
            vehicle_category=s.vehicle_category,
            refrigeration_required=s.refrigeration_required,
        ),
        fleet=FleetParams(
            province=s.province,
            ev_fleet_size=s.ev_fleet_size,
            ice_fleet_size=s.ice_fleet_size,
            annual_km_per_vehicle=s.annual_km_per_vehicle,
            depot_charging_pct=s.depot_charging_pct,
            public_charging_rate_per_kwh=s.public_charging_rate,
            ev_vehicles_per_charger=s.ev_vehicles_per_charger,
        ),
        vehicles=VehicleSelection(
            ev_model_id=s.ev_model_id,
            ice_model_id=s.ice_model_id,
            charger_type_id=s.charger_type_id,
        ),
        loan=LoanParams(
            interest_rate=s.loan_interest_rate or 0.065,
            down_payment_pct=s.loan_down_payment_pct or 0.20,
            loan_term_months=s.loan_term_months or 60,
        ),
        lease=LeaseParams(
            money_factor=s.lease_money_factor or 0.00125,
            lease_term_months=s.lease_term_months or 48,
            residual_value_pct=s.lease_residual_pct or 0.50,
        ),
        analysis_year=s.analysis_year or 2025,
        discount_rate=s.discount_rate or 0.08,
    )


class ScenarioIn(TCOInputs):
    name: str


@router.get("", response_model=List[dict])
def list_scenarios(db: Session = Depends(get_db)):
    rows = db.query(Scenario).order_by(Scenario.created_at.desc()).all()
    result = []
    for s in rows:
        ev_tco = None
        if s.result_json:
            try:
                r = json.loads(s.result_json)
                ev_tco = r["scenarios"][0]["ev_total_tco"] if r.get("scenarios") else None
            except Exception:
                pass
        result.append({
            "id": s.id,
            "name": s.name,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "province": s.province,
            "ev_fleet_size": s.ev_fleet_size,
            "ice_fleet_size": s.ice_fleet_size,
            "vehicle_category": s.vehicle_category,
            "ev_total_tco_cash": ev_tco,
        })
    return result


@router.get("/{scenario_id}", response_model=dict)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    s = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Scenario not found")
    inputs = _orm_to_inputs(s)
    result = json.loads(s.result_json) if s.result_json else None
    return {
        "id": s.id,
        "name": s.name,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "inputs": inputs.model_dump(),
        "result": result,
    }


class SaveScenarioRequest(TCOInputs):
    name: str


@router.post("", response_model=dict, status_code=201)
def save_scenario(body: SaveScenarioRequest, db: Session = Depends(get_db)):
    from app.engine.tco_calculator import calculate
    from app.engine.vehicle_selector import NoCandidateError

    inputs = TCOInputs(**body.model_dump(exclude={"name"}))
    try:
        result = calculate(inputs, db)
    except NoCandidateError as e:
        raise HTTPException(status_code=422, detail=str(e))

    s = Scenario(
        name=body.name,
        daily_distance_km=body.duty_cycle.daily_distance_km,
        max_payload_lbs=body.duty_cycle.max_payload_lbs,
        vehicle_category=body.duty_cycle.vehicle_category,
        refrigeration_required=body.duty_cycle.refrigeration_required,
        province=body.fleet.province,
        ev_fleet_size=body.fleet.ev_fleet_size,
        ice_fleet_size=body.fleet.ice_fleet_size,
        annual_km_per_vehicle=body.fleet.annual_km_per_vehicle,
        depot_charging_pct=body.fleet.depot_charging_pct,
        public_charging_rate=body.fleet.public_charging_rate_per_kwh,
        ev_vehicles_per_charger=body.fleet.ev_vehicles_per_charger,
        ev_model_id=result.recommended_ev.id,
        ice_model_id=result.recommended_ice.id,
        charger_type_id=body.vehicles.charger_type_id,
        loan_interest_rate=body.loan.interest_rate,
        loan_down_payment_pct=body.loan.down_payment_pct,
        loan_term_months=body.loan.loan_term_months,
        lease_money_factor=body.lease.money_factor,
        lease_term_months=body.lease.lease_term_months,
        lease_residual_pct=body.lease.residual_value_pct,
        analysis_year=body.analysis_year,
        discount_rate=body.discount_rate,
        result_json=result.model_dump_json(),
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "name": s.name, "created_at": s.created_at.isoformat() if s.created_at else None}


@router.delete("/{scenario_id}", status_code=204)
def delete_scenario(scenario_id: int, db: Session = Depends(get_db)):
    s = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(s)
    db.commit()
