from datetime import date
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    customer_id: int
    product_id: int
    channel: str = Field(min_length=2, max_length=50)
    message: str = Field(min_length=3)
    event_date: date


class FeedbackResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    customer_id: int
    product_id: int
    channel: str
    message: str
    sentiment: str | None = None
    issue_label: str | None = None
    event_date: date


class InsightItem(BaseModel):
    issue_label: str
    total_mentions: int
    negative_mentions: int
    channels: list[str]


class UploadSummary(BaseModel):
    rows_received: int
    rows_processed: int
    rows_failed: int
