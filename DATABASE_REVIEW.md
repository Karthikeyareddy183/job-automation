# Database Schema Review for Agent System

## Current Database Schema ✅

### Existing Tables (Already Built)
1. **users** - User accounts and preferences ✅
2. **jobs** - Scraped job postings ✅
3. **applications** - Application tracking ✅
4. **resumes** - Resume versions ✅

---

## Analysis: What's Missing for Agent System? 🔍

### ❌ **CRITICAL MISSING TABLES** (Required for Agent System)

#### 1. **approval_requests** ❌ MUST ADD
**Purpose:** Email approval workflow with 24h timeout

**Why Needed:**
- Agents send approval emails before applying
- Track approval status (pending/approved/rejected/expired)
- 24-hour timeout mechanism
- Magic link tokens for approve/reject

**Fields Needed:**
```sql
- id (UUID)
- application_id (FK) - Links to applications table
- user_id (FK)
- job_id (FK)
- resume_id (FK)
- sent_at (DateTime)
- expires_at (DateTime) - 24h from sent_at
- status (pending/approved/rejected/expired)
- approval_token (unique string) - For magic links
- user_response (Text) - Optional feedback
- agent_reasoning (Text) - Why agent recommended this job
```

#### 2. **agent_learning** ❌ MUST ADD
**Purpose:** Store agent learning metrics and improvements

**Why Needed:**
- Track what agents learn over time
- Measure success rates of different strategies
- Store A/B test results
- Continuous improvement tracking

**Fields Needed:**
```sql
- id (UUID)
- agent_type (scraper/matcher/resume/application/learning)
- metric_name (keyword_success_rate, resume_format_performance, etc.)
- metric_value (Float)
- context (JSONB) - What was tried, what worked
- success_rate (Float) - 0.0 to 1.0
- sample_size (Integer) - How many data points
- timestamp (DateTime)
- user_id (FK) - Optional, for per-user learning
```

#### 3. **feedback_loop** ❌ MUST ADD
**Purpose:** Capture outcomes and agent insights

**Why Needed:**
- Track every application outcome
- Store what agents learned from each result
- Record strategy adjustments
- Build knowledge base for future decisions

**Fields Needed:**
```sql
- id (UUID)
- application_id (FK) - Links to specific application
- outcome (response/rejection/interview/offer/no_response)
- outcome_timestamp (DateTime)
- insights (JSONB) - What agent learned
  {
    "successful_keywords": ["python", "ai"],
    "resume_version_used": "v2.0",
    "response_time_days": 3
  }
- strategy_adjustments (JSONB) - How agent will change
  {
    "increase_keyword_density": true,
    "try_different_format": false,
    "adjust_match_threshold": 0.75
  }
- agent_notes (Text) - Human-readable insights
```

#### 4. **agent_memory** ❌ MUST ADD
**Purpose:** Vector store metadata for RAG (Retrieval Augmented Generation)

**Why Needed:**
- Store embeddings of successful resumes
- Quick similarity search for new jobs
- RAG: "Find resumes similar to this job description"
- Build knowledge base over time

**Fields Needed:**
```sql
- id (UUID)
- memory_type (successful_resume/rejection_pattern/company_insight)
- content (Text) - What to remember
- embedding_id (String) - ChromaDB collection ID
- relevance_score (Float) - How relevant/important
- usage_count (Integer) - How often referenced
- last_used_at (DateTime)
- metadata (JSONB) - Additional context
```

---

### ⚠️ **FIELDS TO ADD TO EXISTING TABLES**

#### **users** table - Add these fields:
```sql
- agent_status (String) - active/paused/stopped - Default: 'active'
- last_agent_run (DateTime) - When agents last processed for this user
- learning_enabled (Boolean) - Default: true
- approval_timeout_hours (Integer) - Default: 24
- agent_preferences (JSONB) - Agent-specific settings
  {
    "scrape_frequency_hours": 6,
    "min_match_for_approval": 0.70,
    "auto_approve_above_score": 0.90,
    "learning_aggressiveness": "moderate"
  }
```

#### **applications** table - Add these fields:
```sql
- agent_reasoning (Text) - Why agent recommended this job
- match_reasoning (JSONB) - Detailed scoring breakdown
  {
    "title_score": 0.9,
    "keyword_score": 0.85,
    "location_score": 1.0,
    "salary_score": 0.8,
    "total_score": 0.88,
    "reasons": ["Strong Python match", "Good salary range"]
  }
- applied_by_agent (Boolean) - True if agent submitted, False if manual
- approval_request_id (FK) - Links to approval_requests table (nullable)
```

#### **resumes** table - Add these fields:
```sql
- performance_score (Float) - Overall success rate with this resume
- response_rate (Float) - % of applications that got responses
- interview_rate (Float) - % that led to interviews
- last_performance_update (DateTime) - When stats were last calculated
- agent_recommendations (JSONB) - What agents suggest improving
  {
    "add_keywords": ["FastAPI", "Docker"],
    "reduce_length": false,
    "format_suggestion": "more bullet points"
  }
```

#### **jobs** table - Add these fields:
```sql
- agent_evaluated (Boolean) - Whether agent has processed this job
- agent_recommendation (String) - apply/skip/needs_review
- match_reasoning (JSONB) - Same as in applications table
- scraped_by_agent (Boolean) - True if agent scraped, False if manual
```

