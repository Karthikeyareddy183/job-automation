"""
Resume Tailor Agent - Groq-powered resume customization
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResponse
from .state import JobApplicationState, add_agent_decision, add_error, update_metrics
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ResumeTailorAgent(BaseAgent):
    """
    Resume Tailor Agent - Customizes resume for each job using LLM

    Responsibilities:
    - Tailor resume to match job description
    - Highlight relevant skills and experience
    - Adjust keywords for ATS optimization
    - Maintain authenticity (no false claims)
    - Track which resume versions perform best
    """

    def __init__(self):
        super().__init__(
            name="ResumeTailor",
            model="llama-3.1-70b-versatile",  # Use larger model for better quality
            temperature=0.4  # Balance creativity and consistency
        )

    async def execute(self, state: JobApplicationState) -> Dict[str, Any]:
        """
        Execute resume tailoring logic

        Args:
            state: Current workflow state

        Returns:
            Updated state with tailored_resume
        """
        try:
            self.log("Starting resume tailoring...")

            # Get current job being processed
            current_job = state.get("current_job")
            if not current_job:
                self.log("No current job to tailor for", "warning")
                state["current_step"] = "approve"
                return state

            # Get base resume
            base_resume = state.get("base_resume")
            if not base_resume:
                self.log("No base resume found", "error")
                add_error(state, "No base resume available for tailoring")
                state["current_step"] = "match"  # Skip to next job
                return state

            # Get user preferences for additional context
            user_preferences = state.get("user_preferences", {})

            # Tailor resume
            tailored_resume, changes, reasoning = await self._tailor_resume(
                base_resume=base_resume,
                job=current_job,
                user_preferences=user_preferences
            )

            # Update state
            state["tailored_resume"] = tailored_resume
            state["resume_changes"] = changes
            state["tailoring_reasoning"] = reasoning
            state["current_step"] = "approve"

            # Add decision
            add_agent_decision(
                state,
                agent="resume_tailor",
                decision=f"tailored_resume_for_{current_job.get('id')}",
                reasoning=reasoning,
                success=True
            )

            # Update metrics
            update_metrics(state, "resumes_tailored", state.get("metrics", {}).get("resumes_tailored", 0) + 1)

            self.log(f"Successfully tailored resume for {current_job.get('title')} at {current_job.get('company')}")
            return state

        except Exception as e:
            self.log(f"Resume tailoring failed: {e}", "error")
            add_error(state, f"Resume tailor error: {e}")
            state["current_step"] = "match"  # Skip to next job
            return state

    async def _tailor_resume(
        self,
        base_resume: str,
        job: Dict,
        user_preferences: Dict
    ) -> tuple[str, List[str], str]:
        """
        Tailor resume for specific job using LLM

        Args:
            base_resume: User's base resume content
            job: Job dictionary
            user_preferences: User preferences

        Returns:
            Tuple of (tailored_resume, list_of_changes, reasoning)
        """
        try:
            # Build prompt
            prompt = self._build_tailoring_prompt(base_resume, job, user_preferences)

            # Invoke LLM
            response = await self.invoke_llm(prompt)

            # Parse response
            tailored_resume, changes, reasoning = self._parse_tailoring_response(response)

            return tailored_resume, changes, reasoning

        except Exception as e:
            self.log(f"Resume tailoring failed: {e}", "error")
            # Return original resume on failure
            return base_resume, [], f"Error: {e}"

    def _build_tailoring_prompt(self, base_resume: str, job: Dict, user_preferences: Dict) -> str:
        """
        Build prompt for LLM resume tailoring

        Args:
            base_resume: User's base resume
            job: Job dictionary
            user_preferences: User preferences

        Returns:
            Prompt string
        """
        job_title = job.get("title", "")
        job_company = job.get("company", "")
        job_description = job.get("description", "")
        job_requirements = self._extract_requirements(job_description)

        prompt = f"""
You are an expert resume writer and career coach. Your task is to tailor a resume for a specific job posting.

JOB POSTING:
Title: {job_title}
Company: {job_company}
Description: {job_description}

KEY REQUIREMENTS:
{job_requirements}

ORIGINAL RESUME:
{base_resume}

TASK:
Customize this resume to maximize the chance of getting an interview for this job. Follow these rules:

1. AUTHENTICITY: Only highlight existing skills and experience. NEVER add false information.
2. RELEVANCE: Emphasize experiences most relevant to this job.
3. KEYWORDS: Incorporate keywords from the job description naturally.
4. ATS OPTIMIZATION: Use terminology that matches the job posting.
5. IMPACT: Quantify achievements where possible.
6. CONCISENESS: Keep it to 1-2 pages.

SPECIFIC CHANGES TO MAKE:
- Adjust the professional summary/objective to align with this role
- Reorder or emphasize relevant skills
- Highlight projects/experiences that match job requirements
- Use similar language and keywords from job description
- Ensure technical skills mentioned in job posting are visible (if user has them)

IMPORTANT: Respond in this exact format:

TAILORED_RESUME:
[Full tailored resume content here]

