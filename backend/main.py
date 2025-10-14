"""
FastAPI application entry point for Job Automation System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import configuration
from config.settings import settings

# Import API routers (to be created)
# from api import jobs, applications, resumes, auth

app = FastAPI(
    title="Job Automation API",
    description="Automated job application system with AI-powered resume tailoring",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Job Automation API",
        "version": "0.1.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check with service status"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB check
        "redis": "connected",     # TODO: Add actual Redis check
        "environment": settings.ENVIRONMENT
    }


# Register API routers
# app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
# app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
# app.include_router(resumes.router, prefix="/api/resumes", tags=["resumes"])
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
