"""
Application model - tracks job applications
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db.base import Base, TimestampMixin, UUIDMixin
import enum


class ApplicationStatus(str, enum.Enum):
    """Enum for application status"""
    PENDING = "pending"  # Ready to apply but not yet submitted
    SUBMITTED = "submitted"  # Application submitted
    VIEWED = "viewed"  # Employer viewed application
    REJECTED = "rejected"  # Application rejected
    INTERVIEW = "interview"  # Interview scheduled
    OFFER = "offer"  # Job offer received
    ACCEPTED = "accepted"  # Offer accepted
    DECLINED = "declined"  # Offer declined
    WITHDRAWN = "withdrawn"  # Application withdrawn


class Application(Base, UUIDMixin, TimestampMixin):
    """
    Application model - tracks job applications and their status
    """
    __tablename__ = "applications"

    # Foreign Keys
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)

    # Application Details
    status = Column(
        SQLEnum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.PENDING,
        nullable=False,
        index=True
    )
    resume_version = Column(String(255))  # Name/version of resume used
    cover_letter_version = Column(String(255))  # Name/version of cover letter used

    # Dates
    applied_at = Column(DateTime, index=True)  # When application was submitted
    response_received_at = Column(DateTime)  # When employer first responded
    interview_date = Column(DateTime)  # Scheduled interview date

    # Response Tracking
    response_received = Column(Boolean, default=False, index=True)
    response_type = Column(String(50))  # email, phone, portal, etc.
    response_text = Column(Text)  # Actual response content

    # Application Metadata
    application_method = Column(String(50))  # direct, indeed, linkedin, etc.
    confirmation_number = Column(String(255))  # Application confirmation/reference number
    portal_url = Column(String(500))  # URL to check application status

    # Notes & Follow-up
    notes = Column(Text)  # User notes about the application
    follow_up_date = Column(DateTime)  # Date to follow up
    automated = Column(Boolean, default=True)  # Whether applied automatically or manually

    # Rejection Details
    rejection_reason = Column(Text)  # Reason for rejection if provided
    rejection_date = Column(DateTime)

    # Screenshots & Evidence
    screenshot_path = Column(String(500))  # Path to screenshot of submission
    submission_data = Column(Text)  # JSON string of form data submitted

    # Agent Context (NEW)
    agent_reasoning = Column(Text)  # Why agent recommended this job
    applied_by_agent = Column(Boolean, default=False)  # True if agent submitted
    approval_request_id = Column(UUID(as_uuid=True), ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    job = relationship("Job", back_populates="applications")
    user = relationship("User", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")

    # Indexes for performance
    __table_args__ = (
        Index('idx_application_status_date', 'status', 'applied_at'),
        Index('idx_application_user_status', 'user_id', 'status'),
        Index('idx_application_job', 'job_id', 'status'),
    )

    def __repr__(self):
        return f"<Application(id={self.id}, job_id={self.job_id}, status={self.status.value}, applied_at={self.applied_at})>"

    @property
    def days_since_applied(self) -> int:
        """Calculate days since application was submitted"""
        from datetime import datetime
        if self.applied_at:
            delta = datetime.utcnow() - self.applied_at
            return delta.days
        return 0

    @property
    def is_active(self) -> bool:
        """Check if application is still active (not rejected/declined/withdrawn)"""
        inactive_statuses = {
            ApplicationStatus.REJECTED,
            ApplicationStatus.DECLINED,
            ApplicationStatus.WITHDRAWN,
            ApplicationStatus.ACCEPTED
        }
        return self.status not in inactive_statuses

    def update_status(self, new_status: ApplicationStatus, notes: str = None) -> None:
        """Update application status with automatic date tracking"""
        from datetime import datetime
        self.status = new_status

        if new_status == ApplicationStatus.SUBMITTED and not self.applied_at:
            self.applied_at = datetime.utcnow()
        elif new_status in {ApplicationStatus.REJECTED, ApplicationStatus.DECLINED, ApplicationStatus.WITHDRAWN}:
            if not self.rejection_date:
                self.rejection_date = datetime.utcnow()
        elif new_status in {ApplicationStatus.VIEWED, ApplicationStatus.INTERVIEW, ApplicationStatus.OFFER}:
            if not self.response_received:
                self.response_received = True
                self.response_received_at = datetime.utcnow()

        if notes:
            existing_notes = self.notes or ""
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            self.notes = f"{existing_notes}\n[{timestamp}] {notes}".strip()
