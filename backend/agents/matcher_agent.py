"""
Matcher Agent - LLM-powered job matching with reasoning
"""
from typing import Dict, Any, List, Tuple
from .base_agent import BaseAgent, AgentResponse
from .state import JobApplicationState, add_agent_decision, add_error, update_metrics
from datetime import datetime
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class MatcherAgent(BaseAgent):
    """
    Matcher Agent - Intelligently matches jobs to user profile using LLM

    Responsibilities:
    - Evaluate job fit using LLM reasoning
    - Calculate match scores (0.0 - 1.0)
    - Filter jobs below threshold
    - Provide detailed reasoning for decisions
    - Learn from successful vs rejected matches
    """

    def __init__(self):
        super().__init__(
            name="Matcher",
            model="llama-3.1-8b-instant",
            temperature=0.3
        )
        self.min_score_threshold = settings.MIN_MATCH_SCORE_THRESHOLD

    async def execute(self, state: JobApplicationState) -> Dict[str, Any]:
        """
        Execute matching logic

        Args:
            state: Current workflow state

        Returns:
            Updated state with matched_jobs
        """
        try:
            self.log("Starting job matching...")

            scraped_jobs = state.get("scraped_jobs", [])
            user_preferences = state.get("user_preferences", {})

            if not scraped_jobs:
                self.log("No jobs to match", "warning")
                state["current_step"] = "learn"
                return state

            # Match each job
            matched_jobs = []
            matching_scores = {}
            matching_reasoning = {}

            for job in scraped_jobs:
                job_id = job.get("id")

                # Calculate match score with LLM reasoning
                score, reasoning = await self._calculate_match_score(job, user_preferences)

                matching_scores[job_id] = score
                matching_reasoning[job_id] = reasoning

                # Filter by threshold
                if score >= self.min_score_threshold:
                    matched_jobs.append(job)
                    self.log(f"✓ Matched: {job.get('title')} at {job.get('company')} (score: {score:.2f})")
                else:
                    self.log(f"✗ Rejected: {job.get('title')} at {job.get('company')} (score: {score:.2f})")

            # Sort by score (highest first)
            matched_jobs.sort(key=lambda j: matching_scores[j.get("id")], reverse=True)

            # Update state
            state["matched_jobs"] = matched_jobs
            state["matching_scores"] = matching_scores
            state["matching_reasoning"] = matching_reasoning
            state["current_step"] = "tailor"

            # Add decision
            add_agent_decision(
                state,
                agent="matcher",
                decision=f"matched_{len(matched_jobs)}_of_{len(scraped_jobs)}_jobs",
                reasoning=f"Filtered jobs with score >= {self.min_score_threshold}",
                success=True
            )

            # Update metrics
            update_metrics(state, "jobs_matched", len(matched_jobs))
            update_metrics(state, "match_rate", len(matched_jobs) / len(scraped_jobs) if scraped_jobs else 0)

            self.log(f"Matched {len(matched_jobs)} of {len(scraped_jobs)} jobs")
            return state

        except Exception as e:
            self.log(f"Matching failed: {e}", "error")
            add_error(state, f"Matcher error: {e}")
            state["current_step"] = "learn"
            return state

    async def _calculate_match_score(self, job: Dict, user_preferences: Dict) -> Tuple[float, str]:
        """
        Calculate match score using LLM reasoning

        Args:
            job: Job dictionary
            user_preferences: User preferences

        Returns:
            Tuple of (score, reasoning)
        """
        try:
            # Build prompt for LLM
            prompt = self._build_matching_prompt(job, user_preferences)

            # Invoke LLM
            response = await self.invoke_llm(prompt)

            # Parse response
            score, reasoning = self._parse_llm_response(response)

            return score, reasoning

        except Exception as e:
            self.log(f"Match calculation failed: {e}", "error")
            return 0.0, f"Error: {e}"

    def _build_matching_prompt(self, job: Dict, user_preferences: Dict) -> str:
        """
        Build prompt for LLM job matching

        Args:
            job: Job dictionary
            user_preferences: User preferences

        Returns:
            Prompt string
        """
        # Extract user preferences
        desired_keywords = user_preferences.get("keywords", [])
        desired_salary_min = user_preferences.get("salary_min", 0)
        desired_location = user_preferences.get("location", "")
        experience_level = user_preferences.get("experience_level", "")
        desired_job_type = user_preferences.get("job_type", "")
        skills = user_preferences.get("skills", [])

        # Extract job details
        job_title = job.get("title", "")
        job_company = job.get("company", "")
        job_description = job.get("description", "")
        job_location = job.get("location", "")
        job_salary = job.get("salary_range", "")
        job_type = job.get("job_type", "")

        prompt = f"""
You are an expert job matcher. Evaluate how well this job matches the user's preferences.

USER PREFERENCES:
- Desired Keywords: {', '.join(desired_keywords) if desired_keywords else 'Not specified'}
- Minimum Salary: ${desired_salary_min:,} if desired_salary_min else 'Not specified'
- Preferred Location: {desired_location or 'Not specified'}
- Experience Level: {experience_level or 'Not specified'}
- Job Type: {desired_job_type or 'Not specified'}
- Skills: {', '.join(skills) if skills else 'Not specified'}

JOB POSTING:
Title: {job_title}
Company: {job_company}
Location: {job_location}
Salary: {job_salary}
Job Type: {job_type}
Description: {job_description[:500]}...

TASK:
Analyze the job posting and provide:
1. A match score from 0.0 to 1.0 (where 1.0 is perfect match)
2. Detailed reasoning for your score

Consider:
- Keyword alignment (title, description)
- Salary fit
- Location match
- Experience level fit
- Job type match
- Skills alignment
- Red flags (unrealistic requirements, vague descriptions)

IMPORTANT: Respond in this exact format:
SCORE: [number between 0.0 and 1.0]
REASONING: [Your detailed reasoning here]

Example:
SCORE: 0.85
REASONING: Strong match. Job title aligns with desired keywords (Python, Django). Salary range ($100k-$130k) meets minimum requirement. Location is remote as preferred. Description mentions 3+ years experience matching user's mid-level preference. Minor concern: requires AWS which user hasn't mentioned.
"""

        return prompt

    def _parse_llm_response(self, response: str) -> Tuple[float, str]:
        """
        Parse LLM response to extract score and reasoning

        Args:
            response: LLM response text

        Returns:
            Tuple of (score, reasoning)
        """
        try:
            # Extract score
            score_line = [line for line in response.split("\n") if line.strip().startswith("SCORE:")][0]
            score_str = score_line.replace("SCORE:", "").strip()
            score = float(score_str)

            # Clamp score to 0.0 - 1.0
            score = max(0.0, min(1.0, score))

            # Extract reasoning
            reasoning_lines = []
            found_reasoning = False
            for line in response.split("\n"):
                if line.strip().startswith("REASONING:"):
                    found_reasoning = True
                    reasoning_lines.append(line.replace("REASONING:", "").strip())
                elif found_reasoning:
                    reasoning_lines.append(line.strip())

            reasoning = " ".join(reasoning_lines).strip()

            if not reasoning:
                reasoning = "LLM provided no reasoning"

            return score, reasoning

        except Exception as e:
            self.log(f"Failed to parse LLM response: {e}", "error")
            # Fallback: Try to extract any number
            import re
            numbers = re.findall(r"0?\.\d+|1\.0", response)
            if numbers:
                score = float(numbers[0])
                return score, response[:200]
            else:
                return 0.0, f"Parse error: {e}"

    async def _learn_from_matches(self, state: JobApplicationState):
        """
        Learn from matching results to improve future matches

        Args:
            state: Current workflow state
        """
        try:
            # TODO: Implement learning logic
            # - Which keywords lead to best matches?
            # - Are we being too strict/lenient with threshold?
            # - Which job characteristics correlate with user approval?

            matching_scores = state.get("matching_scores", {})

            if not matching_scores:
                return

            # Calculate statistics
            scores = list(matching_scores.values())
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)

            insights = {
                "avg_match_score": avg_score,
                "max_match_score": max_score,
                "min_match_score": min_score,
                "total_evaluated": len(scores),
                "matched_count": len([s for s in scores if s >= self.min_score_threshold])
            }

            if "learning_insights" not in state:
                state["learning_insights"] = {}

            state["learning_insights"]["matcher"] = insights

            self.log(f"Match statistics: avg={avg_score:.2f}, max={max_score:.2f}, min={min_score:.2f}")

        except Exception as e:
            self.log(f"Learning from matches failed: {e}", "error")

    async def adjust_threshold(self, state: JobApplicationState):
        """
        Dynamically adjust match threshold based on results

        Args:
            state: Current workflow state
        """
        try:
            # TODO: Implement dynamic threshold adjustment
            # - If too few matches: lower threshold
            # - If too many low-quality matches: raise threshold
            # - Learn from user approval/rejection patterns

            matched_count = len(state.get("matched_jobs", []))

            if matched_count == 0:
                # Too strict, lower threshold
                self.min_score_threshold = max(0.5, self.min_score_threshold - 0.05)
                self.log(f"Lowered threshold to {self.min_score_threshold:.2f}")
            elif matched_count > 20:
                # Too lenient, raise threshold
                self.min_score_threshold = min(0.9, self.min_score_threshold + 0.05)
                self.log(f"Raised threshold to {self.min_score_threshold:.2f}")

        except Exception as e:
            self.log(f"Threshold adjustment failed: {e}", "error")
