"""
Agent Memory model - Vector store metadata for RAG and agent knowledge
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from db.base import Base, TimestampMixin, UUIDMixin
from datetime import datetime


class AgentMemory(Base, UUIDMixin, TimestampMixin):
    """
    Agent Memory model - Stores metadata for vector embeddings and agent knowledge
    """
    __tablename__ = "agent_memory"

    # Memory Type
    memory_type = Column(String(50), nullable=False, index=True)  # successful_resume/rejection_pattern/company_insight/keyword_strategy

    # Content
    content = Column(Text, nullable=False)  # What to remember
    content_summary = Column(String(500))  # Short summary for quick reference

    # Vector Store Reference
    embedding_id = Column(String(255), index=True)  # ChromaDB/FAISS collection ID
    collection_name = Column(String(100))  # Which vector collection
    embedding_model = Column(String(100))  # Which model created embedding (text-embedding-ada-002, etc.)

    # Importance & Relevance
    relevance_score = Column(Float, default=0.5)  # 0.0 to 1.0 - How important/relevant
    confidence_score = Column(Float, default=0.5)  # 0.0 to 1.0 - How confident we are

    # Usage Tracking
    usage_count = Column(Integer, default=0)  # How often this memory was referenced
    last_used_at = Column(DateTime)  # When it was last retrieved
    success_rate = Column(Float)  # If applicable, success rate when using this memory

    # Context & Metadata
    context_metadata = Column(JSONB)  # Additional structured data (renamed from 'metadata')
    # Example:
    # {
    #   "job_title": "Software Engineer",
    #   "company_type": "startup",
    #   "salary_range": "80k-120k",
    #   "keywords": ["python", "ai"],
    #   "outcome": "interview"
    # }

    # Tags for Filtering
    tags = Column(JSONB)  # Array of tags for categorization
    # Example: ["high_success", "ai_jobs", "remote_work", "senior_level"]

    # Expiration (optional)
    expires_at = Column(DateTime)  # When this memory should be considered stale

    # Indexes
    __table_args__ = (
        Index('idx_memory_type_score', 'memory_type', 'relevance_score'),
        Index('idx_memory_usage', 'usage_count', 'last_used_at'),
        Index('idx_memory_embedding', 'collection_name', 'embedding_id'),
    )

    def __repr__(self):
        return f"<AgentMemory(type={self.memory_type}, relevance={self.relevance_score}, uses={self.usage_count})>"

    @classmethod
    def store_memory(cls, memory_type: str, content: str, embedding_id: str, collection_name: str,
                     relevance_score: float = 0.5, context_metadata: dict = None, tags: list = None):
        """Factory method to store a new memory"""
        return cls(
            memory_type=memory_type,
            content=content,
            content_summary=content[:500] if len(content) > 500 else content,
            embedding_id=embedding_id,
            collection_name=collection_name,
            embedding_model="text-embedding-ada-002",  # Default, can be overridden
            relevance_score=relevance_score,
            confidence_score=0.5,
            usage_count=0,
            context_metadata=context_metadata or {},
            tags=tags or []
        )

    def increment_usage(self):
        """Increment usage counter and update last used timestamp"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()

    def is_expired(self) -> bool:
        """Check if memory has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    def add_tag(self, tag: str):
        """Add a tag to this memory"""
        if self.tags is None:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)

    def update_relevance(self, new_score: float):
        """Update relevance score based on usage effectiveness"""
        # Weighted average: 70% old score, 30% new
        self.relevance_score = (self.relevance_score * 0.7) + (new_score * 0.3)
