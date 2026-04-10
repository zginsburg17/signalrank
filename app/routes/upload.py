from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.security import validate_api_key
from app.dependencies import get_db
from app.schemas import UploadSummary
from app.services.ingestion import IngestionService

router = APIRouter(prefix="/upload", tags=["upload"], dependencies=[Depends(validate_api_key)])
service = IngestionService()


@router.post("/csv", response_model=UploadSummary)
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = await file.read()
    try:
        summary = service.process_csv_bytes(contents, db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return summary
