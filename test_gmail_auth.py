"""
Simple Gmail Authentication Test Script
Run this to authenticate and test Gmail API
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pathlib import Path
import sys

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
credentials_path = Path('credentials.json')
token_path = Path('AI_Employee_Vault/token.json')

print("=" * 60)
print("Gmail API Authentication Test")
print("=" * 60)
print()

# Check credentials file
if not credentials_path.exists():
    print("[ERROR] credentials.json not found!")
    print("        Download from Google Cloud Console")
    sys.exit(1)

print("[OK] credentials.json found")

# Try to load existing token
creds = None
if token_path.exists():
    print("[INFO] Loading existing token...")
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds.valid:
            print("[OK] Token is valid")
        elif creds.expired and creds.refresh_token:
            print("[INFO] Token expired, refreshing...")
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            print("[OK] Token refreshed")
        else:
            print("[WARN] Token needs re-authentication")
            creds = None
    except Exception as e:
        print(f"[ERROR] Token error: {e}")
        creds = None

# Need new auth
if not creds or not creds.valid:
    print()
    print("[INFO] Starting OAuth authorization flow...")
    print("[STEP 1] Copy the URL below to your browser:")
    print()
    
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    
    # Get authorization URL manually
    auth_url, _ = flow.authorization_url(prompt='consent')
    print("=" * 60)
    print(auth_url)
    print("=" * 60)
    print()
    print("[STEP 2] Complete authorization in your browser")
    print("[STEP 3] After redirect, paste the full redirect URL here:")
    print("         (It will look like http://localhost:8081/?code=...)")
    print()
    
    try:
        redirect_response = input("Paste redirect URL: ").strip()
        if redirect_response:
            flow.fetch_token(code=redirect_response.split('code=')[1].split('&')[0])
            creds = flow.credentials
            print("[OK] Authorization successful!")
        else:
            print("[ERROR] No URL provided")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Authorization failed: {e}")
        sys.exit(1)

# Save token
if creds and creds.valid:
    print()
    print("[INFO] Saving token...")
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json())
    print(f"[OK] Token saved to: {token_path.absolute()}")
    
    # Test Gmail API
    print()
    print("[INFO] Testing Gmail API connection...")
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Get profile
        profile = service.users().getProfile(userId='me').execute()
        print(f"[OK] Connected to Gmail!")
        print(f"     Account: {profile['emailAddress']}")
        print(f"     Messages: {profile['messagesTotal']}")
        print(f"     Threads: {profile['threadsTotal']}")
        
        # Get recent messages
        print()
        print("[INFO] Fetching recent messages...")
        results = service.users().messages().list(userId='me', maxResults=5).execute()
        messages = results.get('messages', [])
        
        if messages:
            print(f"[OK] Found {len(messages)} recent messages:")
            print()
            for msg in messages:
                msg_detail = service.users().messages().get(
                    userId='me', id=msg['id'], format='metadata'
                ).execute()
                headers = msg_detail['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                print(f"     • From: {from_addr[:60]}")
                print(f"       Subject: {subject[:60]}")
                print(f"       Date: {date}")
                print()
        else:
            print("[INFO] No messages found")
            
        print("=" * 60)
        print("Gmail API Test COMPLETE!")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] Gmail API test failed: {e}")
        sys.exit(1)
else:
    print("[ERROR] No valid credentials")
    sys.exit(1)
