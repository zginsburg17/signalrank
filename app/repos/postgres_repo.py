from sqlalchemy.orm import Session
from app.models.feedback import Feedback


class FeedbackPostgresRepo:
    def __init__(self, db: Session):
        self.db = db

    def create_feedback(
        self,
        customer_id: int,
        product_id: int,
        channel: str,
        message: str,
        event_date,
    ) -> Feedback:
        feedback = Feedback(
            customer_id=customer_id,
            product_id=product_id,
            channel=channel,
            message=message,
            event_date=event_date,
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def update_feedback_enrichment(self, feedback: Feedback, sentiment: str | None, issue_label: str | None) -> Feedback:
        feedback.sentiment = sentiment
        feedback.issue_label = issue_label
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def list_feedback(self, limit: int = 100) -> list[Feedback]:
        return self.db.query(Feedback).order_by(Feedback.id.desc()).limit(limit).all()
