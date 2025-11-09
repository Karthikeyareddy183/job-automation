"""
Test script for agent workflow

Run this to test the complete agent workflow without API keys.
This script will use mock data to demonstrate the flow.
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.workflow import JobApplicationWorkflow
from agents.state import create_initial_state


async def test_workflow():
    """Test the complete agent workflow"""

    print("=" * 80)
    print("🤖 JOB APPLICATION AGENT WORKFLOW TEST")
    print("=" * 80)
    print()

    # Create test user preferences
    user_preferences = {
        "keywords": ["Python", "Django", "FastAPI"],
        "location": "Remote",
        "job_type": "Full-time",
        "experience_level": "Mid-level",
        "salary_min": 80000,
        "skills": ["Python", "React", "PostgreSQL", "Docker"],
    }

    # Mock base resume
    base_resume = """
JOHN DOE
Software Engineer

EXPERIENCE:
- Senior Python Developer at TechCorp (2021-2024)
  * Built REST APIs using Django and FastAPI
  * Managed PostgreSQL databases
  * Deployed applications with Docker
  * Led team of 3 developers

- Python Developer at StartupXYZ (2019-2021)
  * Developed web applications with Django
  * Implemented React frontends
  * Worked in Agile environment

SKILLS:
Python, Django, FastAPI, React, PostgreSQL, Docker, Git, AWS

