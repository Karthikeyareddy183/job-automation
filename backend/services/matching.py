"""
Job matching engine to score jobs against user preferences
"""
from typing import Dict, List
import json
import re


class JobMatcher:
    """Match and score jobs against user preferences"""

    def __init__(
        self,
        target_titles: List[str],
        target_locations: List[str],
        keywords: List[str],
        excluded_keywords: List[str] = None,
        min_salary: int = None,
        work_type_preference: str = "any",
    ):
        """
        Initialize job matcher

        Args:
            target_titles: List of desired job titles
            target_locations: List of preferred locations
            keywords: List of must-have keywords
            excluded_keywords: List of keywords to avoid
            min_salary: Minimum acceptable salary
            work_type_preference: remote/hybrid/onsite/any
        """
        self.target_titles = [t.lower() for t in target_titles]
        self.target_locations = [l.lower() for l in target_locations]
        self.keywords = [k.lower() for k in keywords]
        self.excluded_keywords = [k.lower() for k in (excluded_keywords or [])]
        self.min_salary = min_salary
        self.work_type_preference = work_type_preference.lower()

    def calculate_match_score(self, job: Dict) -> float:
        """
        Calculate match score for a job (0.0 to 1.0)

        Args:
            job: Job dictionary with title, description, requirements, etc.

        Returns:
            Match score between 0.0 and 1.0
        """
        scores = []
        weights = []

        # Title match (weight: 30%)
        title_score = self._score_title(job.get("title", ""))
        scores.append(title_score)
        weights.append(0.30)

        # Keyword match (weight: 35%)
        keyword_score = self._score_keywords(job)
        scores.append(keyword_score)
        weights.append(0.35)

        # Location match (weight: 15%)
        location_score = self._score_location(job.get("location", ""))
        scores.append(location_score)
        weights.append(0.15)

        # Salary match (weight: 10%)
        salary_score = self._score_salary(job.get("salary_min"), job.get("salary_max"))
        scores.append(salary_score)
        weights.append(0.10)

        # Work type match (weight: 10%)
        work_type_score = self._score_work_type(job.get("work_type", "onsite"))
        scores.append(work_type_score)
        weights.append(0.10)

        # Check for excluded keywords (automatic rejection)
        if self._has_excluded_keywords(job):
            return 0.0

        # Calculate weighted average
        total_score = sum(score * weight for score, weight in zip(scores, weights))

        return round(total_score, 2)

    def _score_title(self, title: str) -> float:
        """Score job title match"""
        if not title:
            return 0.0

        title_lower = title.lower()

        # Exact match
        for target in self.target_titles:
            if target in title_lower:
                return 1.0

        # Partial match
        title_words = set(title_lower.split())
        for target in self.target_titles:
            target_words = set(target.split())
            overlap = len(title_words & target_words)
            if overlap > 0:
                return overlap / len(target_words)

        return 0.0

    def _score_keywords(self, job: Dict) -> float:
        """Score keyword match in description and requirements"""
        if not self.keywords:
            return 1.0  # No keywords required

        # Combine title, description, requirements, and skills
        text = " ".join([
            job.get("title", ""),
            job.get("description", ""),
            job.get("requirements", ""),
            job.get("skills_required", ""),
        ]).lower()

        # Count keyword matches
        matches = 0
        for keyword in self.keywords:
            if keyword in text:
                matches += 1

        # Return percentage of keywords matched
        return matches / len(self.keywords)

    def _score_location(self, location: str) -> float:
        """Score location match"""
        if not location:
            return 0.5

        location_lower = location.lower()

        # Check for remote
        if any(loc in ["remote", "anywhere"] for loc in self.target_locations):
            if "remote" in location_lower or "work from home" in location_lower:
                return 1.0

        # Exact location match
        for target_loc in self.target_locations:
            if target_loc in location_lower:
                return 1.0

        # Partial match
        return 0.3

    def _score_salary(self, salary_min: int, salary_max: int) -> float:
        """Score salary match"""
        if not self.min_salary:
            return 1.0  # No salary requirement

        if not salary_min and not salary_max:
            return 0.5  # Unknown salary, neutral score

        # Check if job meets minimum salary
        job_salary = salary_max or salary_min

        if job_salary >= self.min_salary:
            return 1.0
        elif job_salary >= self.min_salary * 0.8:
            return 0.7  # Within 80% of target
        elif job_salary >= self.min_salary * 0.6:
            return 0.4  # Within 60% of target
        else:
            return 0.0

    def _score_work_type(self, work_type: str) -> float:
        """Score work type match"""
        if self.work_type_preference == "any":
            return 1.0

        if not work_type:
            return 0.5

        if work_type.lower() == self.work_type_preference:
            return 1.0

        # Partial credit for flexible arrangements
        if self.work_type_preference == "remote" and work_type.lower() == "hybrid":
            return 0.6
        elif self.work_type_preference == "hybrid":
            return 0.7  # Hybrid is somewhat flexible

        return 0.3

    def _has_excluded_keywords(self, job: Dict) -> bool:
        """Check if job contains excluded keywords"""
        if not self.excluded_keywords:
            return False

        text = " ".join([
            job.get("title", ""),
            job.get("description", ""),
            job.get("requirements", ""),
        ]).lower()

        for excluded in self.excluded_keywords:
            if excluded in text:
                return True

        return False

    def filter_jobs(self, jobs: List[Dict], min_score: float = 0.70) -> List[Dict]:
        """
        Filter and score jobs

        Args:
            jobs: List of job dictionaries
            min_score: Minimum match score threshold

        Returns:
            List of jobs with scores >= min_score, sorted by score
        """
        scored_jobs = []

        for job in jobs:
            score = self.calculate_match_score(job)
            job["match_score"] = score

            if score >= min_score:
                scored_jobs.append(job)

        # Sort by score (highest first)
        scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)

        return scored_jobs

    @staticmethod
    def from_user(user) -> "JobMatcher":
        """
        Create JobMatcher from User model

        Args:
            user: User model instance

        Returns:
            JobMatcher instance
        """
        return JobMatcher(
            target_titles=json.loads(user.target_titles or "[]"),
            target_locations=json.loads(user.target_locations or "[]"),
            keywords=json.loads(user.keywords or "[]"),
            excluded_keywords=json.loads(user.excluded_keywords or "[]"),
            min_salary=int(user.min_salary) if user.min_salary else None,
            work_type_preference=user.work_type_preference or "any",
        )


