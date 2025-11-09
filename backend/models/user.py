"""
User model - manages user accounts and preferences
"""
from sqlalchemy import Column, String, Boolean, Text, Index, DateTime
from sqlalchemy.orm import relationship
from db.base import Base, TimestampMixin, UUIDMixin
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base, UUIDMixin, TimestampMixin):
    """
    User model - stores user accounts and job search preferences
    """
    __tablename__ = "users"

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255))

    # Profile Information
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50))
    location = Column(String(255))  # Current location
    timezone = Column(String(50), default="UTC")

    # Job Search Preferences
    target_titles = Column(Text)  # JSON array of job titles looking for
    target_locations = Column(Text)  # JSON array of preferred locations
    target_companies = Column(Text)  # JSON array of companies interested in
    keywords = Column(Text)  # JSON array of keywords to match
    excluded_keywords = Column(Text)  # JSON array of keywords to avoid

    # Salary Preferences
    min_salary = Column(String(50))  # Minimum acceptable salary
    max_salary = Column(String(50))  # Maximum salary expectation
    salary_currency = Column(String(10), default="USD")

    # Work Preferences
    work_type_preference = Column(String(50))  # remote, hybrid, onsite, any
    job_type_preference = Column(String(50))  # full-time, part-time, contract, any
    min_experience_years = Column(String(50))  # Minimum years of experience
    max_experience_years = Column(String(50))  # Maximum years of experience

    # Application Settings
    max_applications_per_day = Column(String(50), default="20")
    min_match_score = Column(String(50), default="0.70")  # Minimum match score (0.0 to 1.0)
    auto_apply_enabled = Column(Boolean, default=False)  # Enable automatic applications
    require_manual_approval = Column(Boolean, default=True)  # Require approval before applying

    # AI Preferences
    preferred_ai_model = Column(String(50), default="claude-3.5-sonnet")  # AI model for resume tailoring
    resume_tone = Column(String(50), default="professional")  # professional, casual, formal
    tailoring_aggressiveness = Column(String(50), default="moderate")  # conservative, moderate, aggressive

    # Notification Settings
    email_notifications = Column(Boolean, default=True)
    notification_frequency = Column(String(50), default="daily")  # realtime, daily, weekly
    notify_on_response = Column(Boolean, default=True)
    notify_on_interview = Column(Boolean, default=True)

    # Statistics
    total_applications = Column(String(50), default="0")
    total_responses = Column(String(50), default="0")
    total_interviews = Column(String(50), default="0")
    total_offers = Column(String(50), default="0")

    # Session & Security
    last_login_at = Column(DateTime)
    last_activity_at = Column(DateTime)
    failed_login_attempts = Column(String(50), default="0")
    locked_until = Column(DateTime)

    # Agent Control (NEW)
    agent_status = Column(String(20), default="active")  # active/paused/stopped
    last_agent_run = Column(DateTime)  # When agents last processed for this user
    learning_enabled = Column(Boolean, default=True)  # Whether agents should learn
    approval_timeout_hours = Column(String(50), default="24")  # Hours before approval expires

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_activity', 'last_activity_at'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"

    def set_password(self, password: str) -> None:
        """Hash and set user password"""
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(password, self.hashed_password)

    @property
    def response_rate(self) -> float:
        """Calculate response rate percentage"""
        try:
            total = int(self.total_applications or "0")
            responses = int(self.total_responses or "0")
            if total > 0:
                return (responses / total) * 100
            return 0.0
        except (ValueError, ZeroDivisionError):
            return 0.0

    @property
    def interview_rate(self) -> float:
        """Calculate interview rate percentage"""
        try:
            total = int(self.total_applications or "0")
            interviews = int(self.total_interviews or "0")
            if total > 0:
                return (interviews / total) * 100
            return 0.0
        except (ValueError, ZeroDivisionError):
            return 0.0

    @property
    def offer_rate(self) -> float:
        """Calculate offer rate percentage"""
        try:
            total = int(self.total_applications or "0")
            offers = int(self.total_offers or "0")
            if total > 0:
                return (offers / total) * 100
            return 0.0
        except (ValueError, ZeroDivisionError):
            return 0.0

    def increment_stat(self, stat_name: str) -> None:
        """Increment a statistic counter"""
        if not hasattr(self, stat_name):
            return
        try:
            current = int(getattr(self, stat_name) or "0")
            setattr(self, stat_name, str(current + 1))
        except ValueError:
            setattr(self, stat_name, "1")

    def update_activity(self) -> None:
        """Update last activity timestamp"""
        from datetime import datetime
        self.last_activity_at = datetime.utcnow()
