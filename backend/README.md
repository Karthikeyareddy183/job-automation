# Backend

FastAPI-based backend service for job automation system.

## Directory Structure

### `/services`
Core business logic modules:
- `scraper.py` - Job board scraping (Playwright/BeautifulSoup)
- `matching.py` - Job matching and scoring algorithm
- `resume_tailor.py` - AI-powered resume customization (Claude API)
- `automation.py` - Application form automation (Phase 2)
- `email_service.py` - Email tracking and notifications

### `/tasks`
Celery async tasks:
- `scrape_jobs.py` - Scheduled job scraping tasks
- `process_applications.py` - Background application processing
- `cleanup.py` - Database maintenance tasks

### `/models`
SQLAlchemy ORM models:
- `job.py` - Job postings schema
- `application.py` - Application tracking
- `user.py` - User profiles and preferences
- `resume.py` - Resume versions and templates

### `/api`
FastAPI route handlers:
- `jobs.py` - Job listing endpoints
- `applications.py` - Application management
- `resumes.py` - Resume CRUD operations
- `auth.py` - Authentication (if multi-user)

### `/db`
Database configuration:
- `session.py` - SQLAlchemy session management
- `migrations/` - Alembic migration scripts

### `/utils`
Helper functions:
- `validators.py` - Input validation
- `parsers.py` - Resume/job description parsing
- `formatters.py` - Data formatting utilities

### `/config`
Configuration files:
- `settings.py` - Environment-based settings
- `constants.py` - Application constants
- `logging.py` - Logging configuration

### `/tests`
Unit and integration tests