---

## 📊 Summary: Required Changes

### MUST ADD (4 new tables):
1. ✅ **approval_requests** - Email approval workflow
2. ✅ **agent_learning** - Agent improvement tracking
3. ✅ **feedback_loop** - Outcome analysis
4. ✅ **agent_memory** - Vector store metadata

### SHOULD ADD (field enhancements):
- **users** table: 5 new fields for agent control
- **applications** table: 3 new fields for agent context
- **resumes** table: 5 new fields for performance tracking
- **jobs** table: 4 new fields for agent processing

---

## 🚨 Data Type Issues in Current Schema

### Problems to Fix:

#### 1. **Integer fields stored as Strings** ❌
**Issue:** Statistics stored as strings instead of integers
- `users.total_applications` → Should be Integer
- `users.total_responses` → Should be Integer
- `users.total_interviews` → Should be Integer
- `users.total_offers` → Should be Integer
- `users.min_salary` → Should be Integer
- `users.max_salary` → Should be Integer
- `users.max_applications_per_day` → Should be Integer
- `users.min_match_score` → Should be Float
- `users.min_experience_years` → Should be Integer
- `users.max_experience_years` → Should be Integer
- `users.failed_login_attempts` → Should be Integer
- `resumes.usage_count` → Should be Integer
- `resumes.views` → Should be Integer
- `resumes.downloads` → Should be Integer
- `resumes.last_used_at` → Should be DateTime

**Fix:** Migration to convert string fields to proper numeric types

#### 2. **JSON stored as Text** ⚠️
**Current:** JSON arrays/objects stored as Text
- `users.target_titles`, `target_locations`, `keywords`, etc.
- `jobs.benefits`, `skills_required`

**Better:** Use PostgreSQL JSONB type
- Native JSON querying
- Better performance
- Validation

**Fix:** Migration to convert Text → JSONB

---

## 🎯 Recommended Migration Plan

### Migration 1: Add New Agent Tables
```sql
CREATE TABLE approval_requests (...);
CREATE TABLE agent_learning (...);
CREATE TABLE feedback_loop (...);
CREATE TABLE agent_memory (...);
```

### Migration 2: Add Fields to Existing Tables
```sql
ALTER TABLE users ADD COLUMN agent_status VARCHAR(20) DEFAULT 'active';
ALTER TABLE users ADD COLUMN agent_preferences JSONB;
-- etc...
```

### Migration 3: Fix Data Types (Breaking Change)
```sql
-- Create new columns with correct types
ALTER TABLE users ADD COLUMN total_applications_new INTEGER DEFAULT 0;

-- Copy and convert data
UPDATE users SET total_applications_new = CAST(total_applications AS INTEGER);

-- Drop old column and rename
ALTER TABLE users DROP COLUMN total_applications;
ALTER TABLE users RENAME COLUMN total_applications_new TO total_applications;
```

### Migration 4: Convert Text to JSONB
```sql
ALTER TABLE users ADD COLUMN target_titles_new JSONB;
UPDATE users SET target_titles_new = target_titles::JSONB;
ALTER TABLE users DROP COLUMN target_titles;
ALTER TABLE users RENAME COLUMN target_titles_new TO target_titles;
```

---

## ✅ What's Already Perfect

### Current schema has excellent foundation:
1. ✅ **UUID primary keys** - Good for distributed systems
2. ✅ **Timestamps on all tables** - Automatic created_at/updated_at
3. ✅ **Proper indexes** - Composite indexes for performance
4. ✅ **Enums for status fields** - Type-safe status tracking
5. ✅ **Foreign key relationships** - Proper CASCADE behaviors
6. ✅ **Unique constraints** - Prevent duplicate jobs/users
7. ✅ **Good separation** - Users, Jobs, Applications, Resumes are distinct

---

## 🚀 Implementation Priority

### Priority 1 (Critical for Agent System):
1. Add **approval_requests** table
2. Add **agent_learning** table
3. Add **feedback_loop** table
4. Add agent fields to **users** table

### Priority 2 (Important for Production):
1. Add **agent_memory** table
2. Add agent fields to **applications** table
3. Add performance fields to **resumes** table
4. Add agent fields to **jobs** table

### Priority 3 (Technical Debt - Can do later):
1. Fix data types (String → Integer/Float)
2. Convert Text → JSONB for JSON fields
3. Add validation constraints

---

## 📝 Recommendation

### Immediate Action:
**Create 4 new tables and add critical agent fields**

### Phased Approach:
**Don't fix data types immediately** - Current system works, agents can parse strings. Fix during major version upgrade.

### Why This Works:
1. ✅ Minimal breaking changes to existing code
2. ✅ Agents can start working immediately
3. ✅ Data type fixes can wait (non-critical)
4. ✅ Backward compatible

---

## Next Steps

1. **Review this analysis** - Confirm what to add/change
2. **Create Alembic migration** - Add 4 new tables + new fields
3. **Build agent system** - Agents will use new tables
4. **Test thoroughly** - Ensure everything works
5. **Plan data type fixes** - Schedule for v2.0

**Should I proceed with creating the migration scripts?** 🚀