EDUCATION:
BS Computer Science, State University (2019)
"""

    print("📋 USER PREFERENCES:")
    print(f"  Keywords: {user_preferences['keywords']}")
    print(f"  Location: {user_preferences['location']}")
    print(f"  Job Type: {user_preferences['job_type']}")
    print(f"  Min Salary: ${user_preferences['salary_min']:,}")
    print()

    # Create workflow
    workflow = JobApplicationWorkflow()

    # Create initial state
    state = create_initial_state(
        user_id="test-user-123",
        user_preferences=user_preferences
    )
    state["base_resume"] = base_resume

    print("🚀 Starting workflow...")
    print()

    # Run workflow
    try:
        final_state = await workflow.run(
            user_id="test-user-123",
            user_preferences=user_preferences
        )

        # Print results
        print()
        print("=" * 80)
        print("✅ WORKFLOW COMPLETED")
        print("=" * 80)
        print()

        # Scraping results
        scraped_jobs = final_state.get("scraped_jobs", [])
        print(f"📥 SCRAPED JOBS: {len(scraped_jobs)}")
        for i, job in enumerate(scraped_jobs[:3], 1):
            print(f"  {i}. {job.get('title')} at {job.get('company')}")
        print()

        # Matching results
        matched_jobs = final_state.get("matched_jobs", [])
        matching_scores = final_state.get("matching_scores", {})
        print(f"🎯 MATCHED JOBS: {len(matched_jobs)}")
        for i, job in enumerate(matched_jobs[:3], 1):
            job_id = job.get("id")
            score = matching_scores.get(job_id, 0.0)
            print(f"  {i}. {job.get('title')} at {job.get('company')} (score: {score:.2f})")
        print()

        # Resume tailoring
        tailored_resume = final_state.get("tailored_resume")
        resume_changes = final_state.get("resume_changes", [])
        if tailored_resume:
            print("📄 RESUME TAILORED:")
            print(f"  Changes made: {len(resume_changes)}")
            for i, change in enumerate(resume_changes[:3], 1):
                print(f"    {i}. {change}")
        print()

        # Agent decisions
        agent_decisions = final_state.get("agent_decisions", [])
        print(f"🤖 AGENT DECISIONS: {len(agent_decisions)}")
        for decision in agent_decisions[:5]:
            agent = decision.get("agent")
            action = decision.get("decision")
            print(f"  [{agent}] {action}")
        print()

        # Errors
        errors = final_state.get("errors", [])
        if errors:
            print(f"⚠️  ERRORS: {len(errors)}")
            for error in errors[:3]:
                print(f"  - {error.get('error', 'Unknown error')}")
        else:
            print("✅ No errors!")
        print()

        # Learning insights
        learning_insights = final_state.get("learning_insights", {})
        if learning_insights:
            print("📊 LEARNING INSIGHTS:")
            workflow_analysis = learning_insights.get("workflow_analysis", {})
            if workflow_analysis:
                print(f"  Match rate: {workflow_analysis.get('match_rate', 0):.1%}")
                print(f"  Duration: {workflow_analysis.get('workflow_duration', 0):.1f}s")
                recommendations = workflow_analysis.get("recommendations", [])
                if recommendations:
                    print("  Recommendations:")
                    for rec in recommendations:
                        print(f"    - {rec}")
        print()

        # Strategy adjustments
        strategy_adjustments = final_state.get("strategy_adjustments", {})
        if strategy_adjustments:
            print("⚙️  STRATEGY ADJUSTMENTS:")
            for agent, adjustments in strategy_adjustments.items():
                if adjustments and agent != "timestamp":
                    print(f"  [{agent}]")
                    action = adjustments.get("action")
                    reasoning = adjustments.get("reasoning")
                    if action:
                        print(f"    Action: {action}")
                        print(f"    Reason: {reasoning}")
        print()

        print("=" * 80)
        print()

        # Next steps
        next_action = final_state.get("next_action")
        if next_action == "wait":
            print("⏳ NEXT STEP: Waiting for user approval via email")
        elif next_action == "stop":
            print("🏁 WORKFLOW COMPLETE")
        else:
            print(f"➡️  NEXT STEP: {next_action}")

        print()
        print("💡 NOTE: This is a test run with mock data.")
        print("   To use real scraping, add your Groq API key to .env")
        print()

        return final_state

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ WORKFLOW FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        return None


async def test_individual_agents():
    """Test individual agents"""

    print("=" * 80)
    print("🧪 TESTING INDIVIDUAL AGENTS")
    print("=" * 80)
    print()

    from agents.scraper_agent import ScraperAgent
    from agents.matcher_agent import MatcherAgent
    from agents.resume_tailor_agent import ResumeTailorAgent
    from agents.learning_agent import LearningAgent

    # Test state
    state = create_initial_state(
        user_id="test-user",
        user_preferences={
            "keywords": ["Python"],
            "location": "Remote",
            "salary_min": 80000
        }
    )

    # Test scraper
    print("1. Testing Scraper Agent...")
    scraper = ScraperAgent()
    state = await scraper.execute(state)
    print(f"   ✓ Scraped {len(state.get('scraped_jobs', []))} jobs")
    print()

    # Test matcher
    print("2. Testing Matcher Agent...")
    matcher = MatcherAgent()
    state = await matcher.execute(state)
    print(f"   ✓ Matched {len(state.get('matched_jobs', []))} jobs")
    print()

    # Test resume tailor (need a job and resume)
    print("3. Testing Resume Tailor Agent...")
    matched_jobs = state.get("matched_jobs", [])
    if matched_jobs:
        state["current_job"] = matched_jobs[0]
        state["base_resume"] = "Sample resume content..."

        tailor = ResumeTailorAgent()
        state = await tailor.execute(state)
        if state.get("tailored_resume"):
            print(f"   ✓ Resume tailored")
        else:
            print(f"   ⚠ Resume tailoring skipped (no Groq API key)")
    print()

    # Test learning
    print("4. Testing Learning Agent...")
    learning = LearningAgent()
    state = await learning.execute(state)
    print(f"   ✓ Learning analysis complete")
    print()

    print("=" * 80)
    print()


async def main():
    """Main test runner"""

    print()
    print("Choose test mode:")
    print("1. Full workflow test (recommended)")
    print("2. Individual agent tests")
    print("3. Both")
    print()

    choice = input("Enter choice (1-3, or press Enter for full workflow): ").strip()

    if not choice:
        choice = "1"

    print()

    if choice in ["1", "3"]:
        await test_workflow()

    if choice in ["2", "3"]:
        print()
        await test_individual_agents()

    print("✅ All tests complete!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
