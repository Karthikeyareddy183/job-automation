# Quick Start Guide - AI Agent System

Get the AI agent system up and running in 5 minutes.

## Prerequisites

- Python 3.11+ installed
- All dependencies installed (`pip install -r backend/requirements.txt`)
- Database migrated (Supabase PostgreSQL)

## Step 1: Get API Keys (Optional for Testing)

### For Mock Testing (No API Keys Needed)
You can test the system immediately with mock data without any API keys.

### For Real LLM Testing
1. **Groq API Key** (Free tier available)
   - Go to https://console.groq.com/keys
   - Sign up for free account
   - Create an API key
   - Copy the key (starts with `gsk_`)

### For Email Approvals
2. **SendGrid API Key** (Free: 100 emails/day)
   - Go to https://signup.sendgrid.com/
   - Create free account
   - Go to Settings → API Keys
   - Create an API key
   - Copy the key (starts with `SG.`)

## Step 2: Configure Environment

Edit `.env` file in the project root:

```bash
# Add your Groq API key (required for real LLM)
GROQ_API_KEY=gsk_your_actual_key_here

# Add your SendGrid credentials (optional for testing)
SENDGRID_API_KEY=SG.your_actual_key_here
NOTIFICATION_EMAIL=your-email@example.com

# These are already configured
MIN_MATCH_SCORE_THRESHOLD=0.70
MAX_APPLICATIONS_PER_DAY=20
```

## Step 3: Test the System

### Option A: Quick Test (Mock Data - No API Keys)

```bash
cd backend
python test_agents.py
```

Press Enter to run the full workflow test. This uses mock data and works without API keys.

### Option B: Test with Real LLM

After adding your Groq API key to `.env`:

```bash
cd backend
python test_agents.py
```

The agents will use real LLM calls for:
- Job matching with reasoning
- Resume tailoring with changes

### Option C: Test Individual Agents

```bash
cd backend
python test_agents.py
```

Choose option `2` to test each agent individually.

## Step 4: Understand the Output

The test will show:

```
🤖 JOB APPLICATION AGENT WORKFLOW TEST
================================================================================

📋 USER PREFERENCES:
  Keywords: ['Python', 'Django', 'FastAPI']
  Location: Remote
  Job Type: Full-time
  Min Salary: $80,000

🚀 Starting workflow...

📥 SCRAPED JOBS: 5
  1. Software Engineer - Python at Tech Company 1
  2. Backend Developer at Tech Company 2
  ...

🎯 MATCHED JOBS: 2
  1. Software Engineer - Python at Tech Company 1 (score: 0.85)
  2. Backend Developer at Tech Company 2 (score: 0.78)

📄 RESUME TAILORED:
  Changes made: 3
    1. Updated professional summary
    2. Reordered skills
    3. Highlighted relevant projects

🤖 AGENT DECISIONS: 5
  [scraper] scraped_5_jobs
  [matcher] matched_2_of_5_jobs
  ...

📊 LEARNING INSIGHTS:
  Match rate: 40.0%
  Recommendations:
    - Match rate is reasonable

⏳ NEXT STEP: Waiting for user approval via email
```

## Step 5: Integrate with Your Application

### Use in Python Code

```python
from agents import run_job_application_workflow

# Define user preferences
user_preferences = {
    "keywords": ["Python", "Django", "FastAPI"],
    "location": "Remote",
    "job_type": "Full-time",
    "experience_level": "Mid-level",
    "salary_min": 80000,
    "skills": ["Python", "React", "PostgreSQL", "Docker"]
}

# Run workflow
final_state = await run_job_application_workflow(
    user_id="user-123",
    user_preferences=user_preferences
)

# Check results
print(f"Matched {len(final_state['matched_jobs'])} jobs")
```

### Use Individual Agents

```python
from agents import ScraperAgent, create_initial_state

# Create initial state
state = create_initial_state(
    user_id="user-123",
    user_preferences={"keywords": ["Python"]}
)

# Run scraper
scraper = ScraperAgent()
state = await scraper.execute(state)

print(f"Scraped {len(state['scraped_jobs'])} jobs")
```

## Agent Workflow

```
1. SCRAPE   → Find jobs matching user keywords
2. MATCH    → Score jobs using LLM (filter by threshold)
3. TAILOR   → Customize resume for best match
4. APPROVE  → Send email to user for approval
5. WAIT     → Wait for user response (24h timeout)
6. APPLY    → Submit application (if approved)
7. LEARN    → Analyze results and improve
```

## Customization

### Adjust Match Threshold

Edit `.env`:
```bash
MIN_MATCH_SCORE_THRESHOLD=0.80  # Be more selective
```

Or in code:
```python
from agents import MatcherAgent

matcher = MatcherAgent()
matcher.min_score_threshold = 0.80
```

### Change LLM Models

Edit agent files to use different models:

```python
# In matcher_agent.py
def __init__(self):
    super().__init__(
        name="Matcher",
        model="llama-3.1-70b-versatile",  # Use larger model
        temperature=0.3
    )
```

Available models:
- `llama-3.1-8b-instant` - Fast, cheap (current for most agents)
- `llama-3.1-70b-versatile` - High quality (current for resume/learning)
- `llama-3.3-70b-versatile` - Latest, best quality
- `mixtral-8x7b-32768` - Alternative, long context

### Customize Resume Tailoring

Edit prompts in `resume_tailor_agent.py`:

```python
def _build_tailoring_prompt(self, base_resume, job, user_preferences):
    # Add your custom instructions
    prompt = f"""
    Your custom instructions here...

    Make the resume more {your_preference}...
    """
```

## Troubleshooting

### "No module named 'agents'"

```bash
# Make sure you're in the backend directory
cd backend
python test_agents.py
```

### "GROQ_API_KEY not set"

The system will work with mock data. To use real LLM:
1. Get API key from https://console.groq.com/keys
2. Add to `.env`: `GROQ_API_KEY=gsk_your_key_here`

### "Failed to invoke LLM"

Check:
- API key is correct in `.env`
- You have internet connection
- Groq API is not down (check https://status.groq.com)

### Import Errors

Reinstall dependencies:
```bash
pip install -r requirements.txt
```

## What's Next?

1. **Add Real Scraping**
   - Implement Playwright or ScrapingBee integration
   - Currently using mock data

2. **Database Persistence**
   - Save workflow states to database
   - Store approval requests
   - Track learning metrics

3. **API Endpoints**
   - Create FastAPI endpoints for frontend
   - WebSocket for real-time updates

4. **Frontend Integration**
   - Build React dashboard
   - Create approval page for magic links
   - User settings for agent control

5. **Production Deployment**
   - Set up Celery for background tasks
   - Add monitoring (Sentry)
   - Configure rate limiting

## Architecture Overview

```
User Preferences → Workflow → [Scraper → Matcher → Resume Tailor]
                       ↓
                  Supervisor (decides next step)
                       ↓
                  Email Approval → Wait for User
                       ↓
                  [Apply → Learn] → End
```

## Need Help?

Check these files:
- `backend/agents/README.md` - Detailed agent documentation
- `AGENT_IMPLEMENTATION_SUMMARY.md` - Complete implementation details
- `backend/test_agents.py` - Example usage

## Success!

You now have a working AI agent system that can:
- ✅ Scrape jobs intelligently
- ✅ Match jobs using LLM reasoning
- ✅ Tailor resumes automatically
- ✅ Request user approval
- ✅ Learn and improve over time

Start testing and enjoy your autonomous job application assistant!
