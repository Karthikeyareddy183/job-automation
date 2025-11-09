"""
Learning Agent - Autonomous improvement and pattern discovery
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResponse
from .state import JobApplicationState, add_agent_decision, add_error, update_metrics
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class LearningAgent(BaseAgent):
    """
    Learning Agent - Analyzes outcomes and continuously improves agent strategies

    Responsibilities:
    - Analyze application outcomes (responses, rejections, interviews)
    - Identify successful patterns
    - Discover failure patterns
    - Adjust agent strategies
    - Update matching criteria
    - Improve resume tailoring
    - Learn from user feedback
    """

    def __init__(self):
        super().__init__(
            name="Learning",
            model="llama-3.1-70b-versatile",  # Use larger model for complex analysis
            temperature=0.3
        )

    async def execute(self, state: JobApplicationState) -> Dict[str, Any]:
        """
        Execute learning logic

        Args:
            state: Current workflow state

        Returns:
            Updated state with learning insights
        """
        try:
            self.log("Starting learning analysis...")

            # Analyze this workflow session
            insights = await self._analyze_workflow(state)

            # Store insights
            state["learning_insights"]["workflow_analysis"] = insights

            # Generate strategy adjustments
            adjustments = await self._generate_strategy_adjustments(state, insights)
            state["strategy_adjustments"] = adjustments

            # Update state
            state["current_step"] = "complete"

            # Add decision
            add_agent_decision(
                state,
                agent="learning",
                decision="workflow_analysis_complete",
                reasoning=f"Generated {len(adjustments)} strategy adjustments",
                success=True
            )

            self.log("Learning analysis complete")
            return state

        except Exception as e:
            self.log(f"Learning failed: {e}", "error")
            add_error(state, f"Learning error: {e}")
            state["current_step"] = "complete"
            return state

    async def _analyze_workflow(self, state: JobApplicationState) -> Dict[str, Any]:
        """
        Analyze the workflow execution

        Args:
            state: Current workflow state

        Returns:
            Analysis insights
        """
        try:
            # Extract workflow data
            scraped_count = len(state.get("scraped_jobs", []))
            matched_count = len(state.get("matched_jobs", []))
            errors = state.get("errors", [])
            decisions = state.get("agent_decisions", [])
            metrics = state.get("metrics", {})

            # Calculate success rates
            match_rate = matched_count / scraped_count if scraped_count > 0 else 0

            insights = {
                "scraped_jobs": scraped_count,
                "matched_jobs": matched_count,
                "match_rate": match_rate,
                "errors_count": len(errors),
                "decisions_count": len(decisions),
                "workflow_duration": self._calculate_duration(state),
                "agent_performance": self._analyze_agent_performance(state),
                "common_errors": self._identify_common_errors(errors),
                "recommendations": []
            }

            # Generate recommendations
            if match_rate < 0.1:
                insights["recommendations"].append("Match rate is very low. Consider lowering match threshold or adjusting keywords.")
            elif match_rate > 0.8:
                insights["recommendations"].append("Match rate is very high. Consider raising match threshold to be more selective.")

            if len(errors) > 5:
                insights["recommendations"].append("Multiple errors detected. Review scraping and matching logic.")

            self.log(f"Workflow analysis: {scraped_count} scraped, {matched_count} matched ({match_rate:.1%})")

            return insights

        except Exception as e:
            self.log(f"Workflow analysis failed: {e}", "error")
            return {"error": str(e)}

    async def _generate_strategy_adjustments(self, state: JobApplicationState, insights: Dict) -> Dict[str, Any]:
        """
        Generate strategy adjustments based on insights

        Args:
            state: Current workflow state
            insights: Analysis insights

        Returns:
            Strategy adjustments
        """
        try:
            adjustments = {
                "scraper": {},
                "matcher": {},
                "resume_tailor": {},
                "timestamp": datetime.utcnow().isoformat()
            }

            # Scraper adjustments
            match_rate = insights.get("match_rate", 0)
            if match_rate < 0.1:
                adjustments["scraper"]["action"] = "broaden_search"
                adjustments["scraper"]["reasoning"] = "Low match rate suggests search is too narrow"

            # Matcher adjustments
            if match_rate > 0.8:
                adjustments["matcher"]["action"] = "raise_threshold"
                adjustments["matcher"]["new_threshold"] = 0.75
                adjustments["matcher"]["reasoning"] = "High match rate suggests we can be more selective"
            elif match_rate < 0.1:
                adjustments["matcher"]["action"] = "lower_threshold"
                adjustments["matcher"]["new_threshold"] = 0.60
                adjustments["matcher"]["reasoning"] = "Low match rate suggests threshold is too strict"

            self.log(f"Generated strategy adjustments for {len(adjustments)} agents")

            return adjustments

        except Exception as e:
            self.log(f"Strategy adjustment generation failed: {e}", "error")
            return {}

    async def analyze_application_outcome(
        self,
        application_id: str,
        outcome: str,
        user_feedback: str = None
    ) -> Dict[str, Any]:
        """
        Analyze individual application outcome

        Args:
            application_id: Application ID
            outcome: Outcome (response/rejection/interview/offer)
            user_feedback: Optional user feedback

        Returns:
            Analysis and learnings
        """
        try:
            self.log(f"Analyzing outcome for application {application_id}: {outcome}")

            # TODO: Fetch application details from database
            # For now, return placeholder analysis

            analysis = {
                "application_id": application_id,
                "outcome": outcome,
                "timestamp": datetime.utcnow().isoformat(),
                "patterns_identified": [],
                "learnings": []
            }

            # Outcome-specific analysis
            if outcome == "rejection":
                analysis["learnings"].append("Analyze resume keywords and matching score")
                analysis["patterns_identified"].append("Check if similar rejections occurred")
            elif outcome == "interview":
                analysis["learnings"].append("This resume/job combination was successful")
                analysis["patterns_identified"].append("Extract winning patterns")
            elif outcome == "response":
                analysis["learnings"].append("Application got a response - positive signal")

            # User feedback analysis
            if user_feedback:
                sentiment = await self._analyze_feedback_sentiment(user_feedback)
                analysis["user_feedback_sentiment"] = sentiment

            return analysis

        except Exception as e:
            self.log(f"Outcome analysis failed: {e}", "error")
            return {"error": str(e)}

    async def _analyze_feedback_sentiment(self, feedback: str) -> str:
        """
        Analyze user feedback sentiment using LLM

        Args:
            feedback: User feedback text

        Returns:
            Sentiment (positive/negative/neutral)
        """
        try:
            prompt = f"""
