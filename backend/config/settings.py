"""
Application settings and configuration management
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    API_PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/job_automation"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # API Keys
    CLAUDE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    SCRAPINGBEE_API_KEY: Optional[str] = None

    # Job Scraping Settings
    SCRAPE_INTERVAL_HOURS: int = 6
    MAX_APPLICATIONS_PER_DAY: int = 20
    MIN_MATCH_SCORE_THRESHOLD: float = 0.70

    # Job Board URLs
    INDEED_BASE_URL: str = "https://www.indeed.com"
    LINKEDIN_BASE_URL: str = "https://www.linkedin.com"
    GLASSDOOR_BASE_URL: str = "https://www.glassdoor.com"

    # Email Settings
    SENDGRID_API_KEY: Optional[str] = None
    NOTIFICATION_EMAIL: Optional[str] = None

    # AWS S3 (Optional)
    S3_BUCKET_NAME: Optional[str] = None
    S3_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # Monitoring
    SENTRY_DSN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
