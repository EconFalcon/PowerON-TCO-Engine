from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.inputs import TCOInputs
from app.schemas.outputs import TCOResult
from app.engine.tco_calculator import calculate
from app.engine.vehicle_selector import NoCandidateError

router = APIRouter(prefix="/api", tags=["calculate"])


@router.post("/calculate", response_model=TCOResult)
def run_calculation(inputs: TCOInputs, db: Session = Depends(get_db)):
    try:
        return calculate(inputs, db)
    except NoCandidateError as e:
        raise HTTPException(status_code=422, detail=str(e))
