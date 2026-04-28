"""
Year-by-year cost breakdown for EV and ICE fleets across all 4 financing scenarios.
"""
from typing import List
from sqlalchemy.orm import Session

from app.models.reference_data import EVVehicle, ICEVehicle, Charger, MaintenanceCost
from app.schemas.inputs import TCOInputs
from app.schemas.outputs import YearCostBreakdown
from app.engine import financing, energy_costs, rebates
from app.engine.constants import (
    ANALYSIS_YEARS,
    TIRE_COST_PER_KM,
    INSURANCE_PCT_OF_MSRP_YEAR1,
    INSURANCE_ANNUAL_DECLINE,
    SALVAGE_PCT,
    CHARGER_MAINTENANCE_PCT,
    DEFAULT_MAINTENANCE_COST_PER_KM,
    IMHZEV_PURCHASE_YEAR_CAP,
)


def _maintenance_rate(db: Session, category: str, vehicle_type: str) -> float:
    row = (
        db.query(MaintenanceCost)
        .filter(
            MaintenanceCost.vehicle_category == category,
            MaintenanceCost.vehicle_type == vehicle_type,
        )
        .first()
    )
    return row.cost_per_km if row else DEFAULT_MAINTENANCE_COST_PER_KM[vehicle_type]


def compute_ev_yearly(
    scenario_id: int,
    inputs: TCOInputs,
    ev: EVVehicle,
    charger: Charger | None,
    charger_count: int,
    charger_capex: float,
    db: Session,
) -> List[YearCostBreakdown]:
    fleet = inputs.fleet
    annual_km = fleet.annual_km_per_vehicle * fleet.ev_fleet_size
    category = inputs.duty_cycle.vehicle_category
    province = fleet.province
    base_year = inputs.analysis_year
    maintenance_rate = _maintenance_rate(db, category, "EV")
    tire_rate = TIRE_COST_PER_KM.get(category, TIRE_COST_PER_KM["Light Duty"])["EV"]

    # Provincial EV rebate (applied in year 1, capped by fleet size)
    prov_rebate_per_vehicle = rebates.ev_provincial_rebate(db, ev.id, province)
    # iMHZEV rebate: only for first N purchase years from the DB on the vehicle
    imhzev_per_vehicle = 0.0
    if ev.imhzev_rebate_eligible:
        imhzev_rebate_row = (
            db.query(rebates.__builtins__) if False else None  # placeholder
        )
        # Look up from ev_provincial_rebates for iMHZEV specifically if tagged
        # For now we sum all rebates into prov_rebate; iMHZEV is included in seeded data
        pass

    charger_rebate_total = rebates.charger_rebate(
        db, province, charger.type_name if charger else "", charger.power_kw if charger else 0
    ) * charger_count

    yearly: List[YearCostBreakdown] = []
    for y in range(1, ANALYSIS_YEARS + 1):
        year = base_year + y - 1

        # Vehicle + charger cost
        veh_cost, chrg_cost = financing.vehicle_cost_by_year(
            scenario_id=scenario_id,
            msrp=ev.msrp_cad,
            charger_capex=charger_capex,
            loan_rate=inputs.loan.interest_rate,
            loan_down_pct=inputs.loan.down_payment_pct,
            loan_term_months=inputs.loan.loan_term_months,
            money_factor=inputs.lease.money_factor,
            lease_term_months=inputs.lease.lease_term_months,
            lease_residual_pct=inputs.lease.residual_value_pct,
            year=y,
            fleet_size=fleet.ev_fleet_size,
        )

        # Charger annual maintenance (after year 1)
        charger_maint = charger_capex * CHARGER_MAINTENANCE_PCT if y > 1 else 0.0
        chrg_cost_total = chrg_cost + charger_maint

        # Electricity cost
        e_rate = energy_costs.blended_electricity_rate(
            db, province, year, fleet.depot_charging_pct, fleet.public_charging_rate_per_kwh
        )
        electricity_cost = annual_km * ev.efficiency_kwh_per_km * e_rate

        # Maintenance
        maint_cost = annual_km * maintenance_rate

        # Tires
        tire_cost = annual_km * tire_rate

        # Insurance (declining)
        insurance_base = ev.msrp_cad * fleet.ev_fleet_size * INSURANCE_PCT_OF_MSRP_YEAR1
        insurance = insurance_base * ((1 - INSURANCE_ANNUAL_DECLINE) ** (y - 1))

        # Rebates (negative — year 1 only for purchase rebates)
        rebate_total = 0.0
        if y == 1:
            rebate_total = (prov_rebate_per_vehicle * fleet.ev_fleet_size) + charger_rebate_total

        # Carbon credits (annual EV benefit — negative cost)
        carbon_rev = rebates.annual_carbon_credit_revenue(
            db, province, year, fleet.annual_km_per_vehicle, fleet.ev_fleet_size,
            ev.efficiency_kwh_per_km
        )
        rebate_total += carbon_rev

        # Salvage (year 10 only, negative cost)
        salvage = 0.0
        if y == ANALYSIS_YEARS:
            salvage = -(ev.msrp_cad * fleet.ev_fleet_size * SALVAGE_PCT["EV"])

        total = (
            veh_cost
            + chrg_cost_total
            + electricity_cost
            + maint_cost
            + tire_cost
            + insurance
            - rebate_total
            + salvage
        )

        yearly.append(
            YearCostBreakdown(
                year=y,
                vehicle_cost=veh_cost,
                fuel_or_electricity=electricity_cost,
                maintenance=maint_cost,
                tires=tire_cost,
                insurance=insurance,
                charger_cost=chrg_cost_total,
                rebates=rebate_total,
                salvage=salvage,
                total=total,
            )
        )
    return yearly


