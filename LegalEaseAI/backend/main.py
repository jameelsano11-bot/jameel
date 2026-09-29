from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.routes import router


settings = get_settings()


app = FastAPI(
    title="LegalEase API",
    version="1.0.0",
    description=(
        "AI-powered legal document drafting API "
        "using Gemini."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/")
def root():
    """
    Root API endpoint.
    """

    return {
        "service": settings.app_name,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }