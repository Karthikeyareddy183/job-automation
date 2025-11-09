"""
Supervisor Agent - Master orchestrator for job application workflow
"""
from typing import Dict, Any
from .base_agent import BaseAgent, AgentResponse
from .state import JobApplicationState, add_agent_decision, add_error
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent - Orchestrates the entire job application workflow

    Responsibilities:
    - Decide which agent to invoke next
    - Monitor overall workflow health
    - Handle errors and recovery
    - Coordinate between agents
    - Manage workflow state transitions
    """

    def __init__(self):
        super().__init__(
            name="Supervisor",
            model="llama-3.1-8b-instant",
            temperature=0.1  # Low temperature for consistent decisions
        )

    async def execute(self, state: JobApplicationState) -> Dict[str, Any]:
        """
        Execute supervisor logic - decide next step in workflow

        Args:
            state: Current workflow state

        Returns:
            Updated state with next_action set
        """
        try:
            self.log(f"Evaluating workflow at step: {state.get('current_step')}")

            # Get current step
            current_step = state.get("current_step", "scrape")

            # Decision logic based on current step
            if current_step == "scrape":
                next_action = await self._decide_after_scrape(state)
            elif current_step == "match":
                next_action = await self._decide_after_match(state)
            elif current_step == "tailor":
                next_action = await self._decide_after_tailor(state)
            elif current_step == "approve":
                next_action = await self._decide_after_approval(state)
            elif current_step == "apply":
                next_action = await self._decide_after_apply(state)
            elif current_step == "learn":
                next_action = await self._decide_after_learn(state)
            else:
                next_action = "scrape"  # Default to start

            # Update state
            state["next_action"] = next_action

            # Add decision to history
            add_agent_decision(
                state,
                agent="supervisor",
                decision=f"next_action={next_action}",
                reasoning=f"Based on current_step={current_step}",
                success=True
            )

            self.log(f"Next action: {next_action}")
            return state

        except Exception as e:
            self.log(f"Supervisor failed: {e}", "error")
            add_error(state, f"Supervisor error: {e}")
            state["next_action"] = "stop"
            return state

    async def _decide_after_scrape(self, state: JobApplicationState) -> str:
        """Decide what to do after scraping"""
        scraped_jobs = state.get("scraped_jobs", [])

        if len(scraped_jobs) == 0:
            self.log("No jobs scraped, stopping workflow")
            return "stop"

        self.log(f"Found {len(scraped_jobs)} jobs, proceeding to matching")
        return "match"

    async def _decide_after_match(self, state: JobApplicationState) -> str:
        """Decide what to do after matching"""
        matched_jobs = state.get("matched_jobs", [])

        if len(matched_jobs) == 0:
            self.log("No jobs matched, proceeding to learning")
            return "learn"

        # Get next job to process
        if not state.get("current_job"):
            # Pick first matched job
            state["current_job"] = matched_jobs[0]
            state["current_job_id"] = matched_jobs[0].get("id")

        self.log(f"Found {len(matched_jobs)} matched jobs, proceeding to tailoring")
        return "tailor"

    async def _decide_after_tailor(self, state: JobApplicationState) -> str:
        """Decide what to do after tailoring resume"""
        tailored_resume = state.get("tailored_resume")

        if not tailored_resume:
            self.log("Resume tailoring failed, skipping to next job")
            return "match"  # Try next job

        self.log("Resume tailored, proceeding to approval")
        return "approve"

    async def _decide_after_approval(self, state: JobApplicationState) -> str:
        """Decide what to do after approval request"""
        approval_status = state.get("approval_status")

        if approval_status == "approved":
            self.log("Application approved, proceeding to apply")
            return "apply"
        elif approval_status == "rejected":
            self.log("Application rejected, proceeding to learning")
            return "learn"
        elif approval_status == "expired":
            self.log("Approval expired, skipping application")
            return "match"  # Try next job
        else:
            # Still pending
            self.log("Approval pending, waiting...")
            return "wait"

    async def _decide_after_apply(self, state: JobApplicationState) -> str:
        """Decide what to do after application"""
        application_status = state.get("application_status")

        if application_status == "submitted":
            self.log("Application submitted successfully")
        else:
            self.log("Application failed")

        # Check if more jobs to process
        matched_jobs = state.get("matched_jobs", [])
        current_job_id = state.get("current_job_id")

        # Remove current job from matched list
        remaining_jobs = [j for j in matched_jobs if j.get("id") != current_job_id]
        state["matched_jobs"] = remaining_jobs
        state["current_job"] = None
        state["current_job_id"] = None

        if len(remaining_jobs) > 0:
            self.log(f"{len(remaining_jobs)} jobs remaining, continuing")
            return "match"
        else:
            self.log("All jobs processed, proceeding to learning")
            return "learn"

    async def _decide_after_learn(self, state: JobApplicationState) -> str:
        """Decide what to do after learning"""
        self.log("Learning complete, workflow finished")
        return "stop"

    async def should_continue_workflow(self, state: JobApplicationState) -> bool:
        """
        Check if workflow should continue

        Args:
            state: Current workflow state

        Returns:
            True if should continue, False otherwise
        """
        # Check for critical errors
        errors = state.get("errors", [])
        if len(errors) > 10:
            self.log("Too many errors, stopping workflow", "error")
            return False

        # Check user preferences
        user_preferences = state.get("user_preferences", {})
        if user_preferences.get("agent_status") == "paused":
            self.log("User paused agents, stopping workflow")
            return False

        # Check daily application limit
        # TODO: Implement daily limit check from database

        return True

    async def get_workflow_summary(self, state: JobApplicationState) -> Dict[str, Any]:
        """
        Get summary of workflow execution

        Args:
            state: Current workflow state

        Returns:
            Summary dictionary
        """
        return {
            "user_id": state.get("user_id"),
            "workflow_start_time": state.get("workflow_start_time"),
            "current_step": state.get("current_step"),
            "scraped_jobs_count": len(state.get("scraped_jobs", [])),
            "matched_jobs_count": len(state.get("matched_jobs", [])),
            "errors_count": len(state.get("errors", [])),
            "decisions_count": len(state.get("agent_decisions", [])),
            "next_action": state.get("next_action")
        }
