from io import StringIO
import pandas as pd
from sqlalchemy.orm import Session
from app.repos.mongo_repo import FeedbackMongoRepo
from app.repos.postgres_repo import FeedbackPostgresRepo
from app.schemas import FeedbackCreate
from app.services.enrichment import EnrichmentService


class IngestionService:
    def __init__(self):
        self.mongo_repo = FeedbackMongoRepo()
        self.enrichment_service = EnrichmentService()

    def process_feedback(self, payload: FeedbackCreate, db: Session) -> dict:
        postgres_repo = FeedbackPostgresRepo(db)

        feedback = postgres_repo.create_feedback(
            customer_id=payload.customer_id,
            product_id=payload.product_id,
            channel=payload.channel,
            message=payload.message,
            event_date=payload.event_date,
        )

        self.mongo_repo.insert_raw_feedback({
            "feedback_id": feedback.id,
            "customer_id": payload.customer_id,
            "product_id": payload.product_id,
            "channel": payload.channel,
            "message": payload.message,
            "event_date": payload.event_date.isoformat(),
        })

        enrichment = self.enrichment_service.analyze_text(payload.message)

        self.mongo_repo.insert_enrichment_result({
            "feedback_id": feedback.id,
            "result": enrichment,
        })

        feedback = postgres_repo.update_feedback_enrichment(
            feedback=feedback,
            sentiment=enrichment.get("sentiment"),
            issue_label=enrichment.get("issue_label"),
        )

        return {
            "id": feedback.id,
            "customer_id": feedback.customer_id,
            "product_id": feedback.product_id,
            "channel": feedback.channel,
            "message": feedback.message,
            "sentiment": feedback.sentiment,
            "issue_label": feedback.issue_label,
            "event_date": feedback.event_date,
        }

    def process_csv_bytes(self, file_bytes: bytes, db: Session) -> dict:
        dataframe = pd.read_csv(StringIO(file_bytes.decode("utf-8")))
        required_columns = {"customer_id", "product_id", "channel", "message", "event_date"}
        missing = required_columns - set(dataframe.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        processed = 0
        failed = 0

        for _, row in dataframe.iterrows():
            try:
                payload = FeedbackCreate(
                    customer_id=int(row["customer_id"]),
                    product_id=int(row["product_id"]),
                    channel=str(row["channel"]),
                    message=str(row["message"]),
                    event_date=pd.to_datetime(row["event_date"]).date(),
                )
                self.process_feedback(payload, db)
                processed += 1
            except Exception:
                failed += 1

        return {
            "rows_received": len(dataframe),
            "rows_processed": processed,
            "rows_failed": failed,
        }
