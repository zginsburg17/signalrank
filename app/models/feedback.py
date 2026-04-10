from sqlalchemy import Column, Date, DateTime, Integer, String, Text
from sqlalchemy.sql import func
from app.db_postgres import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    channel = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    sentiment = Column(String(50), nullable=True)
    issue_label = Column(String(100), nullable=True)
    event_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
