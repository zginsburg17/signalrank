from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import validate_api_key
from app.dependencies import get_db
from app.repos.postgres_repo import FeedbackPostgresRepo
from app.schemas import InsightItem
from app.services.ranking import RankingService

router = APIRouter(prefix="/insights", tags=["insights"], dependencies=[Depends(validate_api_key)])
ranking_service = RankingService()


@router.get("/issues", response_model=list[InsightItem])
def get_issue_insights(db: Session = Depends(get_db)):
    rows = FeedbackPostgresRepo(db).list_feedback(limit=1000)
    return ranking_service.build_issue_summary(rows)
