"""
no_db_wrapper.py — In-memory TCO calculation bypassing all SQLAlchemy/database calls.

This module provides ``calculate_no_db()``, a thin wrapper around the core
financing and present-value functions that accepts explicit parameter values
instead of resolving them from the SQLite database.  It is the sole entry-point
used by the BEV Fleet Replacement Plan Tool's TCO_Adapter.

All DB-backed lookups (energy prices, maintenance rates, rebates, vehicle
records, charger records) are replaced by explicit fields on ``TCOInputsNoDB``.
The pure-math helpers in ``financing.py`` and ``present_value.py`` are called
directly, so the calculation logic is identical to the original engine.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.engine import financing, present_value
from app.engine.constants import (
    ANALYSIS_YEARS,
    TIRE_COST_PER_KM,
    INSURANCE_PCT_OF_MSRP_YEAR1,
    INSURANCE_ANNUAL_DECLINE,
    SALVAGE_PCT,
    CHARGER_MAINTENANCE_PCT,
)
from app.schemas.outputs import YearCostBreakdown, ScenarioTCO, TCOResult


# ---------------------------------------------------------------------------
# Input schema
# ---------------------------------------------------------------------------

class VehicleParamsNoDB(BaseModel):
    """Explicit vehicle parameters — replaces DB vehicle record lookups."""

    msrp_cad: float = Field(gt=0, description="Vehicle MSRP in CAD")
    # EV-specific
    efficiency_kwh_per_km: Optional[float] = Field(
        default=None, ge=0, description="BEV energy consumption in kWh/km"
    )
    # ICE-specific
    fuel_consumption_l_per_100km: Optional[float] = Field(
        default=None, ge=0, description="ICE fuel consumption in L/100 km"
    )
    fuel_type: str = Field(
        default="Gasoline", description="'Gasoline' | 'Diesel' | 'Propane'"
    )
    vehicle_category: str = Field(
        default="Light Duty",
        description="'Light Duty' | 'Medium Duty' | 'Heavy Duty'",
    )


class ChargerParamsNoDB(BaseModel):
    """Explicit charger parameters — replaces DB charger record lookups."""

    unit_cost_cad: float = Field(ge=0, description="Charger equipment cost per unit in CAD")
    installation_cost_cad: float = Field(
        ge=0, description="Charger installation cost per unit in CAD"
    )
    vehicles_per_charger: float = Field(
        gt=0, description="Number of vehicles sharing each charger"
    )


class TCOInputsNoDB(BaseModel):
    """
    Complete in-memory input schema for ``calculate_no_db()``.

    All values that the original engine resolves from the SQLite database must
    be supplied explicitly here.  The TCO_Adapter in the fleet replacement tool
    is responsible for mapping ``VehicleRecord``, ``SiteRecord``, and
    ``ParameterStore`` fields onto this schema.
    """

    # --- Vehicle parameters -------------------------------------------------
    ev: VehicleParamsNoDB
    ice: VehicleParamsNoDB

    # --- Charger parameters -------------------------------------------------
    charger: ChargerParamsNoDB

    # --- Fleet parameters ---------------------------------------------------
    fleet_size: int = Field(gt=0, description="Number of vehicles in this replacement cycle")
    annual_km_per_vehicle: float = Field(gt=0, description="Average annual km per vehicle")

    # --- Energy prices (explicit, no DB lookup) ----------------------------
    electricity_rate_per_kwh: float = Field(
        ge=0, description="Blended electricity rate in $/kWh"
    )
    fuel_price_per_litre: float = Field(ge=0, description="Fuel price in $/L")

    # --- Maintenance rates (explicit, no DB lookup) ------------------------
    ev_maintenance_cost_per_km: float = Field(ge=0, description="EV maintenance cost in $/km")
    ice_maintenance_cost_per_km: float = Field(ge=0, description="ICE maintenance cost in $/km")

    # --- Rebates and incentives (explicit, no DB lookup) -------------------
    ev_rebate_total_cad: float = Field(
        default=0.0, ge=0, description="Total EV purchase rebate in CAD (applied year 1)"
    )
    charger_rebate_total_cad: float = Field(
        default=0.0, ge=0, description="Total charger rebate in CAD (applied year 1)"
    )
    annual_cfr_revenue_per_kwh: float = Field(
        default=0.0,
        ge=0,
        description="CFR (Clean Fuel Regulation) revenue in $/kWh dispensed, per year",
    )

    # --- Financing parameters -----------------------------------------------
    discount_rate: float = Field(default=0.08, ge=0, le=1)
    loan_interest_rate: float = Field(default=0.065, ge=0, le=1)
    loan_down_payment_pct: float = Field(default=0.20, ge=0, le=1)
    loan_term_months: int = Field(default=60, gt=0)
    lease_money_factor: float = Field(default=0.00125, ge=0)
    lease_term_months: int = Field(default=48, gt=0)
    lease_residual_value_pct: float = Field(default=0.50, ge=0, le=1)

    # --- Scenario -----------------------------------------------------------
    scenario_id: int = Field(
        ge=1,
        le=6,
        description=(
            "TCO scenario: "
            "1=Cash purchase + chargers upfront, "
            "2=Cash purchase + CaaS, "
            "3=Financed + chargers upfront, "
            "4=Financed + CaaS, "
            "5=Lease + chargers upfront, "
            "6=Lease + CaaS"
        ),
    )

    # --- Analysis period ----------------------------------------------------
    analysis_years: int = Field(
        default=ANALYSIS_YEARS,
        gt=0,
        description="Number of years in the replacement cycle",
    )


# ---------------------------------------------------------------------------
# Scenario mapping
# ---------------------------------------------------------------------------

# The original engine supports 4 financing scenarios (1–4).  The fleet
# replacement tool exposes 6 scenarios by splitting "charger upfront" vs
# "CaaS" (Charging as a Service) for each of the three vehicle financing
# modes.  We map the 6 external scenarios onto the 4 internal financing
# scenarios and handle the CaaS charger cost separately.
#
#   External → Internal financing scenario + charger mode
#   1  Cash + chargers upfront          → financing=1, caas=False
#   2  Cash + CaaS                      → financing=1, caas=True
#   3  Finance + chargers upfront       → financing=2, caas=False
#   4  Finance + CaaS                   → financing=2, caas=True
#   5  Lease + chargers upfront         → financing=4, caas=False
#   6  Lease + CaaS                     → financing=4, caas=True

_SCENARIO_MAP: dict[int, tuple[int, bool]] = {
    1: (1, False),
    2: (1, True),
    3: (2, False),
    4: (2, True),
    5: (4, False),
    6: (4, True),
}

_SCENARIO_NAMES: dict[int, str] = {
    1: "Purchase vehicles upfront & purchase chargers upfront",
    2: "Purchase vehicles upfront & purchase charging as a service (CaaS)",
    3: "Finance vehicles & purchase chargers upfront",
    4: "Finance vehicles & purchase charging as a service (CaaS)",
    5: "Lease vehicles & purchase chargers upfront",
    6: "Lease vehicles & purchase charging as a service (CaaS)",
}


# ---------------------------------------------------------------------------
# Core calculation helpers
# ---------------------------------------------------------------------------

def _compute_charger_capex(inputs: TCOInputsNoDB) -> float:
    """Total charger capital expenditure for the fleet."""
    import math
    charger_count = math.ceil(inputs.fleet_size / inputs.charger.vehicles_per_charger)
    return (
        inputs.charger.unit_cost_cad + inputs.charger.installation_cost_cad
    ) * charger_count


def _compute_ev_yearly(
    inputs: TCOInputsNoDB,
    internal_scenario_id: int,
    caas: bool,
    charger_capex: float,
) -> List[YearCostBreakdown]:
    """Year-by-year EV cost breakdown without any DB calls."""
    fleet_size = inputs.fleet_size
    annual_km = inputs.annual_km_per_vehicle * fleet_size
    ev = inputs.ev
    category = ev.vehicle_category

    tire_rates = TIRE_COST_PER_KM.get(category, TIRE_COST_PER_KM["Light Duty"])
    tire_rate = tire_rates["EV"]

    # For CaaS the charger capex is treated as an annual operating cost
    # (spread evenly over the analysis period) rather than a capital purchase.
    caas_annual_charger_cost = charger_capex / inputs.analysis_years if caas else 0.0
    capex_for_financing = 0.0 if caas else charger_capex

    yearly: List[YearCostBreakdown] = []
    for y in range(1, inputs.analysis_years + 1):
        # Vehicle + charger financing cost
        veh_cost, chrg_cost = financing.vehicle_cost_by_year(
            scenario_id=internal_scenario_id,
            msrp=ev.msrp_cad,
            charger_capex=capex_for_financing,
            loan_rate=inputs.loan_interest_rate,
            loan_down_pct=inputs.loan_down_payment_pct,
            loan_term_months=inputs.loan_term_months,
            money_factor=inputs.lease_money_factor,
            lease_term_months=inputs.lease_term_months,
            lease_residual_pct=inputs.lease_residual_value_pct,
            year=y,
            fleet_size=fleet_size,
        )

        # Charger annual maintenance (after year 1, non-CaaS only)
        charger_maint = (
            capex_for_financing * CHARGER_MAINTENANCE_PCT if (y > 1 and not caas) else 0.0
        )
        chrg_cost_total = chrg_cost + charger_maint + caas_annual_charger_cost

        # Electricity cost
        assert ev.efficiency_kwh_per_km is not None, (
            "efficiency_kwh_per_km must be set for EV vehicles"
        )
        electricity_cost = annual_km * ev.efficiency_kwh_per_km * inputs.electricity_rate_per_kwh

        # Maintenance
        maint_cost = annual_km * inputs.ev_maintenance_cost_per_km

        # Tires
        tire_cost = annual_km * tire_rate

        # Insurance (declining)
        insurance_base = ev.msrp_cad * fleet_size * INSURANCE_PCT_OF_MSRP_YEAR1
        insurance = insurance_base * ((1 - INSURANCE_ANNUAL_DECLINE) ** (y - 1))

        # Rebates (year 1 only for purchase rebates)
        rebate_total = 0.0
        if y == 1:
            rebate_total = inputs.ev_rebate_total_cad + inputs.charger_rebate_total_cad

        # CFR carbon credit revenue (annual)
        assert ev.efficiency_kwh_per_km is not None
        cfr_revenue = (
            ev.efficiency_kwh_per_km
            * inputs.annual_km_per_vehicle
            * fleet_size
            * inputs.annual_cfr_revenue_per_kwh
        )
        rebate_total += cfr_revenue

        # Salvage (final year only, negative cost)
        salvage = 0.0
        if y == inputs.analysis_years:
            salvage = -(ev.msrp_cad * fleet_size * SALVAGE_PCT["EV"])

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


def _compute_ice_yearly(
    inputs: TCOInputsNoDB,
    internal_scenario_id: int,
) -> List[YearCostBreakdown]:
    """Year-by-year ICE cost breakdown without any DB calls."""
    fleet_size = inputs.fleet_size
    annual_km = inputs.annual_km_per_vehicle * fleet_size
    ice = inputs.ice
    category = ice.vehicle_category

    tire_rates = TIRE_COST_PER_KM.get(category, TIRE_COST_PER_KM["Light Duty"])
    tire_rate = tire_rates["ICE"]

    yearly: List[YearCostBreakdown] = []
    for y in range(1, inputs.analysis_years + 1):
        # Vehicle cost (ICE has no charger)
        veh_cost, _ = financing.vehicle_cost_by_year(
            scenario_id=internal_scenario_id,
            msrp=ice.msrp_cad,
            charger_capex=0.0,
            loan_rate=inputs.loan_interest_rate,
            loan_down_pct=inputs.loan_down_payment_pct,
            loan_term_months=inputs.loan_term_months,
            money_factor=inputs.lease_money_factor,
            lease_term_months=inputs.lease_term_months,
            lease_residual_pct=inputs.lease_residual_value_pct,
            year=y,
            fleet_size=fleet_size,
        )

        # Fuel cost
        assert ice.fuel_consumption_l_per_100km is not None, (
            "fuel_consumption_l_per_100km must be set for ICE vehicles"
        )
        fuel_l_per_km = ice.fuel_consumption_l_per_100km / 100
        fuel_cost = annual_km * fuel_l_per_km * inputs.fuel_price_per_litre

        # Maintenance
        maint_cost = annual_km * inputs.ice_maintenance_cost_per_km

        # Tires
        tire_cost = annual_km * tire_rate

        # Insurance (declining)
        insurance_base = ice.msrp_cad * fleet_size * INSURANCE_PCT_OF_MSRP_YEAR1
        insurance = insurance_base * ((1 - INSURANCE_ANNUAL_DECLINE) ** (y - 1))

        # Salvage (final year only)
        salvage = 0.0
        if y == inputs.analysis_years:
            salvage = -(ice.msrp_cad * fleet_size * SALVAGE_PCT["ICE"])

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


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calculate_no_db(inputs: TCOInputsNoDB) -> float:
    """
    Compute the EV Total Cost of Ownership for a single replacement cycle
    without any database access.

    Accepts an in-memory ``TCOInputsNoDB`` Pydantic object and returns a
    scalar float representing the total EV TCO over the analysis period
    (undiscounted sum of all annual costs).

    The selected TCO scenario (``inputs.scenario_id`` 1–6) determines the
    vehicle financing mode and whether charger costs are treated as capital
    expenditure or a CaaS subscription.

    Raises
    ------
    ValueError
        If ``inputs.scenario_id`` is not in the range 1–6.
    """
    if inputs.scenario_id not in _SCENARIO_MAP:
        raise ValueError(
            f"Invalid scenario_id {inputs.scenario_id!r}. "
            f"Must be one of {sorted(_SCENARIO_MAP.keys())}."
        )

    internal_scenario_id, caas = _SCENARIO_MAP[inputs.scenario_id]
    charger_capex = _compute_charger_capex(inputs)

    ev_yearly = _compute_ev_yearly(inputs, internal_scenario_id, caas, charger_capex)
    ev_totals = [y.total for y in ev_yearly]

    return sum(ev_totals)


def calculate_no_db_full(inputs: TCOInputsNoDB) -> TCOResult:
    """
    Extended version of ``calculate_no_db()`` that returns the full
    ``TCOResult`` including both EV and ICE yearly breakdowns and NPV.

    Useful for debugging and for the TCO_Adapter when it needs to compare
    EV vs ICE costs directly.
    """
    from datetime import datetime, timezone

    if inputs.scenario_id not in _SCENARIO_MAP:
        raise ValueError(
            f"Invalid scenario_id {inputs.scenario_id!r}. "
            f"Must be one of {sorted(_SCENARIO_MAP.keys())}."
        )

    internal_scenario_id, caas = _SCENARIO_MAP[inputs.scenario_id]
    charger_capex = _compute_charger_capex(inputs)

    ev_yearly = _compute_ev_yearly(inputs, internal_scenario_id, caas, charger_capex)
    ice_yearly = _compute_ice_yearly(inputs, internal_scenario_id)

    ev_totals = [y.total for y in ev_yearly]
    ice_totals = [y.total for y in ice_yearly]

    ev_total = sum(ev_totals)
    ice_total = sum(ice_totals)
    ev_npv = present_value.npv(ev_totals, inputs.discount_rate)
    ice_npv = present_value.npv(ice_totals, inputs.discount_rate)

    total_km = inputs.annual_km_per_vehicle * inputs.fleet_size * inputs.analysis_years
    ev_cost_per_km = ev_total / total_km if total_km > 0 else 0.0
    ice_cost_per_km = ice_total / total_km if total_km > 0 else 0.0

    be_year = present_value.break_even_year(ev_totals, ice_totals)

    scenario_result = ScenarioTCO(
        scenario_name=_SCENARIO_NAMES[inputs.scenario_id],
        scenario_id=inputs.scenario_id,
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

    # Minimal VehicleSummary stubs (no DB IDs available in no-DB mode)
    from app.schemas.outputs import VehicleSummary

    ev_summary = VehicleSummary(
        id=0,
        display_name=f"BEV ({inputs.ev.vehicle_category})",
        msrp_cad=inputs.ev.msrp_cad,
        category=inputs.ev.vehicle_category,
    )
    ice_summary = VehicleSummary(
        id=0,
        display_name=f"ICE ({inputs.ice.vehicle_category})",
        msrp_cad=inputs.ice.msrp_cad,
        category=inputs.ice.vehicle_category,
    )

    import math
    charger_count = math.ceil(inputs.fleet_size / inputs.charger.vehicles_per_charger)

    return TCOResult(
        scenarios=[scenario_result],
        recommended_ev=ev_summary,
        recommended_ice=ice_summary,
        charger_count=charger_count,
        charger_total_cost=charger_capex,
        calculation_timestamp=datetime.now(timezone.utc),
    )
