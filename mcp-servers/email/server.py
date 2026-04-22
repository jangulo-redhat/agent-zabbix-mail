from fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText
import os

mcp = FastMCP("email")


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via SMTP."""
    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = os.environ["SMTP_FROM"]
    msg["To"] = to

    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", "587"))) as smtp:
        smtp.ehlo()
        if os.environ.get("SMTP_TLS", "true").lower() == "true":
            smtp.starttls()
        if os.environ.get("SMTP_USER"):
            smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(msg)

    return f"Email sent to {to}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)
