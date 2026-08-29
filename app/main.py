from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.config.database import engine, Base
from app.api import router as api_router
from app.services.predictions import get_ml_bundle

# Initialize Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI Backend for SIH26103 Integrated Project Monitoring Platform with ML Delay Classification",
    docs_url="/docs",
    redoc_url="/redoc"
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
app.include_router(api_router, prefix=settings.API_PREFIX)
app.include_router(api_router)  # Also mount at root for convenient direct calls

@app.on_event("startup")
def startup_event():
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    # Verify or initialize ML Model
    try:
        bundle = get_ml_bundle()
        print(f"Loaded ML Model: '{bundle.get('model_name')}' successfully.")
    except Exception as e:
        print(f"Warning: Could not pre-load ML model: {e}")

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
