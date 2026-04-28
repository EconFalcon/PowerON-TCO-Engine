"""Orchestrator: produces TCOResult from TCOInputs + DB."""
from datetime import datetime
from sqlalchemy.orm import Session

from app.schemas.inputs import TCOInputs
from app.schemas.outputs import TCOResult, ScenarioTCO, VehicleSummary
from app.engine import annual_costs, present_value
from app.engine.vehicle_selector import select_ev, select_ice
from app.engine.charger_calculator import get_charger, compute_charger_count, compute_charger_capex


SCENARIO_NAMES = {
    1: "Cash",
    2: "Vehicle Financed",
    3: "Vehicle Financed + CAAS",
    4: "Lease",
}


def calculate(inputs: TCOInputs, db: Session) -> TCOResult:
    # Resolve vehicles
    ev = select_ev(inputs.duty_cycle, db, inputs.vehicles.ev_model_id)
    ice = select_ice(inputs.duty_cycle, db, inputs.vehicles.ice_model_id)
    charger = get_charger(db, inputs.vehicles.charger_type_id)

    charger_count = compute_charger_count(inputs.fleet)
    charger_capex = compute_charger_capex(charger, charger_count)

    total_annual_km = inputs.fleet.annual_km_per_vehicle * inputs.fleet.ev_fleet_size

    scenarios = []
    for scenario_id in [1, 2, 3, 4]:
        ev_yearly = annual_costs.compute_ev_yearly(
            scenario_id=scenario_id,
            inputs=inputs,
            ev=ev,
            charger=charger,
            charger_count=charger_count,
            charger_capex=charger_capex,
            db=db,
        )
        ice_yearly = annual_costs.compute_ice_yearly(
            scenario_id=scenario_id,
            inputs=inputs,
            ice=ice,
            db=db,
        )

        ev_totals = [y.total for y in ev_yearly]
        ice_totals = [y.total for y in ice_yearly]

        ev_total = sum(ev_totals)
        ice_total = sum(ice_totals)
        ev_npv = present_value.npv(ev_totals, inputs.discount_rate)
        ice_npv = present_value.npv(ice_totals, inputs.discount_rate)

        total_km_10yr = total_annual_km * 10
        ev_cost_per_km = ev_total / total_km_10yr if total_km_10yr > 0 else 0
        ice_fleet_km = inputs.fleet.annual_km_per_vehicle * inputs.fleet.ice_fleet_size * 10
        ice_cost_per_km = ice_total / ice_fleet_km if ice_fleet_km > 0 else 0

        be_year = present_value.break_even_year(ev_totals, ice_totals)

        scenarios.append(
            ScenarioTCO(
                scenario_name=SCENARIO_NAMES[scenario_id],
                scenario_id=scenario_id,
                ev_total_tco=ev_total,
                ice_total_tco=ice_total,
                ev_npv=ev_npv,
                ice_npv=ice_npv,
                ev_cost_per_km=ev_cost_per_km,
                ice_cost_per_km=ice_cost_per_km,
                savings_vs_ice=ice_total - ev_total,
                break_even_year=be_year,
                ev_yearly=ev_yearly,
                ice_yearly=ice_yearly,
            )
        )

    return TCOResult(
        scenarios=scenarios,
        recommended_ev=VehicleSummary(
            id=ev.id,
            display_name=ev.display_name,
            msrp_cad=ev.msrp_cad,
            category=ev.category,
        ),
        recommended_ice=VehicleSummary(
            id=ice.id,
            display_name=ice.display_name,
            msrp_cad=ice.msrp_cad,
            category=ice.category,
        ),
        charger_count=charger_count,
        charger_total_cost=charger_capex,
        calculation_timestamp=datetime.utcnow(),
    )