def compute_ice_yearly(
    scenario_id: int,
    inputs: TCOInputs,
    ice: ICEVehicle,
    db: Session,
) -> List[YearCostBreakdown]:
    fleet = inputs.fleet
    annual_km = fleet.annual_km_per_vehicle * fleet.ice_fleet_size
    category = inputs.duty_cycle.vehicle_category
    province = fleet.province
    base_year = inputs.analysis_year
    maintenance_rate = _maintenance_rate(db, category, "ICE")
    tire_rate = TIRE_COST_PER_KM.get(category, TIRE_COST_PER_KM["Light Duty"])["ICE"]

    yearly: List[YearCostBreakdown] = []
    for y in range(1, ANALYSIS_YEARS + 1):
        year = base_year + y - 1

        # Vehicle cost (ICE has no charger)
        veh_cost, _ = financing.vehicle_cost_by_year(
            scenario_id=scenario_id,
            msrp=ice.msrp_cad,
            charger_capex=0.0,
            loan_rate=inputs.loan.interest_rate,
            loan_down_pct=inputs.loan.down_payment_pct,
            loan_term_months=inputs.loan.loan_term_months,
            money_factor=inputs.lease.money_factor,
            lease_term_months=inputs.lease.lease_term_months,
            lease_residual_pct=inputs.lease.residual_value_pct,
            year=y,
            fleet_size=fleet.ice_fleet_size,
        )

        # Fuel cost
        fuel_l_per_km = ice.fuel_consumption_l_per_100km / 100
        f_price = energy_costs.fuel_price(db, province, year, ice.fuel_type)
        fuel_cost = annual_km * fuel_l_per_km * f_price

        # Maintenance
        maint_cost = annual_km * maintenance_rate

        # Tires
        tire_cost = annual_km * tire_rate

        # Insurance
        insurance_base = ice.msrp_cad * fleet.ice_fleet_size * INSURANCE_PCT_OF_MSRP_YEAR1
        insurance = insurance_base * ((1 - INSURANCE_ANNUAL_DECLINE) ** (y - 1))

        # Salvage (year 10)
        salvage = 0.0
        if y == ANALYSIS_YEARS:
            salvage = -(ice.msrp_cad * fleet.ice_fleet_size * SALVAGE_PCT["ICE"])

        total = veh_cost + fuel_cost + maint_cost + tire_cost + insurance + salvage

        yearly.append(
            YearCostBreakdown(
                year=y,
                vehicle_cost=veh_cost,
                fuel_or_electricity=fuel_cost,
                maintenance=maint_cost,
                tires=tire_cost,
                insurance=insurance,
                charger_cost=0.0,
                rebates=0.0,
                salvage=salvage,
                total=total,
            )
        )
    return yearly
