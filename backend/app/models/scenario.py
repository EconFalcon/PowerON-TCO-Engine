from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # DutyCycle
    daily_distance_km = Column(Float, nullable=False)
    max_payload_lbs = Column(Float, nullable=False)
    vehicle_category = Column(String, nullable=False)
    refrigeration_required = Column(Boolean, nullable=False)

    # FleetParams
    province = Column(String, nullable=False)
    ev_fleet_size = Column(Integer, nullable=False)
    ice_fleet_size = Column(Integer, nullable=False)
    annual_km_per_vehicle = Column(Float, nullable=False)
    depot_charging_pct = Column(Float, nullable=False)
    public_charging_rate = Column(Float, nullable=False)
    ev_vehicles_per_charger = Column(Float, nullable=False)

    # VehicleSelection
    ev_model_id = Column(Integer, ForeignKey("ev_vehicles.id"), nullable=True)
    ice_model_id = Column(Integer, ForeignKey("ice_vehicles.id"), nullable=True)
    charger_type_id = Column(Integer, ForeignKey("chargers.id"), nullable=True)

    # LoanParams (Scenario 3)
    loan_interest_rate = Column(Float, nullable=True)
    loan_down_payment_pct = Column(Float, nullable=True)
    loan_term_months = Column(Integer, nullable=True)

    # LeaseParams (Scenario 4)
    lease_money_factor = Column(Float, nullable=True)
    lease_term_months = Column(Integer, nullable=True)
    lease_residual_pct = Column(Float, nullable=True)

    # Misc
    analysis_year = Column(Integer, default=2025)
    discount_rate = Column(Float, default=0.08)

    # Cached result
    result_json = Column(Text, nullable=True)
