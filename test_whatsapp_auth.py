"""
WhatsApp Authentication Test Script

Run this to authenticate WhatsApp Web and save the session.
The session will be reused for future runs.

Usage:
    python test_whatsapp_auth.py
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_PATH = Path("AI_Employee_Vault/.whatsapp_session")
SESSION_PATH.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("WhatsApp Web Authentication Test")
print("=" * 60)
print()

print("[INFO] Starting browser...")
print("[STEP 1] A browser window will open")
print("[STEP 2] WhatsApp Web will load")
print("[STEP 3] Scan the QR code with your WhatsApp mobile app")
print("[STEP 4] After successful login, the session will be saved")
print()
print("Press Enter to continue...")
input()

with sync_playwright() as p:
    # Launch browser
    browser = p.chromium.launch(
        headless=False,  # Visible browser for QR scan
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ]
    )
    
    # Create context with persistent storage
    context = browser.new_context(
        user_data_dir=str(SESSION_PATH),
        viewport={'width': 1280, 'height': 800}
    )
    
    page = context.new_page()
    
    print("[INFO] Loading WhatsApp Web...")
    page.goto('https://web.whatsapp.com/', wait_until='networkidle')
    
    print()
    print("[WAITING] Please scan the QR code with your WhatsApp mobile app")
    print("          This will take about 30-60 seconds...")
    print()
    
    # Wait for main chat list to appear (indicates successful login)
    try:
        print("[INFO] Waiting for chat list to load...")
        page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
        print("[OK] WhatsApp Web logged in successfully!")
        print()
        
        # Wait a bit for session to stabilize
        time.sleep(3)
        
        # Get current chat count
        chats = page.query_selector_all('[role="row"]')
        print(f"[INFO] Found {len(chats)} recent chats")
        
        print()
        print("[OK] Session saved to:", SESSION_PATH.absolute())
        print()
        print("=" * 60)
        print("Authentication Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Close the browser window")
        print("  2. Run the WhatsApp watcher:")
        print("     python watchers/whatsapp_watcher.py AI_Employee_Vault --session-path AI_Employee_Vault/.whatsapp_session")
        
    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        print()
        print("Possible causes:")
        print("  - QR code expired (refresh page and try again)")
        print("  - Network connection issue")
        print("  - WhatsApp Web temporarily unavailable")
    
    print()
    print("Keep browser open for 5 more seconds to save session...")
    time.sleep(5)
    
    browser.close()

print()
print("[OK] Browser closed. Session saved.")
