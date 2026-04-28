from sqlalchemy import Column, Integer, Float, String, Boolean, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class EVVehicle(Base):
    __tablename__ = "ev_vehicles"

    id = Column(Integer, primary_key=True)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer)
    msrp_cad = Column(Float, nullable=False)
    battery_kwh = Column(Float, nullable=False)
    efficiency_kwh_per_km = Column(Float, nullable=False)
    range_km = Column(Float, nullable=False)
    payload_lbs = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    has_refrigeration = Column(Boolean, default=False)
    imhzev_rebate_eligible = Column(Boolean, default=True)
    display_name = Column(String, nullable=False)

    provincial_rebates = relationship("EVProvincialRebate", back_populates="ev_vehicle")


class EVProvincialRebate(Base):
    __tablename__ = "ev_provincial_rebates"

    id = Column(Integer, primary_key=True)
    ev_vehicle_id = Column(Integer, ForeignKey("ev_vehicles.id"), nullable=False)
    province = Column(String, nullable=False)
    rebate_amount_cad = Column(Float, nullable=False)

    ev_vehicle = relationship("EVVehicle", back_populates="provincial_rebates")

    __table_args__ = (UniqueConstraint("ev_vehicle_id", "province"),)


class ICEVehicle(Base):
    __tablename__ = "ice_vehicles"

    id = Column(Integer, primary_key=True)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer)
    msrp_cad = Column(Float, nullable=False)
    fuel_type = Column(String, nullable=False)
    fuel_consumption_l_per_100km = Column(Float, nullable=False)
    payload_lbs = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    display_name = Column(String, nullable=False)


class Charger(Base):
    __tablename__ = "chargers"

    id = Column(Integer, primary_key=True)
    type_name = Column(String, nullable=False)
    power_kw = Column(Float, nullable=False)
    unit_cost_cad = Column(Float, nullable=False)
    installation_cost_cad = Column(Float, nullable=False)
    lifespan_years = Column(Integer, nullable=False)
    display_name = Column(String, nullable=False)


class ProvincialFuelCost(Base):
    __tablename__ = "provincial_fuel_costs"

    id = Column(Integer, primary_key=True)
    province = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    electricity_rate_kwh = Column(Float, nullable=False)
    diesel_price_l = Column(Float, nullable=False)
    gasoline_price_l = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("province", "year"),)


class MaintenanceCost(Base):
    __tablename__ = "maintenance_costs"

    id = Column(Integer, primary_key=True)
    vehicle_category = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=False)  # 'EV' | 'ICE'
    cost_per_km = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("vehicle_category", "vehicle_type"),)


class CarbonCredit(Base):
    __tablename__ = "carbon_credits"

    id = Column(Integer, primary_key=True)
    province = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=True)
    credit_value_per_tonne = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("province", "year", "month"),)


class ChargerIncentive(Base):
    __tablename__ = "charger_incentives"

    id = Column(Integer, primary_key=True)
    province = Column(String, nullable=False)
    charger_type = Column(String, nullable=False)
    power_kw = Column(Float, nullable=True)
    rebate_amount_cad = Column(Float, nullable=False)
