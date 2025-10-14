#!/bin/bash
# Initial setup script for Job Automation System

set -e

echo "=== Job Automation System Setup ==="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual configuration"
fi

# Create data directories
echo "Creating data directories..."
mkdir -p data/resumes data/logs data/templates

# Install Python dependencies
echo "Installing Python dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys and configuration"
echo "2. Start PostgreSQL and Redis (or use Docker: docker-compose up postgres redis)"
echo "3. Run database migrations: cd backend && alembic upgrade head"
echo "4. Start the backend: cd backend && python main.py"
echo "5. Start the frontend: cd frontend && npm run dev"
echo "6. Start Celery worker: cd backend && celery -A celery_app worker -l info"
echo "7. Start Celery beat: cd backend && celery -A celery_app beat -l info"
