"""
Feedback Loop model - Captures application outcomes and agent insights
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from db.base import Base, TimestampMixin, UUIDMixin
from datetime import datetime


class FeedbackLoop(Base, UUIDMixin, TimestampMixin):
    """
    Feedback Loop model - Tracks outcomes and what agents learned from them
    """
    __tablename__ = "feedback_loop"

    # Foreign Key
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)

    # Outcome Information
    outcome = Column(String(50), nullable=False, index=True)  # response/rejection/interview/offer/no_response
    outcome_timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Response Timing (if applicable)
    response_time_days = Column(String(50))  # How many days until response
    response_quality = Column(String(20))  # positive/neutral/negative

    # What Agent Learned
    insights = Column(JSONB)  # Structured insights
    # Example:
    # {
    #   "successful_keywords": ["python", "ai", "fastapi"],
    #   "resume_version": "v2.0",
    #   "match_score_was": 0.85,
    #   "company_responsiveness": "high",
    #   "salary_alignment": true
    # }

    # Strategy Adjustments
    strategy_adjustments = Column(JSONB)  # What agent will change
    # Example:
    # {
    #   "increase_keyword_density": true,
    #   "try_different_resume_format": false,
    #   "adjust_match_threshold": 0.75,
    #   "prioritize_similar_companies": true
    # }

    # Human-Readable Notes
    agent_notes = Column(Text)  # Summary of what was learned

    # Pattern Recognition
    pattern_tags = Column(JSONB)  # Tags for pattern matching
    # Example: ["high_match_score_success", "quick_response", "senior_role"]

    # Relationships
    application = relationship("Application", backref="feedback")

    # Indexes
    __table_args__ = (
        Index('idx_feedback_outcome', 'outcome', 'outcome_timestamp'),
    )

    def __repr__(self):
        return f"<FeedbackLoop(application_id={self.application_id}, outcome={self.outcome})>"

    @classmethod
    def create_feedback(cls, application_id, outcome, insights=None, strategy_adjustments=None, agent_notes=None):
        """Factory method to create feedback entry"""
        return cls(
            application_id=application_id,
            outcome=outcome,
            outcome_timestamp=datetime.utcnow(),
            insights=insights or {},
            strategy_adjustments=strategy_adjustments or {},
            agent_notes=agent_notes,
            pattern_tags=[]
        )

    def add_insight(self, key: str, value):
        """Add an insight to the insights JSON"""
        if self.insights is None:
            self.insights = {}
        self.insights[key] = value

    def add_strategy_adjustment(self, key: str, value):
        """Add a strategy adjustment"""
        if self.strategy_adjustments is None:
            self.strategy_adjustments = {}
        self.strategy_adjustments[key] = value

    def add_pattern_tag(self, tag: str):
        """Add a pattern tag"""
        if self.pattern_tags is None:
            self.pattern_tags = []
        if tag not in self.pattern_tags:
            self.pattern_tags.append(tag)
