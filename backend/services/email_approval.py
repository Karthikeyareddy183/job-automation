"""
Email Approval System - SendGrid integration for user approvals
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from config.settings import settings
import secrets
import logging

logger = logging.getLogger(__name__)


class EmailApprovalService:
    """
    Email approval service using SendGrid

    Handles:
    - Sending approval request emails
    - Generating magic link tokens
    - Processing approve/reject actions
    - Managing 24-hour timeouts
    """

    def __init__(self):
        self.sendgrid_api_key = settings.SENDGRID_API_KEY
        self.notification_email = settings.NOTIFICATION_EMAIL
        self.frontend_url = settings.VITE_API_BASE_URL.replace("8000", "5173")  # Default Vite port

    async def send_approval_request(
        self,
        user_email: str,
        user_id: str,
        application_id: str,
        job: Dict[str, Any],
        tailored_resume: str,
        match_score: float,
        reasoning: str
    ) -> Dict[str, Any]:
        """
        Send approval request email to user

        Args:
            user_email: User's email address
            user_id: User ID
            application_id: Application ID
            job: Job dictionary
            tailored_resume: Tailored resume content
            match_score: Match score (0.0 - 1.0)
            reasoning: Why agent recommended this job

        Returns:
            Approval request details
        """
        try:
            # Generate approval token
            approval_token = self._generate_approval_token()

            # Calculate expiry (24 hours from now)
            expires_at = datetime.utcnow() + timedelta(hours=24)

            # Build email content
            email_content = self._build_approval_email(
                job=job,
                match_score=match_score,
                reasoning=reasoning,
                approval_token=approval_token
            )

            # Send email via SendGrid
            await self._send_email_sendgrid(
                to_email=user_email,
                subject=f"Approval Needed: {job.get('title')} at {job.get('company')}",
                html_content=email_content
            )

            # Create approval request record (caller will save to DB)
            approval_request = {
                "application_id": application_id,
                "user_id": user_id,
                "job_id": job.get("id"),
                "sent_at": datetime.utcnow(),
                "expires_at": expires_at,
                "status": "pending",
                "approval_token": approval_token,
                "agent_reasoning": reasoning
            }

            logger.info(f"Approval request sent to {user_email} for job {job.get('id')}")
            return approval_request

        except Exception as e:
            logger.error(f"Failed to send approval request: {e}")
            raise

    async def _send_email_sendgrid(self, to_email: str, subject: str, html_content: str):
        """
        Send email using SendGrid API

        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML email content
        """
        try:
            if not self.sendgrid_api_key:
                logger.warning("SendGrid API key not configured. Skipping email send.")
                # For testing, just log the email
                logger.info(f"[TEST EMAIL] To: {to_email}, Subject: {subject}")
                return

            # Import SendGrid
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=self.notification_email or "noreply@jobautomation.com",
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )

            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)

            logger.info(f"Email sent successfully. Status code: {response.status_code}")

        except Exception as e:
            logger.error(f"SendGrid email failed: {e}")
            raise

    def _build_approval_email(
        self,
        job: Dict,
        match_score: float,
        reasoning: str,
        approval_token: str
    ) -> str:
        """
        Build HTML email content for approval request

        Args:
            job: Job dictionary
            match_score: Match score
            reasoning: Agent reasoning
            approval_token: Approval token

        Returns:
            HTML email content
        """
        job_title = job.get("title", "Unknown")
        job_company = job.get("company", "Unknown")
        job_location = job.get("location", "Unknown")
        job_salary = job.get("salary_range", "Not specified")
        job_description = job.get("description", "")[:500] + "..."
        job_url = job.get("url", "#")

        # Build approval/reject URLs
        approve_url = f"{self.frontend_url}/approve/{approval_token}?action=approve"
        reject_url = f"{self.frontend_url}/approve/{approval_token}?action=reject"

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .job-details {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }}
        .match-score {{
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            display: inline-block;
            font-weight: bold;
            margin: 10px 0;
        }}
        .reasoning {{
            background: #fff9e6;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }}
        .buttons {{
            text-align: center;
            margin: 30px 0;
        }}
        .btn {{
            display: inline-block;
            padding: 15px 40px;
            margin: 10px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
            transition: all 0.3s;
        }}
        .btn-approve {{
            background: #10b981;
            color: white;
        }}
        .btn-approve:hover {{
            background: #059669;
        }}
        .btn-reject {{
            background: #ef4444;
            color: white;
        }}
        .btn-reject:hover {{
            background: #dc2626;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
        .expiry {{
            background: #fee2e2;
            padding: 10px;
            border-radius: 5px;
            color: #991b1b;
            text-align: center;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Job Application Approval Needed</h1>
    </div>

    <div class="content">
        <p>Hi there!</p>

        <p>I've found a great job match for you and tailored your resume. Please review and approve the application.</p>

        <div class="job-details">
            <h2>{job_title}</h2>
            <p><strong>Company:</strong> {job_company}</p>
            <p><strong>Location:</strong> {job_location}</p>
            <p><strong>Salary:</strong> {job_salary}</p>
            <p><strong>Link:</strong> <a href="{job_url}" target="_blank">View Job Posting</a></p>

            <div class="match-score">
                Match Score: {match_score * 100:.0f}%
            </div>
        </div>

        <div class="reasoning">
            <h3>🎯 Why I recommend this job:</h3>
            <p>{reasoning}</p>
        </div>

        <h3>📄 Job Description (excerpt):</h3>
        <p style="background: white; padding: 15px; border-radius: 8px;">{job_description}</p>

        <div class="expiry">
            ⏰ This approval request expires in 24 hours. If no action is taken, I'll skip this application and move on.
        </div>

        <div class="buttons">
            <a href="{approve_url}" class="btn btn-approve">✅ Approve & Apply</a>
            <a href="{reject_url}" class="btn btn-reject">❌ Reject</a>
        </div>

        <p style="text-align: center; color: #666; font-size: 14px;">
            Click the buttons above to respond, or visit your dashboard to review the tailored resume.
        </p>
    </div>

    <div class="footer">
        <p>This is an automated message from your Job Application AI Agent</p>
        <p>Token expires: {(datetime.utcnow() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M UTC')}</p>
    </div>
</body>
</html>
"""

        return html

    def _generate_approval_token(self) -> str:
        """
        Generate secure approval token

        Returns:
            Random token string
        """
        return secrets.token_urlsafe(32)

    async def process_approval_response(
        self,
        approval_token: str,
        action: str,
        user_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user's approval/rejection

        Args:
            approval_token: Approval token from email
            action: 'approve' or 'reject'
            user_feedback: Optional feedback on rejection

        Returns:
            Processing result
        """
        try:
            # TODO: Fetch approval request from database by token
            # For now, return placeholder

            result = {
                "success": True,
                "action": action,
                "token": approval_token,
                "timestamp": datetime.utcnow().isoformat()
            }

            if action == "approve":
                logger.info(f"Application approved via token {approval_token[:8]}...")
                result["message"] = "Application approved. Proceeding with submission."
            elif action == "reject":
                logger.info(f"Application rejected via token {approval_token[:8]}...")
                result["message"] = "Application rejected. Agent will learn from this feedback."
                result["feedback"] = user_feedback

            return result

        except Exception as e:
            logger.error(f"Failed to process approval response: {e}")
            raise

    async def check_expired_approvals(self) -> List[str]:
        """
        Check for and mark expired approval requests

        Returns:
            List of expired approval request IDs
        """
        try:
            # TODO: Query database for approval requests with expires_at < now AND status = pending
            # Mark them as 'expired'

            logger.info("Checking for expired approval requests...")
            expired_ids = []  # Placeholder

            return expired_ids

        except Exception as e:
            logger.error(f"Failed to check expired approvals: {e}")
            return []


# Singleton instance
email_approval_service = EmailApprovalService()
