"""
Job model - represents scraped job postings
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Boolean, Index
from sqlalchemy.orm import relationship
from db.base import Base, TimestampMixin, UUIDMixin


class Job(Base, UUIDMixin, TimestampMixin):
    """
    Job posting model - stores scraped job listings
    """
    __tablename__ = "jobs"

    # Basic Information
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text)

    # Location & Work Type
    location = Column(String(255), index=True)
    work_type = Column(String(50))  # remote, hybrid, onsite

    # Salary Information
    salary_min = Column(Integer)  # Annual salary in USD
    salary_max = Column(Integer)
    salary_currency = Column(String(10), default="USD")

    # Job Details
    experience_years = Column(Integer)  # Years of experience required
    job_type = Column(String(50))  # full-time, part-time, contract, etc.

    # Source Information
    source = Column(String(50), nullable=False, index=True)  # indeed, linkedin, glassdoor
    source_url = Column(String(500), nullable=False, unique=True)  # Unique job URL
    external_id = Column(String(255), index=True)  # Job ID from source platform

    # Dates
    posted_date = Column(DateTime)  # When job was originally posted
    expires_at = Column(DateTime)  # Job posting expiry date
    scraped_at = Column(DateTime, nullable=False, index=True)

    # Matching & Status
    match_score = Column(Float, default=0.0, index=True)  # 0.0 to 1.0
    is_active = Column(String(20), default="active")  # active, expired, filled, closed

    # Additional Metadata
    company_logo_url = Column(String(500))
    benefits = Column(Text)  # JSON string or text of benefits
    skills_required = Column(Text)  # JSON array as text or comma-separated

    # Agent Processing (NEW)
    agent_evaluated = Column(Boolean, default=False, index=True)  # Whether agent has processed
    agent_recommendation = Column(String(20))  # apply/skip/needs_review
    scraped_by_agent = Column(Boolean, default=True)  # True if agent scraped

    # Relationships
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_job_search', 'title', 'company', 'location'),
        Index('idx_job_matching', 'match_score', 'is_active', 'scraped_at'),
        Index('idx_job_source', 'source', 'scraped_at'),
    )

    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', company='{self.company}', match_score={self.match_score})>"

    @property
    def salary_range_str(self) -> str:
        """Returns formatted salary range string"""
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} - ${self.salary_max:,}"
        elif self.salary_min:
            return f"${self.salary_min:,}+"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,}"
        return "Not specified"

    @property
    def is_expired(self) -> bool:
        """Check if job posting has expired"""
        from datetime import datetime
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
