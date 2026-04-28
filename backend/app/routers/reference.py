from fastapi import APIRouter
from app.engine.constants import PROVINCES

router = APIRouter(prefix="/api", tags=["reference"])


@router.get("/provinces")
def list_provinces():
    return PROVINCES
