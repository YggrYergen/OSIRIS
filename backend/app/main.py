from fastapi import FastAPI
from app.core.config import settings
from app.core.logging_config import setup_logging

# Initialize logging before app creation
setup_logging(log_level="DEBUG") # Default to DEBUG for dev as requested

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

@app.get("/")
def root():
    return {"message": "Omni-Channel Dev Orchestrator API is running"}

from app.api.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
