# Job Application Automation System - Product Requirements Document

## Executive Summary
An automated system that scrapes job postings, tailors resumes to each role using AI, and submits applications automatically.

---

## Tech Stack

### Backend
- **Language**: Python 3.11+
- **Web Scraping**: 
  - Playwright/Selenium (for dynamic sites)
  - BeautifulSoup4 + httpx (for static sites)
  - ScrapingBee API (for anti-bot bypass)
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL (job data, application history)
- **API Framework**: FastAPI

### AI/ML Components
- **Resume Tailoring**: 
  - OpenAI GPT-4o or Claude 3.5 Sonnet API
  - Alternative: Llama 3 (self-hosted for cost savings)
- **Document Processing**: 
  - python-docx (Word docs)
  - PyPDF2/pdfplumber (PDF generation)
  - Jinja2 (templating)

### Frontend (Optional Dashboard)
- **Framework**: React + TypeScript
- **UI Library**: Tailwind CSS + shadcn/ui
- **State Management**: TanStack Query

### Infrastructure
- **Hosting**: 
  - AWS EC2 t3.medium OR DigitalOcean Droplet ($24/mo)
  - Alternative: Railway.app (simpler deployment)
- **Storage**: AWS S3 (resume versions, documents)
- **Monitoring**: Sentry + Grafana
- **Scheduler**: Celery Beat (cron jobs)

---

## System Architecture

### Core Components

#### 1. Job Scraper Service
- Crawls target job boards (LinkedIn, Indeed, Glassdoor, company careers pages)
- Extracts: title, description, requirements, company, location, salary
- Frequency: Every 2-6 hours
- Stores in PostgreSQL with deduplication

#### 2. Job Matching Engine
- Scores jobs against user preferences (keywords, location, salary, etc.)
- Filters out already-applied positions
- Priority queue based on match score

#### 3. Resume Tailoring Engine
- Takes base resume + job description
- Uses LLM to:
  - Rewrite experience bullets to match job keywords
  - Adjust skills section
  - Customize summary/objective
  - Maintain truthfulness (no false information)
- Generates PDF/DOCX output

#### 4. Application Submission Service
- Fills out application forms (Playwright automation)
- Handles file uploads (resume, cover letter)
- Completes common fields (name, email, phone)
- Takes screenshots for verification

#### 5. Tracking & Analytics
- Application status tracking
- Response rate analytics
- A/B testing different resume versions

---

## Data Schema

### Jobs Table
```sql
- id (uuid)
- title (text)
- company (text)
- description (text)
- requirements (text)
- location (text)
- salary_min, salary_max (integer)
- source_url (text)
- scraped_at (timestamp)
- match_score (float)
```

### Applications Table
```sql
- id (uuid)
- job_id (foreign key)
- resume_version (text)
- applied_at (timestamp)
- status (enum: submitted, rejected, interview, offer)
- response_received (boolean)
```

---

## Features

### Phase 1 (MVP - 4-6 weeks)
- Scrape 3 major job boards
- Basic keyword matching
- AI resume tailoring
- Manual application review before submission
- Simple dashboard to approve/reject

### Phase 2 (8-10 weeks)
- Automatic application submission
- Cover letter generation
- Email integration (track responses)
- Advanced filtering (salary, remote, etc.)
- Application analytics

### Phase 3 (12+ weeks)
- Multi-user support
- Interview scheduling assistant
- Chrome extension for one-click applications
- Custom job board integrations
- ML-based match scoring

---

## Cost Breakdown (Monthly)

### Infrastructure
| Service | Cost |
|---------|------|
| DigitalOcean Droplet (4GB RAM) | $24 |
| PostgreSQL Managed DB | $15 |
| AWS S3 Storage (50GB) | $1.15 |
| Redis (Upstash) | $10 |
| Domain + SSL | $1 |
| **Subtotal** | **$51** |

### APIs & Services
| Service | Usage | Cost |
|---------|-------|------|
| OpenAI API (GPT-4o) | ~150 resumes/mo | $15-30 |
| ScrapingBee (anti-bot) | 50k requests | $49 |
| SendGrid (email) | 40k emails | Free |
| Sentry (monitoring) | Basic | Free |
| **Subtotal** | **$64-79** |

### **Total Monthly Cost: $115-130**

### Cost Optimization Options
- Use Claude API instead of OpenAI: ~40% cheaper
- Self-host Llama 3 on GPU instance: $0 API costs (but $50-100 GPU hosting)
- Skip ScrapingBee, use proxies: Save $49 (less reliable)
- Use Supabase free tier: Save $15

**Optimized Budget: $50-70/month**

---

## Hosting Options

### Option 1: DigitalOcean (Recommended)
**Pros**: Simple, predictable pricing, good docs
**Setup**: 
- 1x Droplet (4GB RAM, 2 vCPUs)
- Docker Compose deployment
- Nginx reverse proxy
- Automated backups

### Option 2: Railway.app
**Pros**: Zero DevOps, automatic scaling, built-in CI/CD
**Cons**: More expensive at scale ($20-40/mo)
**Best for**: Rapid prototyping

### Option 3: AWS EC2 + RDS
**Pros**: Maximum control, can optimize costs
**Cons**: Complex setup, unpredictable costs
**Best for**: Production at scale

---

## Legal & Ethical Considerations

### Critical Requirements
1. **Terms of Service Compliance**
   - Check each job board's ToS (many prohibit scraping)
   - Use official APIs where available (LinkedIn, Indeed)
   - Respect robots.txt and rate limits

2. **Resume Truthfulness**
   - AI should only reframe existing experience
   - Never fabricate skills, dates, or positions
   - User review before first submission

3. **Application Quality**
   - Don't spam applications to every job
   - Minimum match score threshold
   - Daily application limits

4. **Data Privacy**
   - Encrypt stored resumes
   - No sharing of personal data
   - GDPR/CCPA compliance if offering to others

---

## Implementation Timeline

### Week 1-2: Setup & Infrastructure
- Set up hosting environment
- Database schema
- Basic scraper for 1 job board

### Week 3-4: AI Integration
- OpenAI API integration
- Resume parsing and templating
- Tailoring logic

### Week 5-6: Automation & Testing
- Application form automation
- End-to-end testing
- Dashboard for monitoring

### Week 7+: Refinement
- Add more job boards
- Improve matching algorithm
- Analytics and reporting

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| IP bans from scraping | Rotate proxies, use ScrapingBee, respect rate limits |
| Captchas block automation | 2Captcha API integration, manual fallback |
| Job boards change HTML | Regular scraper updates, CSS selector monitoring |
| Poor resume quality | Human review loop, A/B testing |
| Account suspensions | Use personal email, don't spam, quality over quantity |

---

## Success Metrics

- **Applications sent**: 50-100/week
- **Response rate**: >5% (vs 1-2% manual)
- **Time saved**: 20+ hours/week
- **Interview rate**: Track improvement over baseline
- **System uptime**: >99%

---

## Alternative: Use Existing Tools

Before building, consider:
- **LazyApply** ($99-249/mo): Auto-applies to jobs
- **Simplify** (Free-$30/mo): Autofill applications
- **Sonara** ($79/mo): AI job applications
- **Teal** (Free-$29/mo): Resume tailoring

**Build if**: You want full control, custom integrations, or to learn. Otherwise, existing tools are faster to deploy.