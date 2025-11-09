"""
Agents package - AI agents for job automation
"""
from .base_agent import BaseAgent, AgentResponse
from .supervisor_agent import SupervisorAgent
from .scraper_agent import ScraperAgent
from .matcher_agent import MatcherAgent
from .resume_tailor_agent import ResumeTailorAgent
from .learning_agent import LearningAgent
from .state import (
    JobApplicationState,
    AgentMessage,
    create_initial_state,
    add_agent_decision,
    add_error,
    update_metrics
)
from .workflow import (
    JobApplicationWorkflow,
    run_job_application_workflow,
    resume_job_application_workflow,
    workflow_instance
)

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentResponse",

    # Agents
    "SupervisorAgent",
    "ScraperAgent",
    "MatcherAgent",
    "ResumeTailorAgent",
    "LearningAgent",

    # State
    "JobApplicationState",
    "AgentMessage",
    "create_initial_state",
    "add_agent_decision",
    "add_error",
    "update_metrics",

    # Workflow
    "JobApplicationWorkflow",
    "run_job_application_workflow",
    "resume_job_application_workflow",
    "workflow_instance",
]