CHANGES_MADE:
- [Change 1]
- [Change 2]
- [Change 3]
...

REASONING:
[Explanation of why these changes improve the match]
"""

        return prompt

    def _extract_requirements(self, job_description: str) -> str:
        """
        Extract key requirements from job description

        Args:
            job_description: Job description text

        Returns:
            Formatted requirements string
        """
        # Simple extraction - look for common patterns
        requirements = []

        # Split into lines
        lines = job_description.split("\n")

        for line in lines:
            line_lower = line.lower().strip()
            # Look for requirement indicators
            if any(keyword in line_lower for keyword in ["required", "must have", "experience with", "proficient in", "years of"]):
                requirements.append(line.strip())

        if requirements:
            return "\n".join(requirements)
        else:
            # If no clear requirements found, return first 300 chars
            return job_description[:300] + "..."

    def _parse_tailoring_response(self, response: str) -> tuple[str, List[str], str]:
        """
        Parse LLM response to extract tailored resume, changes, and reasoning

        Args:
            response: LLM response text

        Returns:
            Tuple of (tailored_resume, changes_list, reasoning)
        """
        try:
            # Extract tailored resume
            tailored_resume = ""
            if "TAILORED_RESUME:" in response:
                resume_section = response.split("TAILORED_RESUME:")[1]
                if "CHANGES_MADE:" in resume_section:
                    tailored_resume = resume_section.split("CHANGES_MADE:")[0].strip()
                else:
                    tailored_resume = resume_section.strip()

            # Extract changes
            changes = []
            if "CHANGES_MADE:" in response:
                changes_section = response.split("CHANGES_MADE:")[1]
                if "REASONING:" in changes_section:
                    changes_text = changes_section.split("REASONING:")[0].strip()
                else:
                    changes_text = changes_section.strip()

                # Parse bullet points
                for line in changes_text.split("\n"):
                    line = line.strip()
                    if line.startswith("-") or line.startswith("•"):
                        changes.append(line[1:].strip())

            # Extract reasoning
            reasoning = ""
            if "REASONING:" in response:
                reasoning = response.split("REASONING:")[1].strip()

            if not tailored_resume:
                self.log("Failed to extract tailored resume from LLM response", "warning")
                tailored_resume = response  # Use full response as fallback

            if not reasoning:
                reasoning = "Resume tailored to match job requirements"

            return tailored_resume, changes, reasoning

        except Exception as e:
            self.log(f"Failed to parse tailoring response: {e}", "error")
            return response, [], f"Parse error: {e}"

    async def _optimize_for_ats(self, resume: str, job_description: str) -> str:
        """
        Optimize resume for Applicant Tracking Systems (ATS)

        Args:
            resume: Resume content
            job_description: Job description

        Returns:
            ATS-optimized resume
        """
        try:
            # Extract keywords from job description
            keywords = self._extract_keywords(job_description)

            prompt = f"""
You are an ATS (Applicant Tracking System) optimization expert.

RESUME:
{resume}

JOB KEYWORDS TO INCORPORATE:
{', '.join(keywords)}

TASK:
Optimize this resume for ATS scanning by:
1. Incorporating relevant keywords naturally
2. Using standard section headers (Experience, Education, Skills)
3. Avoiding tables, graphics, or complex formatting
4. Using standard fonts and bullet points
5. Including relevant technical terms

Return the ATS-optimized resume.
"""

            optimized = await self.invoke_llm(prompt)
            return optimized

        except Exception as e:
            self.log(f"ATS optimization failed: {e}", "error")
            return resume

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from text

        Args:
            text: Text to extract from

        Returns:
            List of keywords
        """
        # Simple keyword extraction
        # TODO: Improve with NLP techniques

        common_tech_terms = [
            "python", "javascript", "react", "node", "django", "flask",
            "sql", "postgresql", "mongodb", "aws", "docker", "kubernetes",
            "machine learning", "api", "rest", "graphql", "typescript",
            "git", "agile", "scrum", "ci/cd", "testing", "backend", "frontend"
        ]

        text_lower = text.lower()
        found_keywords = []

        for term in common_tech_terms:
            if term in text_lower:
                found_keywords.append(term)

        return found_keywords[:15]  # Limit to top 15

    async def _learn_from_resume_performance(self, state: JobApplicationState):
        """
        Learn which resume customizations lead to best outcomes

        Args:
            state: Current workflow state
        """
        try:
            # TODO: Implement learning logic
            # - Which types of changes lead to approvals/responses?
            # - Which keywords are most effective?
            # - Optimal resume length?
            # - Best formatting strategies?

            tailored_resume = state.get("tailored_resume", "")
            changes = state.get("resume_changes", [])

            insights = {
                "resume_length": len(tailored_resume),
                "changes_count": len(changes),
                "changes_made": changes
            }

            if "learning_insights" not in state:
                state["learning_insights"] = {}

            state["learning_insights"]["resume_tailor"] = insights

        except Exception as e:
            self.log(f"Learning from resume performance failed: {e}", "error")
