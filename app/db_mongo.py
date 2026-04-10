from pymongo import MongoClient
from app.core.config import settings


mongo_client = MongoClient(settings.mongo_url)
mongo_db = mongo_client[settings.mongo_db_name]
raw_feedback_collection = mongo_db["raw_feedback"]
enrichment_results_collection = mongo_db["enrichment_results"]
issue_snapshots_collection = mongo_db["issue_snapshots"]
