import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

# Loads backend/.env no matter where the app is started from
# Variables already set on the machine win, so a deployed server can set its own
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Gmail SMTP settings, see .env.example
# GMAIL_ADDRESS is the team Gmail account the codes are sent from
# GMAIL_APP_PASSWORD is a 16 character app password, NOT the account's normal password
GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 465

# The values in .env.example, so a copied but unfilled .env still falls back to printing
PLACEHOLDER_ADDRESS = "your-team-address@gmail.com"
PLACEHOLDER_PASSWORD = "your-16-character-app-password"


# Returns (address, app_password) if real Gmail credentials are set, otherwise None
def get_gmail_credentials():
    address = os.environ.get("GMAIL_ADDRESS", "").strip()
    password = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
    if not address or not password:
        return None
    if address == PLACEHOLDER_ADDRESS or password == PLACEHOLDER_PASSWORD.replace(" ", ""):
        return None
    return address, password


# Sends an email through Gmail
# If no Gmail account is set up yet, it just prints the email in the terminal running flask
# so we can test without an email account
# Raises an exception if Gmail rejects the email
def send_email(to, subject, body):
    credentials = get_gmail_credentials()
    if credentials is None:
        print(f"\n----- EMAIL to {to} -----\nSubject: {subject}\n\n{body}\n-------------------------\n")
        return

    address, password = credentials
    msg = EmailMessage()
    msg["From"] = f"LionLift <{address}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT, timeout=10) as server:
        server.login(address, password)
        server.send_message(msg)
