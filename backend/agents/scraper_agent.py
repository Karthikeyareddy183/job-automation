"""
Scraper Agent - Intelligent job scraping with LLM adaptation
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResponse
from .state import JobApplicationState, add_agent_decision, add_error, update_metrics
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class ScraperAgent(BaseAgent):
    """
    Scraper Agent - Intelligently scrapes job postings with LLM adaptation

    Responsibilities:
    - Scrape jobs from multiple platforms (Indeed, LinkedIn, Glassdoor)
    - Use LLM to adapt to site changes
    - Extract structured job data
    - Learn which sources yield best results
    - Adjust scraping strategy based on success rates
    """

    def __init__(self):
        super().__init__(
            name="Scraper",
            model="llama-3.1-8b-instant",
            temperature=0.2
        )

    async def execute(self, state: JobApplicationState) -> Dict[str, Any]:
        """
        Execute scraping logic

        Args:
            state: Current workflow state

        Returns:
            Updated state with scraped_jobs
        """
        try:
            self.log("Starting job scraping...")

            user_preferences = state.get("user_preferences", {})

            # Extract search parameters
            keywords = user_preferences.get("keywords", [])
            location = user_preferences.get("location", "")
            job_type = user_preferences.get("job_type", "")
            experience_level = user_preferences.get("experience_level", "")

            # Scrape from multiple sources
            all_jobs = []

            # Indeed scraping
            indeed_jobs = await self._scrape_indeed(keywords, location, job_type)
            all_jobs.extend(indeed_jobs)

            # LinkedIn scraping (TODO: Implement when ready)
            # linkedin_jobs = await self._scrape_linkedin(keywords, location)
            # all_jobs.extend(linkedin_jobs)

            # Update state
            state["scraped_jobs"] = all_jobs
            state["scraping_stats"] = {
                "total_scraped": len(all_jobs),
                "indeed_count": len(indeed_jobs),
                "linkedin_count": 0,
                "glassdoor_count": 0,
                "timestamp": datetime.utcnow()
            }
            state["current_step"] = "match"

            # Add decision
            add_agent_decision(
                state,
                agent="scraper",
                decision=f"scraped_{len(all_jobs)}_jobs",
                reasoning=f"Scraped from Indeed using keywords: {keywords}",
                success=True
            )

            # Update metrics
            update_metrics(state, "jobs_scraped", len(all_jobs))

            self.log(f"Successfully scraped {len(all_jobs)} jobs")
            return state

        except Exception as e:
            self.log(f"Scraping failed: {e}", "error")
            add_error(state, f"Scraper error: {e}")
            state["current_step"] = "match"  # Continue workflow
            return state

    async def _scrape_indeed(self, keywords: List[str], location: str, job_type: str) -> List[Dict]:
        """
        Scrape jobs from Indeed

        Args:
            keywords: Search keywords
            location: Job location
            job_type: Job type (full-time, part-time, etc.)

        Returns:
            List of job dictionaries
        """
        try:
            self.log(f"Scraping Indeed for: {keywords} in {location}")

            # TODO: Implement actual scraping with Playwright or ScrapingBee
            # For now, return mock data for testing

            mock_jobs = [
                {
                    "id": f"indeed_{i}",
                    "title": f"Software Engineer - {keywords[0] if keywords else 'Python'}",
                    "company": f"Tech Company {i}",
                    "location": location or "Remote",
                    "description": f"We are looking for a talented software engineer with experience in {keywords[0] if keywords else 'Python'}. Must have 3+ years of experience.",
                    "salary_range": "$80,000 - $120,000",
                    "job_type": job_type or "Full-time",
                    "posted_date": datetime.utcnow().isoformat(),
                    "url": f"https://www.indeed.com/viewjob?jk=mock{i}",
                    "source": "indeed",
                    "scraped_at": datetime.utcnow().isoformat()
                }
                for i in range(1, 6)  # Mock 5 jobs
            ]

            return mock_jobs

        except Exception as e:
            self.log(f"Indeed scraping failed: {e}", "error")
            return []

    async def _scrape_with_llm_adaptation(self, html_content: str, site_name: str) -> Dict:
        """
        Use LLM to extract job data from HTML when selectors fail

        Args:
            html_content: Raw HTML content
            site_name: Name of job site

        Returns:
            Extracted job data
        """
        try:
            # Create prompt for LLM
            prompt = f"""
You are a web scraping expert. Extract job posting data from the following HTML.

HTML Content (truncated):
{html_content[:2000]}

Extract the following fields if available:
- Job Title
- Company Name
- Location
- Job Description
- Salary Range
- Job Type (full-time, part-time, contract, etc.)
- Posted Date
- Application URL

Return ONLY valid JSON with these fields. If a field is not found, use null.

Example:
{{
    "title": "Software Engineer",
    "company": "Google",
    "location": "Mountain View, CA",
    "description": "...",
    "salary_range": "$120k - $180k",
    "job_type": "Full-time",
    "posted_date": "2025-01-15",
    "url": "https://..."
}}
"""

            # Invoke LLM
            response = await self.invoke_llm(prompt)

            # Parse JSON from response
            import json
            job_data = json.loads(response)

            self.log(f"LLM successfully extracted job data for {site_name}")
            return job_data

        except Exception as e:
            self.log(f"LLM extraction failed: {e}", "error")
            return {}

    async def _learn_from_scraping_results(self, state: JobApplicationState):
        """
        Analyze scraping results and adjust strategy

        Args:
            state: Current workflow state
        """
        try:
            # TODO: Implement learning logic
            # - Which sites have highest quality jobs?
            # - Which keywords yield best results?
            # - Optimal scraping frequency
            # - Site-specific patterns

            scraping_stats = state.get("scraping_stats", {})

            # Store insights
            insights = {
                "best_source": "indeed",  # Placeholder
                "recommended_keywords": [],  # Placeholder
                "scraping_quality_score": 0.8  # Placeholder
            }

            if "learning_insights" not in state:
                state["learning_insights"] = {}

            state["learning_insights"]["scraper"] = insights

        except Exception as e:
            self.log(f"Learning from scraping failed: {e}", "error")

    async def validate_job_posting(self, job: Dict) -> bool:
        """
        Validate that scraped job has required fields

        Args:
            job: Job dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["title", "company", "description", "url"]

        for field in required_fields:
            if not job.get(field):
                self.log(f"Job missing required field: {field}", "warning")
                return False

        return True

    async def deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Remove duplicate job postings

        Args:
            jobs: List of job dictionaries

        Returns:
            Deduplicated list
        """
        seen_urls = set()
        unique_jobs = []

        for job in jobs:
            url = job.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_jobs.append(job)

        removed_count = len(jobs) - len(unique_jobs)
        if removed_count > 0:
            self.log(f"Removed {removed_count} duplicate jobs")

        return unique_jobs
