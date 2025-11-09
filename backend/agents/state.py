"""
LangGraph State Definitions - Workflow state management
"""
from typing import TypedDict, List, Dict, Optional, Any
from datetime import datetime


class JobApplicationState(TypedDict, total=False):
    """
    State for job application workflow

    This state is passed between agents and tracks the entire workflow
    """

    # User Context
    user_id: str
    user_preferences: Dict[str, Any]  # Job preferences, keywords, salary, etc.

    # Workflow Status
    current_step: str  # scrape/match/tailor/approve/apply/learn
    workflow_start_time: datetime
    errors: List[str]  # Error messages

    # Scraping Results
    scraped_jobs: List[Dict]  # Raw scraped jobs
    scraping_stats: Dict  # Statistics from scraping

    # Matching Results
    matched_jobs: List[Dict]  # Jobs that passed matching
    matching_scores: Dict[str, float]  # job_id -> match_score
    matching_reasoning: Dict[str, str]  # job_id -> LLM reasoning

    # Current Job Being Processed
    current_job: Optional[Dict]  # Job currently being processed
    current_job_id: Optional[str]

    # Resume Tailoring
    base_resume: Optional[str]  # User's base resume
    tailored_resume: Optional[str]  # Tailored resume content
    resume_changes: Optional[List[str]]  # List of changes made
    tailoring_reasoning: Optional[str]  # Why changes were made

    # Approval Workflow
    approval_request_id: Optional[str]  # ID of approval request
    approval_status: Optional[str]  # pending/approved/rejected/expired
    approval_sent_at: Optional[datetime]
    user_feedback: Optional[str]  # User's feedback on rejection

    # Application Result
    application_id: Optional[str]  # Created application ID
    application_status: Optional[str]  # Status of application
    application_result: Optional[Dict]  # Result from application agent

    # Learning & Feedback
    learning_insights: Dict[str, Any]  # What agents learned
    strategy_adjustments: Dict[str, Any]  # How agents adjusted
    feedback_loop_id: Optional[str]  # ID of feedback loop entry

    # Agent Decisions
    agent_decisions: List[Dict]  # History of agent decisions
    # [{agent: "matcher", decision: "apply", reasoning: "...", timestamp: ...}]

    # Performance Metrics
    metrics: Dict[str, Any]  # Workflow performance metrics

    # Next Action
    next_action: Optional[str]  # What should happen next


class AgentMessage(TypedDict):
    """Message passed between agents"""
    agent: str  # Agent name
    action: str  # Action taken
    result: Any  # Result of action
    reasoning: str  # Why this action was taken
    success: bool  # Whether action succeeded
    timestamp: datetime
    metadata: Dict  # Additional metadata


def create_initial_state(user_id: str, user_preferences: Dict) -> JobApplicationState:
    """
    Create initial workflow state

    Args:
        user_id: User ID
        user_preferences: User job preferences

    Returns:
        Initial state
    """
    return JobApplicationState(
        user_id=user_id,
        user_preferences=user_preferences,
        current_step="scrape",
        workflow_start_time=datetime.utcnow(),
        errors=[],
        scraped_jobs=[],
        scraping_stats={},
        matched_jobs=[],
        matching_scores={},
        matching_reasoning={},
        current_job=None,
        current_job_id=None,
        base_resume=None,
        tailored_resume=None,
        resume_changes=None,
        tailoring_reasoning=None,
        approval_request_id=None,
        approval_status=None,
        approval_sent_at=None,
        user_feedback=None,
        application_id=None,
        application_status=None,
        application_result=None,
        learning_insights={},
        strategy_adjustments={},
        feedback_loop_id=None,
        agent_decisions=[],
        metrics={},
        next_action="scrape"
    )


def add_agent_decision(state: JobApplicationState, agent: str, decision: str, reasoning: str, success: bool = True):
    """Add agent decision to state history"""
    if "agent_decisions" not in state:
        state["agent_decisions"] = []

    state["agent_decisions"].append({
        "agent": agent,
        "decision": decision,
        "reasoning": reasoning,
        "success": success,
        "timestamp": datetime.utcnow()
    })


def add_error(state: JobApplicationState, error: str):
    """Add error to state"""
    if "errors" not in state:
        state["errors"] = []

    state["errors"].append({
        "error": error,
        "timestamp": datetime.utcnow(),
        "step": state.get("current_step", "unknown")
    })


def update_metrics(state: JobApplicationState, metric_name: str, value: Any):
    """Update workflow metrics"""
    if "metrics" not in state:
        state["metrics"] = {}

    state["metrics"][metric_name] = value
