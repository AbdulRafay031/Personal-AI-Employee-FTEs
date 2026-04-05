"""
Simple Gmail Auth - Automatic Flow
Just run and complete browser authorization
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from pathlib import Path
import webbrowser
import time

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
credentials_path = Path('credentials.json')
token_path = Path('AI_Employee_Vault/token.json')

print("=" * 60)
print("Gmail API Authentication")
print("=" * 60)

# Check credentials
if not credentials_path.exists():
    print("\n[ERROR] credentials.json not found!")
    input("Press Enter to exit...")
    exit(1)

print("\n[OK] credentials.json found")

# Try existing token
creds = None
if token_path.exists():
    print("[INFO] Found existing token")
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds.valid:
            print("[OK] Token is valid")
        elif creds.expired and creds.refresh_token:
            print("[INFO] Refreshing expired token...")
            creds.refresh(Request())
            print("[OK] Token refreshed")
        else:
            print("[WARN] Token invalid, re-authorizing...")
            creds = None
    except Exception as e:
        print(f"[ERROR] Token error: {e}")
        creds = None

# New authorization
if not creds or not creds.valid:
    print("\n[INFO] Opening browser for authorization...")
    print("[INFO] Please complete the authorization in your browser")
    print("[INFO] After redirect, come back here - token will be saved automatically")
    
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    
    # Open browser automatically
    creds = flow.run_local_server(port=8080, open_browser=True)
    
    # Save token
    print("\n[INFO] Authorization successful!")
    print("[INFO] Saving token...")
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json())
    print(f"[OK] Token saved to: {token_path.absolute()}")

# Test Gmail API
print("\n" + "=" * 60)
print("Testing Gmail API")
print("=" * 60)

service = build('gmail', 'v1', credentials=creds)

# Get profile
profile = service.users().getProfile(userId='me').execute()
print(f"\n[OK] Connected to Gmail!")
print(f"     Account: {profile['emailAddress']}")
print(f"     Total Messages: {profile['messagesTotal']}")
print(f"     Total Threads: {profile['threadsTotal']}")

# Get recent unread messages
print("\n[INFO] Checking for unread messages...")
results = service.users().messages().list(userId='me', q='is:unread', maxResults=10).execute()
messages = results.get('messages', [])

if messages:
    print(f"[OK] Found {len(messages)} unread messages:")
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
        headers = msg_detail['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        print(f"\n     • From: {from_addr[:60]}")
        print(f"       Subject: {subject[:60]}")
else:
    print("[INFO] No unread messages")

# Get all recent messages
print("\n[INFO] Recent messages (all):")
results = service.users().messages().list(userId='me', maxResults=5).execute()
messages = results.get('messages', [])

for msg in messages:
    msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
    headers = msg_detail['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
    date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
    print(f"\n     • From: {from_addr[:50]}")
    print(f"       Subject: {subject[:50]}")
    print(f"       Date: {date[:30]}")

print("\n" + "=" * 60)
print("Gmail API Test COMPLETE!")
print("=" * 60)
print("\nToken saved. Future runs will use the saved token.")
print("\nYou can now run the Gmail watcher:")
print("  python watchers/gmail_watcher.py AI_Employee_Vault --credentials credentials.json")
input("\nPress Enter to exit...")
