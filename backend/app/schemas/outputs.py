from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class YearCostBreakdown(BaseModel):
    year: int
    vehicle_cost: float
    fuel_or_electricity: float
    maintenance: float
    tires: float
    insurance: float
    charger_cost: float
    rebates: float
    salvage: float
    total: float


class VehicleSummary(BaseModel):
    id: int
    display_name: str
    msrp_cad: float
    category: str


class ScenarioTCO(BaseModel):
    scenario_name: str
    scenario_id: int
    ev_total_tco: float
    ice_total_tco: float
    ev_npv: float
    ice_npv: float
    ev_cost_per_km: float
    ice_cost_per_km: float
    savings_vs_ice: float
    break_even_year: Optional[int]
    ev_yearly: List[YearCostBreakdown]
    ice_yearly: List[YearCostBreakdown]


class TCOResult(BaseModel):
    scenarios: List[ScenarioTCO]
    recommended_ev: VehicleSummary
    recommended_ice: VehicleSummary
    charger_count: int
    charger_total_cost: float
    calculation_timestamp: datetime
