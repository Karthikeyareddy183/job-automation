"""
Resume model - manages resume versions and templates
"""
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Index, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db.base import Base, TimestampMixin, UUIDMixin
import enum


class ResumeFormat(str, enum.Enum):
    """Enum for resume file formats"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class ResumeType(str, enum.Enum):
    """Enum for resume types"""
    BASE = "base"  # Original base resume
    TAILORED = "tailored"  # AI-tailored for specific job
    TEMPLATE = "template"  # Resume template


class Resume(Base, UUIDMixin, TimestampMixin):
    """
    Resume model - stores resume versions and metadata
    """
    __tablename__ = "resumes"

    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)  # If tailored
    based_on_resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)

    # Resume Metadata
    name = Column(String(255), nullable=False)  # User-friendly name
    version = Column(String(50))  # Version identifier (e.g., "v1.0", "2024-01")
    resume_type = Column(
        SQLEnum(ResumeType, name="resume_type"),
        default=ResumeType.BASE,
        nullable=False,
        index=True
    )

    # File Information
    file_format = Column(
        SQLEnum(ResumeFormat, name="resume_format"),
        default=ResumeFormat.PDF,
        nullable=False
    )
    file_path = Column(String(500))  # Local file path or S3/Supabase Storage URL
    file_size = Column(String(50))  # File size in KB/MB
    storage_provider = Column(String(50), default="local")  # local, s3, supabase

    # Content
    content_text = Column(Text)  # Plain text version for AI processing
    content_json = Column(Text)  # JSON structure of resume sections
    html_content = Column(Text)  # HTML version for preview

    # Tailoring Information (if tailored resume)
    tailored_for_title = Column(String(255))  # Job title this was tailored for
    tailored_for_company = Column(String(255))  # Company name
    tailoring_prompt = Column(Text)  # AI prompt used for tailoring
    tailoring_model = Column(String(100))  # AI model used (gpt-4, claude-3.5, etc.)
    changes_made = Column(Text)  # Summary of changes made by AI

    # Template Information (if template)
    template_name = Column(String(100))  # Template identifier
    template_style = Column(String(50))  # modern, classic, minimal, etc.

    # Status & Usage
    is_active = Column(Boolean, default=True, index=True)  # Whether resume is currently in use
    is_default = Column(Boolean, default=False)  # Default resume for new applications
    usage_count = Column(String(50), default="0")  # Number of times used in applications

    # Statistics
    views = Column(String(50), default="0")  # Number of times viewed
    downloads = Column(String(50), default="0")  # Number of times downloaded
    success_rate = Column(String(50))  # Response rate when using this resume

    # Agent Performance Tracking (NEW)
    performance_score = Column(String(50))  # Overall success rate 0.0-1.0
    response_rate = Column(String(50))  # % of applications that got responses
    interview_rate = Column(String(50))  # % that led to interviews
    last_performance_update = Column(DateTime)  # When stats were last calculated

    # Metadata
    tags = Column(Text)  # Comma-separated tags (e.g., "software,python,remote")
    notes = Column(Text)  # User notes about this resume
    last_used_at = Column(String(50))  # Last time resume was used in application

    # Relationships
    user = relationship("User", back_populates="resumes")
    applications = relationship("Application", back_populates="resume")
    job = relationship("Job", foreign_keys=[job_id])

    # Indexes for performance
    __table_args__ = (
        Index('idx_resume_user_type', 'user_id', 'resume_type', 'is_active'),
        Index('idx_resume_job', 'job_id'),
    )

    def __repr__(self):
        return f"<Resume(id={self.id}, name='{self.name}', type={self.resume_type.value}, format={self.file_format.value})>"

    @property
    def file_extension(self) -> str:
        """Get file extension based on format"""
        return f".{self.file_format.value}"

    @property
    def is_tailored(self) -> bool:
        """Check if this is a tailored resume"""
        return self.resume_type == ResumeType.TAILORED

    @property
    def is_base_resume(self) -> bool:
        """Check if this is a base resume"""
        return self.resume_type == ResumeType.BASE

    def increment_usage(self) -> None:
        """Increment usage count"""
        from datetime import datetime
        try:
            current = int(self.usage_count or "0")
            self.usage_count = str(current + 1)
        except ValueError:
            self.usage_count = "1"
        self.last_used_at = datetime.utcnow().isoformat()
