"""
Quick WhatsApp Test - Auto Run

This will:
1. Open browser with fresh session
2. Load WhatsApp Web
3. Wait for you to scan QR code
4. Test reading messages
5. Create action files for keyword messages

Usage:
    python test_whatsapp_quick.py
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_PATH = Path("AI_Employee_Vault/.whatsapp_session")
NEEDS_ACTION = Path("AI_Employee_Vault/Needs_Action")

KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'test', 'hello']

print("=" * 60)
print("WhatsApp Quick Test")
print("=" * 60)
print()

with sync_playwright() as p:
    print("[INFO] Opening browser...")
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_PATH),
        headless=False,
        args=['--disable-blink-features=AutomationControlled', '--no-sandbox'],
        viewport={'width': 1280, 'height': 800}
    )
    
    page = context.pages[0] if context.pages else context.new_page()
    
    print("[INFO] Loading WhatsApp Web...")
    print("[ACTION] Scan the QR code with your WhatsApp mobile app!")
    print()
    
    page.goto('https://web.whatsapp.com/', wait_until='networkidle')
    
    # Wait for chat list (logged in)
    print("[WAIT] Waiting for WhatsApp to load...")
    try:
        page.wait_for_selector('[data-testid="chat-list"]', timeout=60000)
        print("[OK] WhatsApp Web loaded!")
        print()
        
        # Give it time to stabilize
        time.sleep(3)
        
        # Get chats
        chats = page.query_selector_all('[role="row"]')
        print(f"[INFO] Found {len(chats)} chats")
        print()
        
        # Check messages for keywords
        print(f"[INFO] Checking for keywords: {', '.join(KEYWORDS)}")
        created_files = []
        
        for i, chat in enumerate(chats[:10]):  # Check top 10 chats
            try:
                name_elem = chat.query_selector('span[dir="auto"]')
                msg_elem = chat.query_selector('span[dir="auto"][title]')
                
                if name_elem and msg_elem:
                    name = name_elem.inner_text()
                    message = msg_elem.get_attribute('title', '')
                    
                    # Check keywords
                    for keyword in KEYWORDS:
                        if keyword in message.lower():
                            print(f"  [FOUND] '{keyword}' in message from: {name}")
                            
                            # Create action file
                            safe_name = "".join(c for c in name if c.isalnum() or c in ' -_')[:30]
                            timestamp = int(time.time())
                            filename = f"WHATSAPP_{safe_name}_{timestamp}.md"
                            filepath = NEEDS_ACTION / filename
                            
                            NEEDS_ACTION.mkdir(parents=True, exist_ok=True)
                            
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
                            filepath.write_text(content, encoding='utf-8')
                            created_files.append(filename)
                            print(f"  [CREATED] {filename}")
                            break
            except Exception:
                pass
        
        print()
        print("=" * 60)
        if created_files:
            print(f"SUCCESS! Created {len(created_files)} WhatsApp action file(s):")
            for f in created_files:
                print(f"  - {f}")
        else:
            print("No messages with keywords found.")
            print("Send yourself a WhatsApp message with 'test' to try again!")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        print("QR code may have expired or connection issue")
    
    print()
    print("Keeping browser open for 10 seconds...")
    time.sleep(10)
    context.close()

print("[OK] Done!")
