"""
Test WhatsApp Watcher - Quick Test

This script will:
1. Load the saved WhatsApp session
2. Check for recent messages
3. Create action files for messages with keywords
4. Exit after 60 seconds

Usage:
    python test_whatsapp_watcher.py
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_PATH = Path("AI_Employee_Vault/.whatsapp_session")
VAULT_PATH = Path("AI_Employee_Vault")
NEEDS_ACTION = VAULT_PATH / "Needs_Action"

# Keywords to detect
KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'quote', 'pricing', 'emergency', 'test']

print("=" * 60)
print("WhatsApp Watcher Test")
print("=" * 60)
print()

print("[INFO] Loading saved session...")
print(f"[INFO] Session path: {SESSION_PATH.absolute()}")
print()

with sync_playwright() as p:
    # Launch browser with saved session using persistent context
    print("[INFO] Starting browser with saved session...")
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_PATH),
        headless=False,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ],
        viewport={'width': 1280, 'height': 800}
    )
    
    page = context.pages[0] if context.pages else context.new_page()
    
    # Go to WhatsApp Web
    print("[INFO] Loading WhatsApp Web...")
    page.goto('https://web.whatsapp.com/', wait_until='networkidle')
    time.sleep(5)  # Wait for page to load
    
    # Check if logged in
    chat_list = page.query_selector('[data-testid="chat-list"]')
    if chat_list:
        print("[OK] WhatsApp Web logged in successfully!")
        print()
        
        # Get recent chats
        chats = page.query_selector_all('[role="row"]')
        print(f"[INFO] Found {len(chats)} recent chats")
        print()
        
        # Check for messages with keywords
        print(f"[INFO] Monitoring for keywords: {', '.join(KEYWORDS)}")
        print("[INFO] Watching for 60 seconds...")
        print()
        
        action_files_created = []
        
        # Monitor for 60 seconds
        for i in range(6):
            print(f"[CHECK {i+1}/6] Scanning for new messages...")
            
            # Get chat list
            chats = page.query_selector_all('[role="row"]')
            
            for chat in chats[:5]:  # Check top 5 chats
                try:
                    # Get chat info
                    name_elem = chat.query_selector('span[dir="auto"]')
                    message_elem = chat.query_selector('span[dir="auto"][title]')
                    
                    if name_elem and message_elem:
                        name = name_elem.inner_text()
                        message = message_elem.get_attribute('title', '')
                        
                        # Check for keywords
                        message_lower = message.lower()
                        for keyword in KEYWORDS:
                            if keyword in message_lower:
                                print(f"  [KEYWORD FOUND] '{keyword}' in message from {name}")
                                
                                # Create action file
                                safe_name = "".join(c for c in name if c.isalnum() or c in ' -_')[:30]
                                timestamp = int(time.time())
                                filename = f"WHATSAPP_{safe_name}_{timestamp}.md"
                                filepath = NEEDS_ACTION / filename
                                
                                content = f'''---
type: whatsapp
sender: "{name}"
message: "{message}"
keywords: ["{keyword}"]
received: {time.strftime('%Y-%m-%dT%H:%M:%S')}
priority: high
status: pending
---

## WhatsApp Message

| Field | Value |
|-------|-------|
| **From** | {name} |
| **Message** | {message} |
| **Keyword** | {keyword} |
| **Priority** | high |

---

## Suggested Actions

- [ ] Read message and determine response
- [ ] Reply via WhatsApp if needed
- [ ] Mark as done after processing

---

## Notes

```
Add processing notes here...
```
'''
                                NEEDS_ACTION.mkdir(parents=True, exist_ok=True)
                                filepath.write_text(content, encoding='utf-8')
                                action_files_created.append(filename)
                                print(f"  [ACTION CREATED] {filename}")
                                break  # Only one action per chat
                
                except Exception as e:
                    pass  # Skip chats that can't be read
            
            time.sleep(10)  # Wait 10 seconds between checks
        
        print()
        print("=" * 60)
        print("Test Complete!")
        print("=" * 60)
        
        if action_files_created:
            print(f"\n[OK] Created {len(action_files_created)} WhatsApp action file(s):")
            for f in action_files_created:
                print(f"  - {f}")
            print()
            print("Check the Needs_Action folder for the created files!")
        else:
            print("\n[INFO] No messages with keywords detected during test")
            print("         Try sending yourself a WhatsApp message with 'test' keyword")
        
    else:
        print("[ERROR] Not logged in!")
        print("        The QR code may have expired or session is invalid")
        print("        Please re-scan the QR code")
    
    context.close()

print()
print("[OK] Browser closed")
