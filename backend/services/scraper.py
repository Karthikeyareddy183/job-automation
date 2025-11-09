"""
Base scraper class for job boards
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import re


class BaseScraper(ABC):
    """Abstract base class for job board scrapers"""

    def __init__(self, keywords: List[str], location: str, max_pages: int = 3):
        """
        Initialize scraper

        Args:
            keywords: List of keywords to search for
            location: Location to search in
            max_pages: Maximum number of pages to scrape
        """
        self.keywords = keywords
        self.location = location
        self.max_pages = max_pages
        self.jobs_scraped = []

    @abstractmethod
    async def scrape_jobs(self) -> List[Dict]:
        """
        Scrape jobs from the job board

        Returns:
            List of job dictionaries
        """
        pass

    @abstractmethod
    def parse_job_listing(self, job_element) -> Optional[Dict]:
        """
        Parse a single job listing

        Args:
            job_element: HTML element or data structure containing job info

        Returns:
            Dictionary with job data or None if parsing fails
        """
        pass

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

    def extract_salary(self, text: str) -> tuple[Optional[int], Optional[int]]:
        """
        Extract salary range from text

        Args:
            text: Text containing salary information

        Returns:
            Tuple of (min_salary, max_salary) in INR/year
        """
        if not text:
            return None, None

        text = text.lower()

        # Patterns for Indian salary formats
        patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lac|l)\s*-\s*₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lac|l)',
            r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakh)',
            r'₹\s*(\d+(?:,\d+)*)\s*-\s*₹?\s*(\d+(?:,\d+)*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    min_sal = float(match.group(1).replace(',', ''))
                    max_sal = float(match.group(2).replace(',', ''))

                    # Convert lakhs to full amount
                    if 'lakh' in text or 'lac' in text or 'lpa' in text:
                        min_sal = int(min_sal * 100000)
                        max_sal = int(max_sal * 100000)
                    else:
                        min_sal = int(min_sal)
                        max_sal = int(max_sal)

                    return min_sal, max_sal
                except (ValueError, AttributeError):
                    pass

        return None, None

    def extract_experience_years(self, text: str) -> Optional[int]:
        """
        Extract years of experience from text

        Args:
            text: Text containing experience information

        Returns:
            Number of years or None
        """
        if not text:
            return None

        # Patterns: "3+ years", "3-5 years", "3 yrs", etc.
        patterns = [
            r'(\d+)\s*\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*-\s*\d+\s*(?:years?|yrs?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    pass

        return None

    def build_search_url(self, base_url: str, page: int = 0) -> str:
        """
        Build search URL for the job board

        Args:
            base_url: Base URL of the job board
            page: Page number

        Returns:
            Full search URL
        """
        # To be implemented by subclasses
        pass

    def get_summary(self) -> Dict:
        """Get scraping summary statistics"""
        return {
            "total_jobs": len(self.jobs_scraped),
            "keywords": self.keywords,
            "location": self.location,
            "timestamp": datetime.utcnow().isoformat(),
        }
