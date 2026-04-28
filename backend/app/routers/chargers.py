from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models.reference_data import Charger

router = APIRouter(prefix="/api/chargers", tags=["chargers"])


class ChargerOut(BaseModel):
    id: int
    display_name: str
    type_name: str
    power_kw: float
    unit_cost_cad: float
    installation_cost_cad: float
    lifespan_years: int

    model_config = {"from_attributes": True}


@router.get("", response_model=List[ChargerOut])
def list_chargers(db: Session = Depends(get_db)):
    return db.query(Charger).order_by(Charger.power_kw).all()
