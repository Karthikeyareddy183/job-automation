"""
LangGraph Workflow - Orchestrates the entire job application workflow
"""
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from .state import JobApplicationState, create_initial_state
from .supervisor_agent import SupervisorAgent
from .scraper_agent import ScraperAgent
from .matcher_agent import MatcherAgent
from .resume_tailor_agent import ResumeTailorAgent
from .learning_agent import LearningAgent
import logging

logger = logging.getLogger(__name__)


class JobApplicationWorkflow:
    """
    LangGraph workflow for autonomous job applications

    Workflow steps:
    1. scrape -> Scrape job postings
    2. match -> Match jobs to user profile
    3. tailor -> Tailor resume for matched job
    4. approve -> Request user approval (handled separately)
    5. apply -> Submit application (TODO)
    6. learn -> Learn from results
    """

    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.scraper = ScraperAgent()
        self.matcher = MatcherAgent()
        self.resume_tailor = ResumeTailorAgent()
        self.learning = LearningAgent()

        # Build workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Build LangGraph workflow

        Returns:
            Compiled workflow graph
        """
        # Create graph
        graph = StateGraph(JobApplicationState)

        # Add nodes (agent steps)
        graph.add_node("scrape", self._scrape_node)
        graph.add_node("match", self._match_node)
        graph.add_node("tailor", self._tailor_node)
        graph.add_node("approve", self._approve_node)
        graph.add_node("apply", self._apply_node)
        graph.add_node("learn", self._learn_node)
        graph.add_node("supervisor", self._supervisor_node)

        # Set entry point
        graph.set_entry_point("scrape")

        # Add edges (workflow transitions)
        # After each step, go to supervisor to decide next action
        graph.add_edge("scrape", "supervisor")
        graph.add_edge("match", "supervisor")
        graph.add_edge("tailor", "supervisor")
        graph.add_edge("approve", "supervisor")
        graph.add_edge("apply", "supervisor")
        graph.add_edge("learn", "supervisor")

        # Supervisor decides next action (conditional routing)
        graph.add_conditional_edges(
            "supervisor",
            self._route_next_step,
            {
                "scrape": "scrape",
                "match": "match",
                "tailor": "tailor",
                "approve": "approve",
                "apply": "apply",
                "learn": "learn",
                "stop": END,
                "wait": END  # Wait for user approval
            }
        )

        # Compile graph
        return graph.compile()

    async def _scrape_node(self, state: JobApplicationState) -> JobApplicationState:
        """Scraping node"""
        logger.info("Executing scrape node...")
        return await self.scraper.execute(state)

    async def _match_node(self, state: JobApplicationState) -> JobApplicationState:
        """Matching node"""
        logger.info("Executing match node...")
        return await self.matcher.execute(state)

    async def _tailor_node(self, state: JobApplicationState) -> JobApplicationState:
        """Resume tailoring node"""
        logger.info("Executing tailor node...")
        return await self.resume_tailor.execute(state)

    async def _approve_node(self, state: JobApplicationState) -> JobApplicationState:
        """Approval request node"""
        logger.info("Executing approve node...")
        # TODO: Send approval email
        # For now, mark as pending
        state["approval_status"] = "pending"
        state["current_step"] = "wait"
        return state

    async def _apply_node(self, state: JobApplicationState) -> JobApplicationState:
        """Application submission node"""
        logger.info("Executing apply node...")
        # TODO: Implement application submission
        state["application_status"] = "submitted"
        state["current_step"] = "learn"
        return state

    async def _learn_node(self, state: JobApplicationState) -> JobApplicationState:
        """Learning node"""
        logger.info("Executing learn node...")
        return await self.learning.execute(state)

    async def _supervisor_node(self, state: JobApplicationState) -> JobApplicationState:
        """Supervisor decision node"""
        logger.info("Executing supervisor node...")
        return await self.supervisor.execute(state)

    def _route_next_step(self, state: JobApplicationState) -> Literal["scrape", "match", "tailor", "approve", "apply", "learn", "stop", "wait"]:
        """
        Route to next step based on supervisor decision

        Args:
            state: Current workflow state

        Returns:
            Next step name
        """
        next_action = state.get("next_action", "stop")
        logger.info(f"Routing to: {next_action}")
        return next_action

    async def run(self, user_id: str, user_preferences: Dict) -> Dict[str, Any]:
        """
        Run the complete workflow

        Args:
            user_id: User ID
            user_preferences: User job preferences

        Returns:
            Final workflow state
        """
        try:
            logger.info(f"Starting workflow for user {user_id}")

            # Create initial state
            initial_state = create_initial_state(user_id, user_preferences)

            # Run workflow
            final_state = await self.workflow.ainvoke(initial_state)

            logger.info("Workflow completed")
            return final_state

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            raise

    async def resume_workflow(self, state: JobApplicationState) -> Dict[str, Any]:
        """
        Resume workflow from a saved state (e.g., after user approval)

        Args:
            state: Saved workflow state

        Returns:
            Final workflow state
        """
        try:
            logger.info("Resuming workflow...")

            # Continue from current state
            final_state = await self.workflow.ainvoke(state)

            logger.info("Workflow resumed and completed")
            return final_state

        except Exception as e:
            logger.error(f"Workflow resume failed: {e}")
            raise

    def get_workflow_visualization(self) -> str:
        """
        Get Mermaid diagram of workflow

        Returns:
            Mermaid diagram string
        """
        return """
graph TD
    Start([Start]) --> Scrape[Scrape Jobs]
    Scrape --> Supervisor1{Supervisor}

    Supervisor1 -->|Jobs Found| Match[Match Jobs]
    Supervisor1 -->|No Jobs| Learn[Learn]

    Match --> Supervisor2{Supervisor}
    Supervisor2 -->|Matches Found| Tailor[Tailor Resume]
    Supervisor2 -->|No Matches| Learn

    Tailor --> Supervisor3{Supervisor}
    Supervisor3 -->|Resume Ready| Approve[Request Approval]
    Supervisor3 -->|Failed| Match

    Approve --> Wait[Wait for User]
    Wait -->|Approved| Apply[Submit Application]
    Wait -->|Rejected| Learn
    Wait -->|Expired| Match

    Apply --> Supervisor4{Supervisor}
    Supervisor4 -->|More Jobs| Match
    Supervisor4 -->|All Done| Learn

    Learn --> End([End])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style Approve fill:#FFD700
    style Wait fill:#FFA500
"""


# Singleton instance
workflow_instance = JobApplicationWorkflow()


async def run_job_application_workflow(user_id: str, user_preferences: Dict) -> Dict[str, Any]:
    """
    Convenience function to run workflow

    Args:
        user_id: User ID
        user_preferences: User job preferences

    Returns:
        Final workflow state
    """
    return await workflow_instance.run(user_id, user_preferences)


async def resume_job_application_workflow(state: JobApplicationState) -> Dict[str, Any]:
    """
    Convenience function to resume workflow

    Args:
        state: Saved workflow state

    Returns:
        Final workflow state
    """
    return await workflow_instance.resume_workflow(state)
