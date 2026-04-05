"""
Execute Approved Email Actions
"""

import smtplib
import os
import re
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Configuration
SMTP_SERVER = os.getenv('GMAIL_SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('GMAIL_SMTP_PORT', 587))
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
VAULT_PATH = Path('AI_Employee_Vault')

print("=" * 60)
print("Execute Approved Email Actions")
print("=" * 60)
print()

# Check credentials
if not GMAIL_USER or not GMAIL_PASSWORD:
    print("[ERROR] Gmail credentials not configured in .env")
    exit(1)

# Find approved approval requests
approved_folder = VAULT_PATH / 'Approved'
approval_files = list(approved_folder.glob('APPROVAL_*.md'))

if not approval_files:
    print("[INFO] No approved actions to execute")
    exit(0)

print(f"[INFO] Found {len(approval_files)} approved action(s)")
print()

executed = 0
failed = 0

for approval_file in approval_files:
    print(f"[PROCESSING] {approval_file.name}")
    
    try:
        content = approval_file.read_text(encoding='utf-8')
        
        # Check if it's an email action
        if 'action: send_email' not in content:
            print(f"  [SKIP] Not an email action")
            continue
        
        # Extract email details
        to_match = re.search(r'\*\*To:\*\* (.+)', content)
        subject_match = re.search(r'\*\*Subject:\*\* (.+)', content)
        body_match = re.search(r'\*\*Body:\*\*\s*```\s*(.+?)```', content, re.DOTALL)
        
        if not to_match or not subject_match or not body_match:
            print(f"  [ERROR] Could not extract email details")
            failed += 1
            continue
        
        to_email = to_match.group(1).strip()
        subject = subject_match.group(1).strip()
        body = body_match.group(1).strip()
        
        print(f"  [OK] Extracted email details:")
        print(f"       To: {to_email}")
        print(f"       Subject: {subject}")
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print(f"  [INFO] Sending email...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"  [OK] Email sent successfully!")
        
        # Move to Done folder
        done_folder = VAULT_PATH / 'Done'
        done_folder.mkdir(exist_ok=True)
        approval_file.rename(done_folder / approval_file.name)
        print(f"  [OK] Moved to Done folder")
        
        executed += 1
        
    except Exception as e:
        print(f"  [ERROR] Failed: {e}")
        failed += 1
    
    print()

print("=" * 60)
print("Execution Summary")
print("=" * 60)
print(f"  Executed: {executed}")
print(f"  Failed: {failed}")
print()

if executed > 0:
    print("🎉 Email actions completed successfully!")
else:
    print("No email actions were executed.")
