"""
Indeed job scraper using Playwright
"""
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser
from services.scraper import BaseScraper
from datetime import datetime
import asyncio
import re


class IndeedScraper(BaseScraper):
    """Scraper for Indeed.com"""

    def __init__(self, keywords: List[str], location: str, max_pages: int = 3):
        super().__init__(keywords, location, max_pages)
        self.base_url = "https://www.indeed.co.in"

    def build_search_url(self, page: int = 0) -> str:
        """
        Build Indeed search URL

        Args:
            page: Page number (starts at 0, increments by 10)

        Returns:
            Full search URL
        """
        # Join keywords with spaces
        query = " ".join(self.keywords)

        # Build URL
        url = f"{self.base_url}/jobs?q={query.replace(' ', '+')}&l={self.location.replace(' ', '+')}"

        if page > 0:
            url += f"&start={page * 10}"

        return url

    async def scrape_jobs(self) -> List[Dict]:
        """
        Scrape jobs from Indeed

        Returns:
            List of job dictionaries
        """
        print(f"\n🔍 Starting Indeed scraper...")
        print(f"   Keywords: {', '.join(self.keywords)}")
        print(f"   Location: {self.location}")
        print(f"   Max pages: {self.max_pages}")

        async with async_playwright() as p:
            # Launch browser (headless mode for production)
            browser = await p.chromium.launch(headless=False)  # Set to True for production
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()

            try:
                for page_num in range(self.max_pages):
                    url = self.build_search_url(page_num)
                    print(f"\n📄 Scraping page {page_num + 1}: {url}")

                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(2)  # Wait for dynamic content

                    # Extract job listings
                    jobs_on_page = await self.extract_jobs_from_page(page)
                    self.jobs_scraped.extend(jobs_on_page)

                    print(f"   ✅ Found {len(jobs_on_page)} jobs on this page")

                    # Check if there's a next page
                    has_next = await self.has_next_page(page)
                    if not has_next:
                        print("   ℹ️ No more pages available")
                        break

            except Exception as e:
                print(f"   ❌ Error during scraping: {e}")
            finally:
                await browser.close()

        print(f"\n✅ Scraping complete! Total jobs found: {len(self.jobs_scraped)}")
        return self.jobs_scraped

    async def extract_jobs_from_page(self, page: Page) -> List[Dict]:
        """Extract job listings from current page"""
        jobs = []

        try:
            # Wait for job cards to load
            await page.wait_for_selector(".job_seen_beacon, .jobsearch-ResultsList", timeout=10000)

            # Get all job cards
            job_cards = await page.query_selector_all(".job_seen_beacon")

            if not job_cards:
                # Try alternative selector
                job_cards = await page.query_selector_all("[class*='jobsearch-SerpJobCard']")

            for card in job_cards:
                try:
                    job_data = await self.parse_job_card(card, page)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    print(f"      ⚠️ Error parsing job card: {e}")
                    continue

        except Exception as e:
            print(f"   ⚠️ Error extracting jobs: {e}")

        return jobs

    async def parse_job_card(self, card, page: Page) -> Optional[Dict]:
        """Parse a single job card"""
        try:
            # Extract job title
            title_elem = await card.query_selector("h2.jobTitle a, .jobTitle span")
            title = await title_elem.inner_text() if title_elem else None

            if not title:
                return None

            # Extract company
            company_elem = await card.query_selector("[data-testid='company-name'], .companyName")
            company = await company_elem.inner_text() if company_elem else "Unknown"

            # Extract location
            location_elem = await card.query_selector("[data-testid='text-location'], .companyLocation")
            location = await location_elem.inner_text() if location_elem else self.location

            # Extract job URL
            link_elem = await card.query_selector("h2.jobTitle a")
            job_url = None
            if link_elem:
                href = await link_elem.get_attribute("href")
                job_url = f"{self.base_url}{href}" if href and href.startswith("/") else href

            # Extract job key/ID from URL or data attribute
            job_id = None
            if job_url:
                match = re.search(r'jk=([a-zA-Z0-9]+)', job_url)
                if match:
                    job_id = match.group(1)

            # Extract salary if available
            salary_elem = await card.query_selector("[data-testid='attribute_snippet_testid'], .salary-snippet")
            salary_text = await salary_elem.inner_text() if salary_elem else ""
            salary_min, salary_max = self.extract_salary(salary_text)

            # Extract snippet/description
            snippet_elem = await card.query_selector(".job-snippet, [data-testid='job-snippet']")
            snippet = await snippet_elem.inner_text() if snippet_elem else ""

            # Determine work type from description
            work_type = self.determine_work_type(f"{title} {snippet}".lower())

            # Extract experience years
            experience_years = self.extract_experience_years(f"{title} {snippet}")

            # Build job data
            job_data = {
                "title": self.clean_text(title),
                "company": self.clean_text(company),
                "location": self.clean_text(location),
                "description": self.clean_text(snippet),
                "requirements": self.clean_text(snippet),  # Initial snippet, will get full desc later
                "source": "indeed",
                "source_url": job_url or f"{self.base_url}/jobs",
                "external_id": job_id or f"IND_{datetime.utcnow().timestamp()}",
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_currency": "INR",
                "work_type": work_type,
                "experience_years": experience_years,
                "job_type": "full-time",
                "scraped_at": datetime.utcnow(),
                "match_score": 0.0,  # Will be calculated by matching engine
                "is_active": "active",
            }

            return job_data

        except Exception as e:
            print(f"      ⚠️ Error parsing job card details: {e}")
            return None

    def parse_job_listing(self, job_element) -> Optional[Dict]:
        """Required by base class - implemented in parse_job_card"""
        pass

    def determine_work_type(self, text: str) -> str:
        """Determine work type from job description"""
        if "remote" in text or "work from home" in text or "wfh" in text:
            return "remote"
        elif "hybrid" in text:
            return "hybrid"
        else:
            return "onsite"

    async def has_next_page(self, page: Page) -> bool:
        """Check if there's a next page available"""
        try:
            # Look for pagination next button
            next_button = await page.query_selector("a[data-testid='pagination-page-next'], a[aria-label='Next']")
            return next_button is not None
        except:
            return False


async def main():
    """Test the Indeed scraper"""
    scraper = IndeedScraper(
        keywords=["Software Engineer", "Python"],
        location="Bangalore",
        max_pages=2
    )

    jobs = await scraper.scrape_jobs()

    print("\n" + "=" * 60)
    print("SCRAPING RESULTS")
    print("=" * 60)

    for i, job in enumerate(jobs[:5], 1):  # Show first 5 jobs
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Salary: {job['salary_min'] or 'N/A'} - {job['salary_max'] or 'N/A'}")
        print(f"   URL: {job['source_url']}")

    print(f"\n✅ Total jobs scraped: {len(jobs)}")


if __name__ == "__main__":
    asyncio.run(main())
