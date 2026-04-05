"""
Test Email MCP Client - Send Test Email
"""

import smtplib
import os
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Email configuration
SMTP_SERVER = os.getenv('GMAIL_SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('GMAIL_SMTP_PORT', 587))
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

print("=" * 60)
print("Email MCP Client Test - Send Email via SMTP")
print("=" * 60)
print()

# Check credentials
if not GMAIL_USER:
    print("[ERROR] GMAIL_USER not set in .env")
    exit(1)
if not GMAIL_PASSWORD:
    print("[ERROR] GMAIL_APP_PASSWORD not set in .env")
    exit(1)

print(f"[OK] SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
print(f"[OK] From: {GMAIL_USER}")
print()

# Create test email
msg = MIMEMultipart()
msg['From'] = GMAIL_USER
msg['To'] = GMAIL_USER  # Send to self for testing
msg['Subject'] = '[TEST] AI Employee Email MCP Test'

body = """
Hello,

This is a test email from the AI Employee Email MCP Client.

If you receive this email, it means:
✓ Gmail SMTP authentication is working
✓ Email sending capability is functional
✓ The AI Employee can now send emails

---
Sent by: AI Employee FTE
Test Mode: Yes
"""

msg.attach(MIMEText(body, 'plain'))

# Send email
print("[INFO] Connecting to SMTP server...")
try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    print("[OK] Connected and secured with STARTTLS")
    
    print("[INFO] Logging in...")
    server.login(GMAIL_USER, GMAIL_PASSWORD)
    print("[OK] Logged in successfully")
    
    print("[INFO] Sending email...")
    server.send_message(msg)
    print("[OK] Email sent successfully!")
    
    server.quit()
    
    print()
    print("=" * 60)
    print("EMAIL TEST PASSED!")
    print("=" * 60)
    print()
    print(f"Check your inbox at {GMAIL_USER} for the test email.")
    print()
    print("Next steps:")
    print("  1. Verify you received the test email")
    print("  2. The Email MCP client is ready to use")
    print("  3. AI can now send emails via the approval workflow")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"[ERROR] SMTP Authentication failed: {e}")
    print()
    print("Possible causes:")
    print("  - Incorrect Gmail password (use App Password, not regular password)")
    print("  - 2FA not enabled on Google Account")
    print("  - App Password not generated correctly")
    print()
    print("To fix:")
    print("  1. Go to: https://myaccount.google.com/apppasswords")
    print("  2. Create a new app password for 'Mail'")
    print("  3. Update GMAIL_APP_PASSWORD in .env file")
except Exception as e:
    print(f"[ERROR] Failed to send email: {e}")
