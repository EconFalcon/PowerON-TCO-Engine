from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models.reference_data import EVVehicle, ICEVehicle

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


class EVVehicleOut(BaseModel):
    id: int
    display_name: str
    make: str
    model: str
    year: int | None
    msrp_cad: float
    battery_kwh: float
    efficiency_kwh_per_km: float
    range_km: float
    payload_lbs: float
    category: str
    has_refrigeration: bool

    model_config = {"from_attributes": True}


class ICEVehicleOut(BaseModel):
    id: int
    display_name: str
    make: str
    model: str
    year: int | None
    msrp_cad: float
    fuel_type: str
    fuel_consumption_l_per_100km: float
    payload_lbs: float
    category: str

    model_config = {"from_attributes": True}


@router.get("/ev", response_model=List[EVVehicleOut])
def list_ev_vehicles(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(EVVehicle)
    if category:
        query = query.filter(EVVehicle.category == category)
    return query.order_by(EVVehicle.display_name).all()


@router.get("/ice", response_model=List[ICEVehicleOut])
def list_ice_vehicles(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(ICEVehicle)
    if category:
        query = query.filter(ICEVehicle.category == category)
    return query.order_by(ICEVehicle.display_name).all()
