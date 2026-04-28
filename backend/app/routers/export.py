from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.inputs import TCOInputs
from app.schemas.outputs import TCOResult
from app.engine.tco_calculator import calculate

router = APIRouter(prefix="/api/export", tags=["export"])


class ExportRequest(TCOInputs):
    pass


@router.post("/pdf")
def export_pdf(inputs: ExportRequest, db: Session = Depends(get_db)):
    from app.pdf.generator import generate_pdf
    result = calculate(inputs, db)
    pdf_bytes = generate_pdf(inputs, result)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="PowerOn_TCO_Report.pdf"'},
    )
