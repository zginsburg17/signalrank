from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import validate_api_key
from app.dependencies import get_db
from app.schemas import FeedbackCreate, FeedbackResponse
from app.services.ingestion import IngestionService

router = APIRouter(prefix="/feedback", tags=["feedback"], dependencies=[Depends(validate_api_key)])
service = IngestionService()


@router.post("", response_model=FeedbackResponse)
def create_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    return service.process_feedback(payload, db)
