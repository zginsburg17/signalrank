from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import configure_logging
from app.db_postgres import Base, engine
from app.routes.feedback import router as feedback_router
from app.routes.health import router as health_router
from app.routes.insights import router as insights_router
from app.routes.upload import router as upload_router

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(health_router)
app.include_router(feedback_router, prefix=settings.api_prefix)
app.include_router(upload_router, prefix=settings.api_prefix)
app.include_router(insights_router, prefix=settings.api_prefix)
