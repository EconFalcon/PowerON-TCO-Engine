from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.inputs import TCOInputs
from app.schemas.outputs import TCOResult


class ScenarioCreate(BaseModel):
    name: str
    inputs: TCOInputs
    result: Optional[TCOResult] = None


class ScenarioSummary(BaseModel):
    id: int
    name: str
    created_at: datetime
    province: str
    ev_fleet_size: int
    ice_fleet_size: int
    vehicle_category: str
    ev_total_tco_cash: Optional[float] = None

    model_config = {"from_attributes": True}


class ScenarioDetail(BaseModel):
    id: int
    name: str
    created_at: datetime
    inputs: TCOInputs
    result: Optional[TCOResult] = None

    model_config = {"from_attributes": True}
