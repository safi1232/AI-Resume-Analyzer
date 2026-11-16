
from fastapi import FastAPI

from backend.routes.analyze import router as analyze_router


app = FastAPI(
    title="AI Resume Analyzer API",
    description="API for analyzing resumes against job descriptions",
    version="1.0.0"
)


@app.get("/")
def home():

    return {
        "message": "Welcome to AI Resume Analyzer API",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


app.include_router(analyze_router)
