# Job Application Automation System

Automated job application system that scrapes postings, tailors resumes using AI, and manages applications.

## Project Structure

```
job-automation/
├── backend/              # FastAPI backend service
│   ├── services/         # Business logic (scraping, matching, AI)
│   ├── tasks/           # Celery background tasks
│   ├── models/          # Database models (SQLAlchemy)
│   ├── api/             # API endpoints
│   ├── db/              # Database configuration
│   ├── utils/           # Helper functions
│   ├── config/          # Settings and configuration
│   └── tests/           # Backend tests
├── frontend/            # React + TypeScript dashboard
│   └── src/
│       ├── components/  # Reusable UI components
│       ├── pages/       # Page components
│       ├── hooks/       # Custom React hooks
│       ├── services/    # API client services
│       ├── types/       # TypeScript definitions
│       └── utils/       # Frontend utilities
├── infrastructure/      # Deployment configuration
│   ├── docker/         # Docker files
│   ├── nginx/          # Reverse proxy config
│   └── scripts/        # Deployment scripts
├── data/               # Local data storage (gitignored)
│   ├── resumes/        # Generated resume versions
│   ├── templates/      # Resume templates
│   └── logs/           # Application logs
├── docs/               # Documentation
└── job_automation_prd.md  # Product requirements

```

## Tech Stack

**Backend**: Python 3.11+, FastAPI, PostgreSQL, Redis, Celery
**Scraping**: Playwright, BeautifulSoup4, httpx
**AI**: Claude 3.5 Sonnet API (resume tailoring)
**Frontend**: React, TypeScript, Tailwind CSS, TanStack Query
**Hosting**: Railway.app / DigitalOcean

## Getting Started

See `docs/SETUP.md` for detailed setup instructions.

## Development Phases

**Phase 1 (MVP)**: Job scraping, AI resume tailoring, manual review dashboard
**Phase 2**: Automatic submission, cover letters, email tracking
**Phase 3**: Multi-user, interview assistant, Chrome extension

## Legal Notice

This tool is for personal use. Respect job board Terms of Service and robots.txt. Never fabricate information in resumes.
