import os
import mimetypes
import logging
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD
from typing import List, Optional
from email_validator import validate_email, EmailNotValidError
import re

# -------------------------------
# Setup logging
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# -------------------------------
# Email Validation (@something.com)
# -------------------------------
def validate_and_normalize_email(email: str) -> str:
    """
    Validate and normalize an email address.
    Only allows addresses like something@domain.com
    """
    try:
        valid = validate_email(email)
        normalized = valid.email.lower()  # normalize to lowercase

        # Regex: must be like @<one or more chars>.com
        if not re.match(r"^[^@]+@[a-zA-Z0-9-]+\.com$", normalized):
            raise ValueError("Email must be in the format: something@domain.com")

        return normalized
    except EmailNotValidError as e:
        raise ValueError(f"Invalid email: {str(e)}")

# -------------------------------
# Send Email with Attachments
# -------------------------------
async def send_email_with_attachment(
    to_email: str,
    subject: str,
    body: str,
    attachment_paths: Optional[List[str]] = None,
):
    # --- Step 1: Validate email ---
    to_email = validate_and_normalize_email(to_email)

    # --- Step 2: Build the email message ---
    msg = MIMEMultipart()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # --- Step 3: Add attachments (if any) ---
    if attachment_paths:
        for path in attachment_paths:
            if path and os.path.exists(path):
                mime_type, _ = mimetypes.guess_type(path)
                if mime_type is None:
                    mime_type = "application/octet-stream"
                main_type, sub_type = mime_type.split("/", 1)

                with open(path, "rb") as f:
                    part = MIMEBase(main_type, sub_type)
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(path)}"
                )
                msg.attach(part)
            else:
                logging.warning(f"Attachment not found: {path}")

    # --- Step 4: Send email with Gmail SMTP ---
    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=GMAIL_ADDRESS,
            password=GMAIL_APP_PASSWORD,
            timeout=30  # ⏱ Timeout to avoid hanging
        )
        logging.info(f"Email successfully sent to {to_email}")
    except Exception as e:
        logging.error(f"Email sending failed: {e}")
        raise
