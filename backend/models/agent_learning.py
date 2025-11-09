"""
Agent Learning model - Tracks agent improvements and learning metrics
"""
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from db.base import Base, TimestampMixin, UUIDMixin


class AgentLearning(Base, UUIDMixin, TimestampMixin):
    """
    Agent Learning model - Stores metrics and insights from agent learning
    """
    __tablename__ = "agent_learning"

    # Agent Information
    agent_type = Column(String(50), nullable=False, index=True)  # scraper/matcher/resume/application/learning
    metric_name = Column(String(100), nullable=False, index=True)  # keyword_success_rate, resume_format_performance, etc.

    # Metrics
    metric_value = Column(Float)  # Numeric metric value
    success_rate = Column(Float)  # 0.0 to 1.0
    sample_size = Column(Integer, default=0)  # Number of data points

    # Context
    context = Column(JSONB)  # What was tried, parameters, configuration
    # Example: {"keyword": "python", "density": 0.15, "position": "title"}

    # Optional: User-specific learning
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    # Indexes
    __table_args__ = (
        Index('idx_agent_type_metric', 'agent_type', 'metric_name'),
        Index('idx_agent_success', 'agent_type', 'success_rate'),
        Index('idx_agent_user', 'user_id', 'agent_type'),
    )

    def __repr__(self):
        return f"<AgentLearning(agent={self.agent_type}, metric={self.metric_name}, value={self.metric_value})>"

    @classmethod
    def log_metric(cls, agent_type: str, metric_name: str, metric_value: float, success_rate: float, context: dict, sample_size: int = 1, user_id=None):
        """Factory method to log a learning metric"""
        return cls(
            agent_type=agent_type,
            metric_name=metric_name,
            metric_value=metric_value,
            success_rate=success_rate,
            context=context,
            sample_size=sample_size,
            user_id=user_id
        )

    @staticmethod
    def get_best_strategy(db_session, agent_type: str, metric_name: str, user_id=None):
        """Get the best performing strategy for an agent"""
        query = db_session.query(AgentLearning).filter(
            AgentLearning.agent_type == agent_type,
            AgentLearning.metric_name == metric_name
        )

        if user_id:
            query = query.filter(AgentLearning.user_id == user_id)

        return query.order_by(AgentLearning.success_rate.desc()).first()
