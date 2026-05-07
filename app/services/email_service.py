import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FRONTEND_URL


def send_reset_password_email(to_email: str, user_name: str, token: str) -> None:
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>Password Reset Request</h2>
        <p>Hi {user_name},</p>
        <p>We received a request to reset your password. Click the button below to set a new one:</p>
        <p style="margin: 24px 0;">
          <a href="{reset_link}"
             style="background:#4F46E5;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;">
            Reset Password
          </a>
        </p>
        <p>This link expires in <strong>30 minutes</strong>. If you did not request a password reset, you can safely ignore this email.</p>
        <hr/>
        <small style="color:#888;">If the button does not work, copy and paste this URL into your browser:<br/>{reset_link}</small>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset your password"
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_HOST, int(SMTP_PORT)) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
