import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.config.database import engine, Base, init_db
from app.api import router as api_router, auth_router
from app.services.predictions import get_ml_bundle

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    # Verify or initialize ML Model
    try:
        bundle = get_ml_bundle()
        print(f"Loaded ML Model: '{bundle.get('model_name')}' successfully.")
    except Exception as e:
        print(f"Warning: Could not pre-load ML model: {e}")
    yield

# Initialize Database tables
init_db(engine)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI Backend for SIH26103 Integrated Project Monitoring Platform with ML Delay Classification",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(api_router, prefix=settings.API_PREFIX)
app.include_router(api_router)  # Also mount at root for convenient direct calls


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
