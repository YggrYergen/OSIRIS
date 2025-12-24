from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging

# Initialize logging before app creation
setup_logging(log_level="DEBUG")

app = FastAPI(
    title=settings.PROJECT_NAME, 
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all origins enabled for development
# In production, this should be restricted
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Omni-Channel Dev Orchestrator API is running"}

from app.api.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
