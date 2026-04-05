"""
WhatsApp Watcher Module

Monitors WhatsApp Web for new messages and creates action files
in the Needs_Action folder for Claude Code to process.

Setup Requirements:
1. Install Playwright: pip install playwright
2. Install browser: playwright install chromium
3. Create session folder: mkdir -p /path/to/vault/.whatsapp_session
4. Run once interactively to scan QR code

Usage:
    python whatsapp_watcher.py /path/to/vault --session-path /path/to/session
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from watchers.base_watcher import BaseWatcher
except ImportError:
    from base_watcher import BaseWatcher

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Run: pip install playwright && playwright install chromium")


class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp Web for new messages.

    Creates action files in Needs_Action folder with:
    - Sender information
    - Message content
    - Detected keywords
    - Suggested actions
    """

    # Default keywords that indicate importance
    DEFAULT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'deadline', 'emergency']

    # WhatsApp Web selectors (may need updates if WhatsApp changes UI)
    SELECTORS = {
        'chat_list': '[data-testid="chat-list"]',
        'chat_item': 'div[role="row"]',
        'message_bubble': 'div[data-testid="message-text"]',
        'contact_name': 'span[dir="auto"]',
        'unread_indicator': '[aria-label*="unread"]',
        'qr_code': '[data-testid="qrcode"]',
        'main_panel': '#main',
    }

    def __init__(
        self,
        vault_path: str,
        session_path: str,
        check_interval: int = 30,
        keywords: List[str] = None,
        headless: bool = True,
        vip_contacts: List[str] = None
    ):
        """
        Initialize WhatsApp Watcher.

        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session data
            check_interval: Seconds between checks (default: 30)
            keywords: List of trigger keywords (default: DEFAULT_KEYWORDS)
            headless: Run browser in headless mode (default: True)
            vip_contacts: List of VIP contact names (always notify)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not available. Install with: pip install playwright")

        super().__init__(vault_path, check_interval)

        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.keywords = keywords or self.DEFAULT_KEYWORDS
        self.headless = headless
        self.vip_contacts = vip_contacts or []

        # Track processed messages
        self.processed_messages: Set[str] = set()

        # Browser state
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        self.logger.info(f'WhatsApp Watcher initialized (keywords: {", ".join(self.keywords)})')

    def _init_browser(self):
        """Initialize Playwright browser with persistent context."""
        try:
            playwright = sync_playwright().start()
            
            # Launch browser with persistent context
            self.context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ],
                viewport={'width': 1280, 'height': 720},
            )
            
            self.page = self.context.pages[0]
            
            # Navigate to WhatsApp Web
            self.page.goto('https://web.whatsapp.com', wait_until='networkidle')
            
            self.logger.info('Browser initialized and navigated to WhatsApp Web')
            
        except Exception as e:
            self.logger.error(f'Failed to initialize browser: {e}')
            raise

    def _check_qr_code(self) -> bool:
        """
        Check if QR code is displayed (needs authentication).

        Returns:
            True if QR code is visible (needs scan), False if logged in
        """
        try:
            # Wait a bit for page to load
            self.page.wait_for_timeout(5000)
            
            # Check for QR code
            qr_locator = self.page.locator(self.SELECTORS['qr_code'])
            if qr_locator.count() > 0:
                self.logger.warning('QR code detected - please scan with WhatsApp mobile app')
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f'QR code check error: {e}')
            return False

    def _wait_for_chat_list(self, timeout: int = 10000):
        """Wait for chat list to be available."""
        try:
            self.page.wait_for_selector(self.SELECTORS['chat_list'], timeout=timeout)
        except Exception as e:
            self.logger.debug(f'Chat list not found: {e}')

    def _get_unread_chats(self) -> List[Dict]:
        """
        Get list of chats with unread messages.

        Returns:
            List of chat info dictionaries
        """
        chats = []
        
        try:
            # Wait for chat list
            self._wait_for_chat_list()
            
            # Find all chat items
            chat_items = self.page.query_selector_all(self.SELECTORS['chat_item'])
            
            for chat_item in chat_items:
                try:
                    # Get contact name
                    name_elem = chat_item.query_selector(self.SELECTORS['contact_name'])
                    if not name_elem:
                        continue
                    
                    contact_name = name_elem.inner_text().strip()
                    
                    # Get message preview
                    message_elem = chat_item.query_selector(self.SELECTORS['message_bubble'])
                    message_text = message_elem.inner_text().strip() if message_elem else ''
                    
                    # Check if unread (look for unread indicator or bold text)
                    is_unread = chat_item.get_attribute('aria-label') and 'unread' in chat_item.get_attribute('aria-label').lower()
                    
                    # Generate contact ID (sanitize for filename)
                    contact_id = self.sanitize_filename(contact_name.lower().replace(' ', '_'))
                    
                    chats.append({
                        'from': contact_name,
                        'contact_id': contact_id,
                        'text': message_text,
                        'timestamp': datetime.now().isoformat(),
                        'is_unread': is_unread,
                        'is_group': False,  # Could be enhanced to detect groups
                    })
                    
                except Exception as e:
                    self.logger.debug(f'Error parsing chat item: {e}')
                    continue
            
        except Exception as e:
            self.logger.error(f'Failed to get unread chats: {e}')
        
        return chats

    def _detect_keywords(self, text: str) -> List[str]:
        """
        Detect keywords in message text.

        Args:
            text: Message text to analyze

        Returns:
            List of detected keywords
        """
        text_lower = text.lower()
        detected = []
        
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                detected.append(keyword)
        
        return detected

    def _determine_priority(self, message: Dict) -> str:
        """
        Determine message priority.

        Args:
            message: Message dictionary

        Returns:
            Priority level: 'high', 'medium', or 'low'
        """
        # VIP contacts always get high priority
        if message['from'] in self.vip_contacts:
            return 'high'
        
        # Check for keywords
        detected_keywords = self._detect_keywords(message['text'])
        if detected_keywords:
            return 'high'
        
        # Unread messages get medium priority
        if message.get('is_unread'):
            return 'medium'
        
        return 'low'

    def check_for_updates(self) -> List[Dict]:
        """
        Check WhatsApp for new messages.

        Returns:
            List of new message dictionaries
        """
        try:
            # Initialize browser if needed
            if self.page is None:
                self._init_browser()
                
                # Check if QR code scan needed
                if self._check_qr_code():
                    self.logger.warning('Waiting for QR code scan...')
                    # Wait up to 60 seconds for scan
                    for _ in range(12):  # 12 * 5 seconds = 60 seconds
                        time.sleep(5)
                        if not self._check_qr_code():
                            self.logger.info('QR code scanned successfully!')
                            break
                    else:
                        self.logger.error('QR code scan timeout')
                        return []
            
            # Refresh page if needed (prevent session timeout)
            try:
                self.page.wait_for_selector(self.SELECTORS['chat_list'], timeout=5000)
            except:
                self.logger.info('Session expired, refreshing...')
                self.page.reload()
                self._wait_for_chat_list()
            
            # Get unread chats
            chats = self._get_unread_chats()
            
            # Filter out already processed
            new_messages = []
            for chat in chats:
                # Create unique message ID
                message_id = f"{chat['contact_id']}_{chat['timestamp']}"
                
                if message_id not in self.processed_messages:
                    # Check if message contains keywords or is from VIP
                    detected_keywords = self._detect_keywords(chat['text'])
                    if detected_keywords or chat['from'] in self.vip_contacts:
                        chat['keywords'] = detected_keywords
                        new_messages.append(chat)
                        self.processed_messages.add(message_id)
                        
                        # Limit cache size
                        if len(self.processed_messages) > 1000:
                            self.processed_messages = set(list(self.processed_messages)[-500:])
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f'Error checking WhatsApp: {e}', exc_info=True)
            return []

    def create_action_file(self, message: Dict) -> Optional[Path]:
        """
        Create action file for a WhatsApp message.

        Args:
            message: Message dictionary

        Returns:
            Path to created file
        """
        priority = self._determine_priority(message)
        detected_keywords = message.get('keywords', [])
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"WHATSAPP_{message['contact_id']}_{timestamp}.md"
        filepath = self.needs_action / filename
        
        # Generate suggested actions based on keywords
        actions = []
        if 'invoice' in detected_keywords or 'payment' in detected_keywords:
            actions.append('- [ ] Extract payment/invoice details')
            actions.append('- [ ] Check accounting records')
            actions.append('- [ ] Prepare response (requires approval)')
        elif 'urgent' in detected_keywords or 'asap' in detected_keywords:
            actions.append('- [ ] Respond urgently (draft for approval)')
            actions.append('- [ ] Determine if immediate action needed')
        elif 'help' in detected_keywords:
            actions.append('- [ ] Assess request')
            actions.append('- [ ] Provide assistance or escalate')
        else:
            actions.append('- [ ] Read message')
            actions.append('- [ ] Draft response if needed')
        
        actions.append('- [ ] Mark as read in WhatsApp after processing')
        
        # Create content
        content = f'''{self.generate_frontmatter(
            item_type='whatsapp',
            sender=f'"{message["from"]}"',
            contact_id=f'"{message["contact_id"]}"',
            received=datetime.now().isoformat(),
            priority=priority,
            keywords=', '.join(detected_keywords) if detected_keywords else 'none'
        )}

## Message Details

| Field | Value |
|-------|-------|
| **From** | {message['from']} |
| **Contact ID** | {message['contact_id']} |
| **Received** | {message['timestamp']} |
| **Priority** | {priority} |
| **Keywords Detected** | {', '.join(detected_keywords) if detected_keywords else 'None'} |

---

## Message Content

{message['text']}

---

## Suggested Actions

{chr(10).join(actions)}

---

## Notes

```
Add processing notes here...
```
'''
        
        try:
            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f'Created action file: {filename}')
            return filepath
        except Exception as e:
            self.logger.error(f'Failed to create action file: {e}')
            return None

    def mark_as_read(self, contact_id: str):
        """
        Mark a chat as read in WhatsApp Web.

        Args:
            contact_id: Contact ID to mark as read
        """
        try:
            # This would require additional Playwright logic to click on the chat
            # For now, this is a placeholder for future implementation
            self.logger.debug(f'Mark as read not yet implemented for: {contact_id}')
        except Exception as e:
            self.logger.error(f'Failed to mark as read: {e}')

    def run(self):
        """
        Main run loop with graceful shutdown.
        """
        self.logger.info(f'Starting WhatsApp Watcher (interval: {self.check_interval}s, headless: {self.headless})')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    for item in items:
                        self.create_action_file(item)
                except Exception as e:
                    self.logger.error(f'Error during check: {e}', exc_info=True)
                    # Try to reinitialize browser on error
                    self.page = None
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info('WhatsApp Watcher stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
        finally:
            # Cleanup
            if self.context:
                try:
                    self.context.close()
                except:
                    pass


def main():
    """Main entry point for WhatsApp Watcher."""
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--session-path', required=True, help='Path to store browser session')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--keywords', type=str, default=None, 
                        help='Comma-separated keywords to detect')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--vip-contacts', type=str, default=None,
                        help='Comma-separated VIP contact names')
    parser.add_argument('--interactive', action='store_true',
                        help='Run in interactive mode (visible browser for QR scan)')

    args = parser.parse_args()

    # Parse keywords
    keywords = None
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(',')]

    # Parse VIP contacts
    vip_contacts = None
    if args.vip_contacts:
        vip_contacts = [c.strip() for c in args.vip_contacts.split(',')]

    # Override headless if interactive mode
    headless = args.headless and not args.interactive

    try:
        watcher = WhatsAppWatcher(
            args.vault_path,
            args.session_path,
            check_interval=args.interval,
            keywords=keywords,
            headless=headless,
            vip_contacts=vip_contacts
        )
        watcher.run()
    except KeyboardInterrupt:
        print('\nWatcher stopped by user')
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
