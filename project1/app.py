
from fastapi import FastAPI

from backend.routes.analyze import router as analyze_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Resume Analyzer API",
    description="API for analyzing resumes against job descriptions",
    version="1.0.0"
)
# CORS Configuration
origins = [
    "http://localhost:8501",  # Streamlit
    "http://127.0.0.1:8501",  # Streamlit
    "http://localhost:3000",  # React
    "http://localhost:5173",  # Vite
    "http://localhost:5174",  # Vite
    "https://resumeanalyzer-2zg.pages.dev",   # final -url 
    "https://ai-resume-analyzer-2m6nxxa1q-acme-4a68.vercel.app",   # final -url 
    "https://ai-resume-analyzer-28c86tn3a-acme-4a68.vercel.app",   # final -url 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
