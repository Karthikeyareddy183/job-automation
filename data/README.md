# Data Storage

Local data storage directories (excluded from git).

## Directory Structure

### `/resumes`
Stores generated resume versions:
- Base resumes uploaded by user
- AI-tailored resume variants
- Naming convention: `{job_id}_{timestamp}.pdf`

### `/templates`
Resume and cover letter templates:
- `.docx` templates for customization
- Jinja2 templates for dynamic content
- Brand/style variations

### `/logs`
Application logs:
- `scraper.log` - Job scraping activity
- `applications.log` - Application submissions
- `errors.log` - Error tracking
- `celery.log` - Background task logs

**Note**: Add `/data` to `.gitignore` to prevent committing sensitive data.
