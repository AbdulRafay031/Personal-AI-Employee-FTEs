"""
Gmail Watcher Module

Monitors Gmail for new unread/important messages and creates action files
in the Needs_Action folder for Claude Code to process.

Setup Requirements:
1. Enable Gmail API: https://developers.google.com/gmail/api/quickstart/python
2. Download credentials.json from Google Cloud Console
3. Run once interactively to authorize: python gmail_watcher.py --auth
4. Token will be saved as token.json (add to .gitignore)

Usage:
    python gmail_watcher.py /path/to/vault --credentials /path/to/credentials.json
"""

import os
import sys
import base64
from pathlib import Path
from datetime import datetime
from email import message_from_bytes
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Gmail API imports (install: pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib)
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.auth.transport.requests import Request
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("Gmail API not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new unread/important messages.
    
    Creates action files in Needs_Action folder with:
    - Sender information
    - Subject line
    - Email snippet/full content
    - Suggested actions
    """
    
    # Scopes required for Gmail API
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    # Keywords that indicate high priority
    PRIORITY_KEYWORDS = [
        'urgent', 'asap', 'invoice', 'payment', 'help',
        'deadline', 'emergency', 'important', 'action required'
    ]
    
    def __init__(self, vault_path: str, credentials_path: str, check_interval: int = 120):
        """
        Initialize Gmail Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to Gmail API credentials.json
            check_interval: Seconds between checks (default: 120)
        """
        if not GMAIL_AVAILABLE:
            raise ImportError("Gmail API not available. Install required packages.")
        
        super().__init__(vault_path, check_interval)
        
        self.credentials_path = Path(credentials_path)
        self.token_path = self.vault_path / 'token.json'  # Store token in vault (add to .gitignore!)
        
        self.service = self._authenticate()
        self.label_map = {}
    
    def _authenticate(self):
        """
        Authenticate with Gmail API.
        
        Returns:
            Gmail API service object
        """
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(
                self.token_path, self.SCOPES
            )
        
        # Refresh or obtain new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f'Credentials file not found: {self.credentials_path}\n'
                        'Download from: https://developers.google.com/gmail/api/quickstart/python'
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token for future use
            self.token_path.write_text(creds.to_json())
            self.token_path.chmod(0o600)  # Restrict permissions
            self.logger.info('Gmail authentication successful')
        
        return build('gmail', 'v1', credentials=creds)
    
    def _get_label_name(self, label_id: str) -> str:
        """Get label name from ID, caching results."""
        if label_id in self.label_map:
            return self.label_map[label_id]
        
        try:
            label = self.service.users().labels().get(
                userId='me', id=label_id
            ).execute()
            self.label_map[label_id] = label['name']
            return label['name']
        except Exception:
            return label_id
    
    def _decode_message(self, message: Dict) -> Dict:
        """
        Decode Gmail message into usable format.
        
        Args:
            message: Raw Gmail message dict
            
        Returns:
            Decoded message with headers and body
        """
        headers = {}
        payload = message.get('payload', {})
        
        # Extract headers
        for header in payload.get('headers', []):
            headers[header['name'].lower()] = header['value']
        
        # Extract body
        body = ''
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='replace')
                        break
        elif 'body' in payload:
            # Simple message
            if 'data' in payload['body']:
                body = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8', errors='replace')
        
        # Truncate long bodies
        if len(body) > 2000:
            body = body[:2000] + '... [truncated]'
        
        return {
            'id': message['id'],
            'threadId': message['threadId'],
            'from': headers.get('from', 'Unknown'),
            'to': headers.get('to', ''),
            'subject': headers.get('subject', 'No Subject'),
            'date': headers.get('date', ''),
            'labels': message.get('labelIds', []),
            'snippet': message.get('snippet', ''),
            'body': body,
            'has_attachment': 'ATTACHMENT' in message.get('labelIds', [])
        }
    
    def _determine_priority(self, message: Dict) -> str:
        """
        Determine message priority based on content.
        
        Args:
            message: Decoded message dict
            
        Returns:
            Priority level: 'high', 'medium', or 'low'
        """
        text = f"{message['subject']} {message['snippet']} {message['body']}".lower()
        
        # Check for priority keywords
        for keyword in self.PRIORITY_KEYWORDS:
            if keyword in text:
                return 'high'
        
        # Check labels
        if 'IMPORTANT' in message['labels']:
            return 'medium'
        if 'UNREAD' in message['labels']:
            return 'medium'
        
        return 'low'
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check Gmail for new unread messages.
        
        Returns:
            List of new message dicts
        """
        try:
            # Fetch unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            # Filter out already processed
            new_messages = []
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    # Fetch full message
                    full_message = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    
                    decoded = self._decode_message(full_message)
                    new_messages.append(decoded)
                    self.processed_ids.add(msg['id'])
                    
                    # Limit processed set size
                    if len(self.processed_ids) > 1000:
                        self.processed_ids = set(list(self.processed_ids)[-500:])
            
            return new_messages
            
        except HttpError as error:
            self.logger.error(f'Gmail API error: {error}')
            return []
        except Exception as error:
            self.logger.error(f'Unexpected error: {error}')
            return []
    
    def create_action_file(self, message: Dict) -> Optional[Path]:
        """
        Create action file for a Gmail message.
        
        Args:
            message: Decoded message dict
            
        Returns:
            Path to created file
        """
        priority = self._determine_priority(message)
        
        # Extract sender email
        from_email = message['from']
        if '<' in from_email:
            from_email = from_email.split('<')[1].strip('>')
        
        # Generate filename
        subject_safe = self.sanitize_filename(message['subject'][:50])
        filename = f"EMAIL_{from_email}_{message['id']}.md"
        filepath = self.needs_action / filename
        
        # Generate suggested actions
        actions = []
        if 'invoice' in message['subject'].lower() or 'payment' in message['subject'].lower():
            actions.append('- [ ] Extract invoice details and log to Accounting')
            actions.append('- [ ] Schedule payment if approved')
        elif 'meeting' in message['subject'].lower() or 'calendar' in message['subject'].lower():
            actions.append('- [ ] Check calendar availability')
            actions.append('- [ ] Respond with available times')
        else:
            actions.append('- [ ] Read and determine response needed')
            actions.append('- [ ] Draft reply if necessary')
        
        actions.append('- [ ] Archive email after processing')
        
        # Create content
        content = f'''{self.generate_frontmatter(
            item_type='email',
            sender=f'"{message["from"]}"',
            sender_email=from_email,
            subject=f'"{message["subject"]}"',
            received=datetime.now().isoformat(),
            priority=priority,
            message_id=f'"{message["id"]}"'
        )}

## Email Details

| Field | Value |
|-------|-------|
| **From** | {message['from']} |
| **To** | {message['to']} |
| **Subject** | {message['subject']} |
| **Date** | {message['date']} |
| **Priority** | {priority} |

---

## Message Content

{message['body'] if message['body'] else message['snippet']}

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


def main():
    """Main entry point for Gmail Watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--credentials', required=True, help='Path to Gmail credentials.json')
    parser.add_argument('--interval', type=int, default=120, help='Check interval in seconds')
    parser.add_argument('--auth-only', action='store_true', help='Authenticate and exit')
    
    args = parser.parse_args()
    
    if args.auth_only:
        # Just authenticate and save token
        watcher = GmailWatcher(args.vault_path, args.credentials)
        print('Authentication successful! Token saved.')
        return
    
    watcher = GmailWatcher(args.vault_path, args.credentials, args.interval)
    watcher.run()


if __name__ == '__main__':
    main()
