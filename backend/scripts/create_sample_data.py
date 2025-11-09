"""
Create sample data for testing the Job Automation System
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.user import User
from models.job import Job
from models.resume import Resume, ResumeFormat, ResumeType
from models.application import Application, ApplicationStatus
import random


def create_sample_user(db: Session) -> User:
    """Create a sample user with job preferences"""
    print("Creating sample user...")

    user = User(
        email="test@example.com",
        full_name="Test User",
        phone="+91-9876543210",
        location="Bangalore, India",
        timezone="Asia/Kolkata",

        # Job Search Preferences
        target_titles='["Software Engineer", "Python Developer", "AI Engineer", "Backend Developer"]',
        target_locations='["Bangalore", "Remote"]',
        keywords='["Python", "AI", "FastAPI", "Machine Learning", "Django"]',
        excluded_keywords='["Java only", "C++ only"]',

        # Salary Preferences
        min_salary="500000",
        max_salary="2000000",
        salary_currency="INR",

        # Work Preferences
        work_type_preference="onsite",
        job_type_preference="full-time",
        min_experience_years="2",
        max_experience_years="5",

        # Application Settings
        max_applications_per_day="20",
        min_match_score="0.70",
        auto_apply_enabled=False,
        require_manual_approval=True,

        # AI Preferences
        preferred_ai_model="claude-3.5-sonnet",
        resume_tone="professional",
        tailoring_aggressiveness="moderate",

        # Statistics
        total_applications="0",
        total_responses="0",
        total_interviews="0",
        total_offers="0",
    )

    # Set a simple hashed password (for testing only)
    # In production, use user.set_password("test123456")
    user.hashed_password = "test123456_hashed"  # Placeholder for testing

    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"✅ Created user: {user.email}")
    return user


def create_sample_jobs(db: Session) -> list[Job]:
    """Create sample job postings"""
    print("\nCreating sample job postings...")

    sample_jobs = [
        {
            "title": "Software Engineer - Python/AI",
            "company": "Tech Mahindra",
            "description": "Looking for a talented Software Engineer with expertise in Python and AI. You'll work on cutting-edge machine learning projects.",
            "requirements": "3+ years Python, AI/ML experience, FastAPI, Docker",
            "location": "Bangalore, Karnataka",
            "work_type": "onsite",
            "salary_min": 800000,
            "salary_max": 1200000,
            "experience_years": 3,
            "source": "indeed",
            "source_url": "https://indeed.com/job/12345",
            "skills_required": "Python, TensorFlow, PyTorch, FastAPI",
        },
        {
            "title": "AI/ML Engineer",
            "company": "Infosys",
            "description": "Join our AI team to build intelligent systems. Work with large datasets and deploy ML models at scale.",
            "requirements": "2-4 years experience, Python, Deep Learning, AWS",
            "location": "Bangalore, Karnataka",
            "work_type": "hybrid",
            "salary_min": 900000,
            "salary_max": 1500000,
            "experience_years": 3,
            "source": "indeed",
            "source_url": "https://indeed.com/job/12346",
            "skills_required": "Python, Keras, AWS SageMaker, MLOps",
        },
        {
            "title": "Backend Developer - Python",
            "company": "Flipkart",
            "description": "Build scalable backend services for India's largest e-commerce platform. Work with microservices architecture.",
            "requirements": "3+ years Python, FastAPI/Django, PostgreSQL, Redis",
            "location": "Bangalore, Karnataka",
            "work_type": "onsite",
            "salary_min": 1200000,
            "salary_max": 1800000,
            "experience_years": 3,
            "source": "indeed",
            "source_url": "https://indeed.com/job/12347",
            "skills_required": "Python, FastAPI, PostgreSQL, Microservices",
        },
        {
            "title": "Python Developer",
            "company": "Wipro",
            "description": "Develop and maintain Python applications. Work on automation, data processing, and API development.",
            "requirements": "2+ years Python, REST APIs, Database design",
            "location": "Bangalore, Karnataka",
            "work_type": "onsite",
            "salary_min": 600000,
            "salary_max": 900000,
            "experience_years": 2,
            "source": "indeed",
            "source_url": "https://indeed.com/job/12348",
            "skills_required": "Python, Django, MySQL, REST APIs",
        },
        {
            "title": "Full Stack Developer",
            "company": "Amazon",
            "description": "Build customer-facing applications using Python backend and React frontend. High-scale distributed systems.",
            "requirements": "4+ years, Python, React, AWS, System Design",
            "location": "Bangalore, Karnataka",
            "work_type": "onsite",
            "salary_min": 2000000,
            "salary_max": 3000000,
            "experience_years": 4,
            "source": "indeed",
            "source_url": "https://indeed.com/job/12349",
            "skills_required": "Python, React, AWS, DynamoDB, Lambda",
        },
        {
            "title": "Data Engineer - Python",
            "company": "Accenture",
            "description": "Build data pipelines and ETL processes. Work with big data technologies and cloud platforms.",
            "requirements": "3+ years Python, Spark, Kafka, SQL",
            "location": "Bangalore, Karnataka",
            "work_type": "hybrid",
            "salary_min": 1000000,
            "salary_max": 1400000,
            "experience_years": 3,
            "source": "indeed",
            "source_url": "https://indeed.com/job/12350",
            "skills_required": "Python, Apache Spark, Kafka, SQL, Azure",
        },
        {
            "title": "Software Engineer - AI Research",
            "company": "Microsoft India",
            "description": "Research and develop AI solutions. Publish papers, build prototypes, and work on cutting-edge AI.",
            "requirements": "MS/PhD preferred, 2+ years AI research, Python, PyTorch",
            "location": "Bangalore, Karnataka",
            "work_type": "onsite",
            "salary_min": 1800000,
            "salary_max": 2500000,
            "experience_years": 2,
            "source": "indeed",
            "source_url": "https://indeed.com/job/12351",
            "skills_required": "Python, PyTorch, Research, NLP, Computer Vision",
        },
        {
            "title": "Python Developer - Automation",
            "company": "TCS",
            "description": "Develop automation scripts and tools. Work on CI/CD pipelines, test automation, and infrastructure automation.",
            "requirements": "2-3 years Python, Selenium, Jenkins, Docker",
            "location": "Bangalore, Karnataka",
            "work_type": "onsite",
            "salary_min": 550000,
            "salary_max": 800000,
            "experience_years": 2,
            "source": "indeed",
            "source_url": "https://indeed.com/job/12352",
            "skills_required": "Python, Selenium, Jenkins, Docker, Ansible",
        },
        {
            "title": "Senior Software Engineer - Python",
            "company": "Goldman Sachs",
            "description": "Build financial systems and trading platforms. Work with high-frequency data and real-time processing.",
            "requirements": "5+ years Python, Finance domain, System design",
            "location": "Bangalore, Karnataka",
            "work_type": "onsite",
            "salary_min": 2500000,
            "salary_max": 4000000,
            "experience_years": 5,
            "source": "indeed",
            "source_url": "https://indeed.com/job/12353",
            "skills_required": "Python, Finance, C++, Low latency systems",
        },
        {
            "title": "AI Engineer - NLP",
            "company": "Zomato",
            "description": "Build NLP models for food recommendations, sentiment analysis, and chatbots.",
            "requirements": "3+ years NLP, Python, Transformers, BERT",
            "location": "Bangalore, Karnataka",
            "work_type": "onsite",
            "salary_min": 1500000,
            "salary_max": 2200000,
            "experience_years": 3,
            "source": "indeed",
            "source_url": "https://indeed.com/job/12354",
            "skills_required": "Python, NLP, Transformers, BERT, spaCy",
        },
    ]

    jobs = []
    base_date = datetime.utcnow()

    for i, job_data in enumerate(sample_jobs):
        job = Job(
            **job_data,
            job_type="full-time",
            salary_currency="INR",
            external_id=f"IND{12345 + i}",
            posted_date=base_date - timedelta(days=random.randint(1, 14)),
            expires_at=base_date + timedelta(days=random.randint(30, 60)),
            scraped_at=base_date - timedelta(hours=random.randint(1, 48)),
            match_score=random.uniform(0.65, 0.95),
            is_active="active",
        )
        db.add(job)
        jobs.append(job)

    db.commit()
    print(f"✅ Created {len(jobs)} sample jobs")
    return jobs


def create_sample_resumes(db: Session, user: User) -> list[Resume]:
    """Create sample resumes"""
    print("\nCreating sample resumes...")

    resumes = []

    # Base resume
    base_resume = Resume(
        user_id=user.id,
        name="Base Resume - Software Engineer",
        version="v1.0",
        resume_type=ResumeType.BASE,
        file_format=ResumeFormat.PDF,
        file_path="/data/resumes/base_resume.pdf",
        storage_provider="local",
        content_text="Experienced Software Engineer with 3+ years in Python development...",
        is_active=True,
        is_default=True,
        usage_count="0",
    )
    db.add(base_resume)
    resumes.append(base_resume)

    # Tailored resume for AI role
    tailored_resume = Resume(
        user_id=user.id,
        name="AI Engineer Resume",
        version="v1.1",
        resume_type=ResumeType.TAILORED,
        file_format=ResumeFormat.PDF,
        file_path="/data/resumes/ai_engineer_resume.pdf",
        storage_provider="local",
        content_text="AI/ML Engineer specializing in deep learning and NLP...",
        tailored_for_title="AI Engineer",
        tailored_for_company="Tech Company",
        tailoring_model="claude-3.5-sonnet",
        changes_made="Enhanced AI/ML experience, added relevant projects",
        is_active=True,
        is_default=False,
        usage_count="3",
        based_on_resume_id=None,  # Will set after base_resume is committed
    )
    db.add(tailored_resume)
    resumes.append(tailored_resume)

    db.commit()

    # Update the relationship
    tailored_resume.based_on_resume_id = base_resume.id
    db.commit()

    print(f"✅ Created {len(resumes)} sample resumes")
    return resumes


def create_sample_applications(db: Session, user: User, jobs: list[Job], resumes: list[Resume]) -> list[Application]:
    """Create sample applications"""
    print("\nCreating sample applications...")

    applications = []
    base_date = datetime.utcnow()

    statuses = [
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.VIEWED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.INTERVIEW,
    ]

    # Create 5 applications
    for i in range(5):
        app = Application(
            job_id=jobs[i].id,
            user_id=user.id,
            resume_id=resumes[0].id,
            status=statuses[i],
            resume_version="Base Resume v1.0",
            applied_at=base_date - timedelta(days=random.randint(1, 10)),
            application_method="indeed",
            automated=False,
            notes=f"Sample application {i+1}",
        )

        if statuses[i] == ApplicationStatus.VIEWED:
            app.response_received = True
            app.response_received_at = base_date - timedelta(days=random.randint(1, 5))
        elif statuses[i] == ApplicationStatus.REJECTED:
            app.response_received = True
            app.response_received_at = base_date - timedelta(days=2)
            app.rejection_date = base_date - timedelta(days=2)
            app.rejection_reason = "Position filled"
        elif statuses[i] == ApplicationStatus.INTERVIEW:
            app.response_received = True
            app.response_received_at = base_date - timedelta(days=3)
            app.interview_date = base_date + timedelta(days=2)

        db.add(app)
        applications.append(app)

    db.commit()
    print(f"✅ Created {len(applications)} sample applications")
    return applications


def main():
    """Main function to create all sample data"""
    print("=" * 60)
    print("Creating Sample Data for Job Automation System")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Create sample data
        user = create_sample_user(db)
        jobs = create_sample_jobs(db)
        resumes = create_sample_resumes(db, user)
        applications = create_sample_applications(db, user, jobs, resumes)

        print("\n" + "=" * 60)
        print("✅ Sample data creation completed!")
        print("=" * 60)
        print(f"\nCreated:")
        print(f"  - 1 User: {user.email}")
        print(f"  - {len(jobs)} Job Postings")
        print(f"  - {len(resumes)} Resumes")
        print(f"  - {len(applications)} Applications")
        print(f"\nYou can now test the system with this data!")
        print(f"\nLogin credentials:")
        print(f"  Email: test@example.com")
        print(f"  Password: test123456")

    except Exception as e:
        print(f"\n❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
