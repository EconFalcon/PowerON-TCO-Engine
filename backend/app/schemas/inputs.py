from pydantic import BaseModel, Field
from typing import Optional


class DutyCycle(BaseModel):
    daily_distance_km: float = Field(gt=0, description="Required daily driving distance in km")
    max_payload_lbs: float = Field(ge=0, description="Maximum payload requirement in lbs")
    vehicle_category: str = Field(description="'Light Duty' | 'Medium Duty' | 'Heavy Duty'")
    refrigeration_required: bool = False


class FleetParams(BaseModel):
    province: str = Field(description="Canadian province code e.g. 'ON'")
    ev_fleet_size: int = Field(gt=0)
    ice_fleet_size: int = Field(gt=0)
    annual_km_per_vehicle: float = Field(gt=0)
    depot_charging_pct: float = Field(ge=0, le=1, description="Fraction of charging done at depot (0-1)")
    public_charging_rate_per_kwh: float = Field(ge=0, description="Public charging rate $/kWh")
    ev_vehicles_per_charger: float = Field(gt=0, description="Number of EVs sharing each charger")


class VehicleSelection(BaseModel):
    ev_model_id: Optional[int] = None
    ice_model_id: Optional[int] = None
    charger_type_id: Optional[int] = None


class LoanParams(BaseModel):
    interest_rate: float = Field(default=0.065, ge=0, le=1)
    down_payment_pct: float = Field(default=0.20, ge=0, le=1)
    loan_term_months: int = Field(default=60, gt=0)


class LeaseParams(BaseModel):
    money_factor: float = Field(default=0.00125, ge=0)
    lease_term_months: int = Field(default=48, gt=0)
    residual_value_pct: float = Field(default=0.50, ge=0, le=1)


class TCOInputs(BaseModel):
    duty_cycle: DutyCycle
    fleet: FleetParams
    vehicles: VehicleSelection
    loan: LoanParams = Field(default_factory=LoanParams)
    lease: LeaseParams = Field(default_factory=LeaseParams)
    analysis_year: int = 2025
    discount_rate: float = Field(default=0.08, ge=0, le=1)
