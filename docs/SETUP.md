# Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 14+
- Redis 7+
- Git

## Local Development Setup

### 1. Clone and Configure

```bash
# Navigate to project directory
cd "Job Automation"

# Copy environment file
cp .env.example .env

# Edit .env with your API keys and configuration
# REQUIRED: CLAUDE_API_KEY, DATABASE_URL, REDIS_URL
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 3. Database Setup

```bash
# Start PostgreSQL (if not running)
# Create database
createdb job_automation

# Run migrations (once implemented)
alembic upgrade head
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 5. Start Services

You need 4 terminal windows:

**Terminal 1 - Backend API:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
source venv/bin/activate
celery -A celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat (Scheduler):**
```bash
cd backend
source venv/bin/activate
celery -A celery_app beat --loglevel=info
```

**Terminal 4 - Frontend:**
```bash
cd frontend
npm run dev
```

### 6. Access the Application

- Frontend Dashboard: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- Flower (Celery Monitor): http://localhost:5555

## Docker Setup (Easier Alternative)

```bash
# Start all services with Docker Compose
cd infrastructure/docker
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Initial Configuration

### 1. Add Your Base Resume

Place your resume in `data/resumes/base_resume.pdf` or `.docx`

### 2. Configure Job Preferences

Edit your preferences in the dashboard or database

### 3. Test Job Scraping

```bash
# Trigger manual scrape (if implemented)
curl -X POST http://localhost:8000/api/jobs/scrape
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
# Windows:
netstat -ano | findstr :8000
# Mac/Linux:
lsof -ti:8000

# Kill process
# Windows:
taskkill /PID <pid> /F
# Mac/Linux:
kill -9 <pid>
```

### Database Connection Errors

- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

### Playwright Errors

```bash
# Reinstall browsers
playwright install chromium --force
```

### Celery Not Running Tasks

- Verify Redis is running
- Check CELERY_BROKER_URL in .env
- Restart Celery worker

## Next Steps

See `docs/ARCHITECTURE.md` for system architecture overview
See backend READMEs for implementing specific features
