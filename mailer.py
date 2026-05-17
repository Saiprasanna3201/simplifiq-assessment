import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def build_email_body(lead, enriched=None):
    """Build a personalized HTML email body."""
    name = lead.get("name", "there")
    company = lead.get("company", "your company")
    return f"""
    <html><body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto;">
      <div style="background: #0F6E56; padding: 24px 28px; border-radius: 8px 8px 0 0;">
        <h2 style="color: white; margin: 0;">Your personalised company audit is ready</h2>
      </div>
      <div style="background: #f9f9f9; padding: 24px 28px; border-radius: 0 0 8px 8px; border: 1px solid #eee; border-top: none;">
        <p>Hi {name},</p>
        <p>Thank you for your interest in <strong>SimplifIQ</strong>. We've reviewed <strong>{company}</strong> 
        and prepared a personalised audit report highlighting your key opportunities and how our solutions 
        can help streamline your operations.</p>
        <p>Your full report is attached to this email as a PDF.</p>
        <p style="margin-top: 24px; padding: 16px; background: #E1F5EE; border-left: 4px solid #0F6E56; border-radius: 0 6px 6px 0;">
          <strong>What's inside your report:</strong><br>
          &nbsp;&nbsp;• Company overview &amp; industry analysis<br>
          &nbsp;&nbsp;• Identified pain points specific to your business<br>
          &nbsp;&nbsp;• Tailored SimplifIQ solution recommendations<br>
          &nbsp;&nbsp;• Key insight from our research
        </p>
        <p>If you have any questions or would like to discuss the findings, simply reply to this email — 
        we'd love to connect.</p>
        <p style="margin-top: 24px;">Warm regards,<br>
        <strong>The SimplifIQ Team</strong><br>
        <span style="color: #888; font-size: 13px;">hello@simplifiq.com</span></p>
      </div>
      <p style="text-align: center; font-size: 11px; color: #bbb; margin-top: 16px;">
        SimplifIQ · Automating tomorrow's businesses today
      </p>
    </body></html>
    """


def send_email(lead, pdf_path):
    """Send the PDF report to the prospect via SMTP."""
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or not smtp_pass:
        raise ValueError("SMTP credentials not configured in .env")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your personalised audit report — {lead['company']}"
    msg["From"]    = f"SimplifIQ <{smtp_user}>"
    msg["To"]      = lead["email"]

    # HTML body
    html_body = build_email_body(lead)
    msg.attach(MIMEText(html_body, "html"))

    # Attach PDF
    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    filename = os.path.basename(pdf_path)
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    msg.attach(part)

    # Send
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, lead["email"], msg.as_string())

    print(f"  Email sent to {lead['email']}")
