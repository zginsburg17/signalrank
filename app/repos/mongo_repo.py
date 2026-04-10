from app.db_mongo import (
    enrichment_results_collection,
    issue_snapshots_collection,
    raw_feedback_collection,
)


class FeedbackMongoRepo:
    def insert_raw_feedback(self, payload: dict) -> None:
        raw_feedback_collection.insert_one(payload)

    def insert_enrichment_result(self, payload: dict) -> None:
        enrichment_results_collection.insert_one(payload)

    def insert_issue_snapshot(self, payload: dict) -> None:
        issue_snapshots_collection.insert_one(payload)
