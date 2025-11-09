"""
Test script to scrape Indeed, match jobs, and save to database
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from services.indeed_scraper import IndeedScraper
from services.matching import JobMatcher
from models.job import Job
from db.session import SessionLocal
from datetime import datetime


async def scrape_and_save_jobs(
    keywords: list[str],
    location: str,
    min_salary: int = None,
    max_pages: int = 2,
    min_match_score: float = 0.70
):
    """
    Scrape jobs from Indeed, match them, and save to database

    Args:
        keywords: List of search keywords
        location: Location to search
        min_salary: Minimum salary requirement
        max_pages: Number of pages to scrape
        min_match_score: Minimum match score to save job
    """
    print("\n" + "=" * 70)
    print(" JOB SCRAPER & MATCHER TEST")
    print("=" * 70)

    # Step 1: Scrape jobs
    print("\n📥 STEP 1: Scraping jobs from Indeed...")
    print("-" * 70)

    scraper = IndeedScraper(
        keywords=keywords,
        location=location,
        max_pages=max_pages
    )

    jobs = await scraper.scrape_jobs()

    if not jobs:
        print("\n❌ No jobs found. Try different keywords or location.")
        return

    print(f"\n✅ Scraped {len(jobs)} jobs from Indeed")

    # Step 2: Match jobs
    print("\n🎯 STEP 2: Matching jobs against preferences...")
    print("-" * 70)

    matcher = JobMatcher(
        target_titles=["Software Engineer", "Python Developer", "AI Engineer"],
        target_locations=[location, "Remote"],
        keywords=keywords,
        excluded_keywords=["Java only", "C++ only"],
        min_salary=min_salary,
        work_type_preference="onsite"
    )

    matched_jobs = matcher.filter_jobs(jobs, min_score=min_match_score)

    print(f"✅ Matched {len(matched_jobs)} jobs (score >= {min_match_score})")

    # Step 3: Save to database
    print("\n💾 STEP 3: Saving matched jobs to database...")
    print("-" * 70)

    db = SessionLocal()
    saved_count = 0
    skipped_count = 0

    try:
        for job_data in matched_jobs:
            # Check if job already exists
            existing_job = db.query(Job).filter(
                Job.source_url == job_data["source_url"]
            ).first()

            if existing_job:
                print(f"   ⏭️ Skipped (duplicate): {job_data['title']}")
                skipped_count += 1
                continue

            # Create Job model
            job = Job(
                title=job_data["title"],
                company=job_data["company"],
                description=job_data["description"],
                requirements=job_data["requirements"],
                location=job_data["location"],
                work_type=job_data["work_type"],
                salary_min=job_data.get("salary_min"),
                salary_max=job_data.get("salary_max"),
                salary_currency=job_data.get("salary_currency", "INR"),
                experience_years=job_data.get("experience_years"),
                job_type=job_data.get("job_type", "full-time"),
                source="indeed",
                source_url=job_data["source_url"],
                external_id=job_data["external_id"],
                scraped_at=datetime.utcnow(),
                match_score=job_data["match_score"],
                is_active="active",
                skills_required=job_data.get("skills_required", ""),
            )

            db.add(job)
            saved_count += 1
            print(f"   ✅ Saved: {job.title} (Score: {job.match_score:.2f})")

        db.commit()
        print(f"\n✅ Saved {saved_count} jobs to database")
        if skipped_count > 0:
            print(f"   ⏭️  Skipped {skipped_count} duplicate jobs")

    except Exception as e:
        print(f"\n❌ Error saving to database: {e}")
        db.rollback()
    finally:
        db.close()

    # Step 4: Display summary
    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    print(f"  📊 Total scraped: {len(jobs)}")
    print(f"  🎯 Jobs matched: {len(matched_jobs)}")
    print(f"  💾 Saved to DB: {saved_count}")
    print(f"  ⏭️  Duplicates: {skipped_count}")

    # Show top 5 matches
    if matched_jobs:
        print(f"\n🏆 TOP {min(5, len(matched_jobs))} MATCHES:")
        print("-" * 70)
        for i, job in enumerate(matched_jobs[:5], 1):
            print(f"\n{i}. {job['title']} at {job['company']}")
            print(f"   📍 {job['location']}")
            print(f"   💰 Salary: ₹{job.get('salary_min', 'N/A')} - ₹{job.get('salary_max', 'N/A')}")
            print(f"   🎯 Match Score: {job['match_score']:.2f}")
            print(f"   🔗 {job['source_url']}")

    print("\n" + "=" * 70)


async def main():
    """Main test function"""
    # Test configuration matching your preferences
    await scrape_and_save_jobs(
        keywords=["Software Engineer", "Python", "AI"],
        location="Bangalore",
        min_salary=500000,
        max_pages=2,  # Start with 2 pages for testing
        min_match_score=0.70
    )


if __name__ == "__main__":
    asyncio.run(main())