def test_matcher():
    """Test the job matcher"""
    matcher = JobMatcher(
        target_titles=["Software Engineer", "Python Developer"],
        target_locations=["Bangalore", "Remote"],
        keywords=["Python", "AI", "FastAPI"],
        excluded_keywords=["Java only"],
        min_salary=500000,
        work_type_preference="onsite",
    )

    # Test jobs
    test_jobs = [
        {
            "title": "Software Engineer - Python/AI",
            "company": "Tech Corp",
            "description": "Build AI applications using Python and FastAPI",
            "requirements": "3+ years Python, AI/ML experience",
            "location": "Bangalore",
            "salary_min": 800000,
            "salary_max": 1200000,
            "work_type": "onsite",
            "skills_required": "Python, AI, FastAPI",
        },
        {
            "title": "Java Developer",
            "company": "Other Corp",
            "description": "Java only position, no Python",
            "requirements": "5+ years Java",
            "location": "Bangalore",
            "salary_min": 1000000,
            "salary_max": 1500000,
            "work_type": "onsite",
            "skills_required": "Java, Spring",
        },
        {
            "title": "Frontend Developer",
            "company": "Web Co",
            "description": "React and JavaScript development",
            "requirements": "2+ years React",
            "location": "Mumbai",
            "salary_min": 600000,
            "salary_max": 900000,
            "work_type": "remote",
            "skills_required": "React, JavaScript",
        },
    ]

    print("Testing Job Matcher\n" + "=" * 60)

    for job in test_jobs:
        score = matcher.calculate_match_score(job)
        print(f"\nJob: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Match Score: {score:.2f}")
        print(f"Status: {'✅ MATCH' if score >= 0.70 else '❌ NO MATCH'}")

    print("\n" + "=" * 60)
    print("Filtering jobs with min_score=0.70")
    matched_jobs = matcher.filter_jobs(test_jobs, min_score=0.70)
    print(f"Matched {len(matched_jobs)} out of {len(test_jobs)} jobs")


if __name__ == "__main__":
    test_matcher()
