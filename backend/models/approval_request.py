"""
Approval Request model - Email approval workflow for job applications
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db.base import Base, TimestampMixin, UUIDMixin
from datetime import datetime, timedelta
import secrets


class ApprovalRequest(Base, UUIDMixin, TimestampMixin):
    """
    Approval Request model - Tracks email approval requests sent to users
    """
    __tablename__ = "approval_requests"

    # Foreign Keys
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)

    # Approval Timeline
    sent_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)  # 24 hours from sent_at
    responded_at = Column(DateTime)  # When user responded

    # Status
    status = Column(String(20), default="pending", nullable=False, index=True)  # pending/approved/rejected/expired

    # Magic Link Token
    approval_token = Column(String(255), unique=True, nullable=False, index=True)

    # User Response
    user_response = Column(Text)  # Optional feedback from user

    # Agent Context
    agent_reasoning = Column(Text)  # Why agent recommended this job
    match_score = Column(String(50))  # Match score at time of recommendation

    # Relationships
    application = relationship("Application", backref="approval_request")
    user = relationship("User")
    job = relationship("Job")
    resume = relationship("Resume")

    # Indexes
    __table_args__ = (
        Index('idx_approval_user_status', 'user_id', 'status'),
        Index('idx_approval_expires', 'expires_at', 'status'),
    )

    def __repr__(self):
        return f"<ApprovalRequest(id={self.id}, status={self.status}, user_id={self.user_id}, job_id={self.job_id})>"

    @staticmethod
    def generate_token() -> str:
        """Generate a secure random token for approval links"""
        return secrets.token_urlsafe(32)

    @classmethod
    def create_approval_request(cls, application_id, user_id, job_id, resume_id, agent_reasoning, match_score, timeout_hours=24):
        """Factory method to create an approval request"""
        return cls(
            application_id=application_id,
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            agent_reasoning=agent_reasoning,
            match_score=str(match_score),
            sent_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=timeout_hours),
            approval_token=cls.generate_token(),
            status="pending"
        )

    def is_expired(self) -> bool:
        """Check if approval request has expired"""
        return datetime.utcnow() > self.expires_at and self.status == "pending"

    def approve(self, user_response: str = None):
        """Mark approval request as approved"""
        self.status = "approved"
        self.responded_at = datetime.utcnow()
        if user_response:
            self.user_response = user_response

    def reject(self, user_response: str = None):
        """Mark approval request as rejected"""
        self.status = "rejected"
        self.responded_at = datetime.utcnow()
        if user_response:
            self.user_response = user_response

    def expire(self):
        """Mark approval request as expired"""
        if self.status == "pending":
            self.status = "expired"