Analyze the sentiment of this user feedback about a job application:

FEEDBACK: {feedback}

Respond with only one word: positive, negative, or neutral
"""

            response = await self.invoke_llm(prompt)
            sentiment = response.strip().lower()

            if sentiment not in ["positive", "negative", "neutral"]:
                sentiment = "neutral"

            return sentiment

        except Exception as e:
            self.log(f"Sentiment analysis failed: {e}", "error")
            return "neutral"

    async def discover_patterns(self, applications: List[Dict]) -> Dict[str, Any]:
        """
        Discover patterns from historical applications

        Args:
            applications: List of application dictionaries

        Returns:
            Discovered patterns
        """
        try:
            self.log(f"Analyzing {len(applications)} applications for patterns...")

            # Build prompt for LLM pattern discovery
            prompt = self._build_pattern_discovery_prompt(applications)

            # Invoke LLM
            response = await self.invoke_llm(prompt)

            # Parse patterns
            patterns = self._parse_patterns(response)

            self.log(f"Discovered {len(patterns.get('patterns', []))} patterns")

            return patterns

        except Exception as e:
            self.log(f"Pattern discovery failed: {e}", "error")
            return {"patterns": [], "error": str(e)}

    def _build_pattern_discovery_prompt(self, applications: List[Dict]) -> str:
        """
        Build prompt for pattern discovery

        Args:
            applications: List of applications

        Returns:
            Prompt string
        """
        # Summarize applications
        summary = []
        for app in applications[:20]:  # Limit to 20 for token efficiency
            summary.append({
                "job_title": app.get("job_title"),
                "company": app.get("company"),
                "match_score": app.get("match_score"),
                "outcome": app.get("status"),
                "response_received": app.get("response_received", False)
            })

        prompt = f"""
You are a data analyst specializing in job application patterns.

APPLICATIONS DATA:
{summary}

TASK:
Analyze these applications and identify patterns:

1. SUCCESS PATTERNS: What characteristics do successful applications share?
   - Job titles
   - Company types
   - Match score ranges
   - Keywords

2. FAILURE PATTERNS: What characteristics do rejected applications share?
   - Mismatched requirements
   - Over/under-qualified
   - Industry mismatches

3. RECOMMENDATIONS: What should we adjust?
   - Targeting strategy
   - Match threshold
   - Keywords to prioritize
   - Keywords to avoid

Provide your analysis in a structured format.
"""

        return prompt

    def _parse_patterns(self, response: str) -> Dict[str, Any]:
        """
        Parse pattern discovery response

        Args:
            response: LLM response

        Returns:
            Parsed patterns
        """
        # Simple parsing - can be improved
        return {
            "patterns": [response],
            "timestamp": datetime.utcnow().isoformat()
        }

    def _calculate_duration(self, state: JobApplicationState) -> float:
        """Calculate workflow duration in seconds"""
        start_time = state.get("workflow_start_time")
        if not start_time:
            return 0.0

        duration = (datetime.utcnow() - start_time).total_seconds()
        return duration

    def _analyze_agent_performance(self, state: JobApplicationState) -> Dict[str, Any]:
        """Analyze individual agent performance"""
        decisions = state.get("agent_decisions", [])

        agent_stats = {}
        for decision in decisions:
            agent = decision.get("agent")
            if agent not in agent_stats:
                agent_stats[agent] = {"total": 0, "success": 0, "failures": 0}

            agent_stats[agent]["total"] += 1
            if decision.get("success"):
                agent_stats[agent]["success"] += 1
            else:
                agent_stats[agent]["failures"] += 1

        return agent_stats

    def _identify_common_errors(self, errors: List[Dict]) -> List[str]:
        """Identify most common error types"""
        if not errors:
            return []

        # Count error types
        error_counts = {}
        for error in errors:
            error_msg = error.get("error", "Unknown error")
            # Extract error type (first 50 chars)
            error_type = error_msg[:50]

            if error_type not in error_counts:
                error_counts[error_type] = 0
            error_counts[error_type] += 1

        # Sort by frequency
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)

        # Return top 3
        return [error_type for error_type, count in sorted_errors[:3]]
