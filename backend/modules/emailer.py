import smtplib, logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

logger = logging.getLogger(__name__)

def send_jobs_email(jobs: list, to_email: str):
    if not jobs:
        logger.info("No new jobs to email")
        return

    body_lines = [f"<h2>🆕 {len(jobs)} New Job(s) Found</h2>"]
    for j in jobs:
        match = j.get("match", {})
        body_lines.append(f"""
        <div style='margin-bottom:20px;border-bottom:1px solid #eee;padding-bottom:10px'>
          <strong>{j['title']}</strong> at {j['company']}<br>
          📍 {j['location']} | Match score: {match.get('score', 'N/A')}/100<br>
          <a href='{j['link']}'>View Job →</a>
        </div>""")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"<strong>{j.get('title', 'Unknown Role')}</strong> at {j.get('company', 'Unknown Company')}<br>"
    msg["From"] = settings.email_address
    msg["To"] = to_email
    msg.attach(MIMEText("".join(body_lines), "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.email_address, settings.email_password)
            server.sendmail(settings.email_address, to_email, msg.as_string())
        logger.info(f"Email sent to {to_email} with {len(jobs)} jobs")
    except Exception as e:
        logger.error(f"Email failed: {e}")
        raise