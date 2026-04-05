"""
Email MCP Client Module

Handles email sending via Gmail API or SMTP with human-in-the-loop approval.

Setup Requirements:
1. Enable Gmail API: https://developers.google.com/gmail/api/quickstart/python
2. Download credentials.json from Google Cloud Console
3. Create .env file with credentials
4. Run once to authenticate: python email_mcp_client.py --auth

Usage:
    python email_mcp_client.py /path/to/vault --action send --to "recipient@example.com"
    python email_mcp_client.py /path/to/vault --action draft --to "client@example.com"
"""

import os
import sys
import base64
import json
import smtplib
import hashlib
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from watchers.base_watcher import BaseWatcher
except ImportError:
    from base_watcher import BaseWatcher

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.auth.transport.requests import Request
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False


class EmailMCPClient(BaseWatcher):
    """
    Email MCP Client for sending emails with approval workflow.

    Supports:
    - Gmail API (recommended)
    - SMTP fallback
    - Draft creation
    - Approval workflow
    - Email logging
    """

    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    # Email templates
    TEMPLATES = {
        'invoice': """Dear {client_name},

Please find attached invoice #{invoice_number} for ${amount}.

**Invoice Details:**
- Invoice Number: {invoice_number}
- Amount: ${amount}
- Due Date: {due_date}
- Services: {services}

Payment can be made via:
{payment_details}

If you have any questions, please don't hesitate to reach out.

Best regards,
{your_name}
{your_company}""",

        'followup': """Hi {contact_name},

Hope you're doing well!

I wanted to follow up on our previous conversation about {topic}.

{custom_message}

Would you have time for a quick call this week to discuss further?

Looking forward to hearing from you.

Best regards,
{your_name}""",

        'meeting_request': """Dear {recipient_name},

I hope this email finds you well.

I'd like to schedule a meeting to discuss {meeting_topic}.

**Proposed Times:**
- {time_option_1}
- {time_option_2}

**Meeting Details:**
- Duration: {duration}
- Location: {location}
- Attendees: {attendees}

Please let me know which time works best for you.

Best regards,
{your_name}""",
    }

    def __init__(
        self,
        vault_path: str,
        credentials_path: str = None,
        use_gmail: bool = True,
        smtp_config: Dict = None,
    ):
        """
        Initialize Email MCP Client.

        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to Gmail credentials.json
            use_gmail: Use Gmail API (default: True)
            smtp_config: SMTP configuration (if not using Gmail)
        """
        super().__init__(vault_path, check_interval=0)

        self.credentials_path = Path(credentials_path) if credentials_path else None
        self.use_gmail = use_gmail
        self.smtp_config = smtp_config or {}

        # Token path (store in vault, add to .gitignore)
        self.token_path = self.vault_path / '.gmail_token.json'

        # Contacts file
        self.approved_contacts_file = self.vault_path / 'Contacts' / 'Approved_Recipients.md'

        # Gmail service
        self.gmail_service = None

        # Load approved contacts
        self.approved_contacts = self._load_approved_contacts()

        self.logger.info(f'Email MCP Client initialized (Gmail API: {self.use_gmail})')

    def _load_approved_contacts(self) -> Dict[str, str]:
        """Load approved contacts from vault."""
        contacts = {}

        if self.approved_contacts_file.exists():
            try:
                content = self.approved_contacts_file.read_text(encoding='utf-8')
                # Simple parsing - extract email addresses
                import re
                emails = re.findall(r'-\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', content)
                for email in emails:
                    contacts[email.lower()] = 'approved'
            except Exception as e:
                self.logger.error(f'Failed to load approved contacts: {e}')

        return contacts

    def _authenticate(self) -> bool:
        """
        Authenticate with Gmail API.

        Returns:
            True if successful, False otherwise
        """
        if not GMAIL_AVAILABLE:
            self.logger.error('Gmail API not available')
            return False

        if not self.credentials_path or not self.credentials_path.exists():
            self.logger.error(f'Credentials file not found: {self.credentials_path}')
            return False

        creds = None

        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(
                self.token_path, self.SCOPES
            )

        # Refresh or obtain new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f'Token refresh failed: {e}')
                    creds = None
            else:
                self.logger.info('Starting OAuth flow...')
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token for future use
            if creds:
                self.token_path.write_text(creds.to_json())
                self.token_path.chmod(0o600)
                self.logger.info('Authentication successful')

        if creds and creds.valid:
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            return True

        return False

    def _is_approved_contact(self, email: str) -> bool:
        """Check if contact is approved for auto-send."""
        return email.lower() in self.approved_contacts

    def _create_message(
        self,
        to: str,
        subject: str,
        body: str,
        cc: str = None,
        bcc: str = None,
        attachments: List[str] = None,
    ) -> Dict:
        """
        Create email message.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachment paths

        Returns:
            Gmail API message object
        """
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = 'me'
        message['subject'] = subject

        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc

        # Add body
        message.attach(MIMEText(body, 'plain', 'utf-8'))

        # Add attachments
        if attachments:
            for file_path in attachments:
                try:
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())

                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{Path(file_path).name}"',
                    )
                    message.attach(part)
                except Exception as e:
                    self.logger.error(f'Failed to attach {file_path}: {e}')

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        return {'raw': raw_message}

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: str = None,
        bcc: str = None,
        attachments: List[str] = None,
        skip_approval: bool = False,
    ) -> Tuple[bool, str]:
        """
        Send email.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachment paths
            skip_approval: Skip approval check (use with caution)

        Returns:
            (success, message_id or error message)
        """
        try:
            # Check dry run mode
            if os.getenv('DRY_RUN', 'false').lower() == 'true':
                self.logger.info(f'[DRY RUN] Would send email to {to}')
                return True, 'DRY_RUN_SUCCESS'

            # Check if approval needed
            needs_approval = not self._is_approved_contact(to)
            if attachments:
                needs_approval = True

            if needs_approval and not skip_approval:
                self.logger.warning(f'Email to {to} requires approval')
                return False, 'REQUIRES_APPROVAL'

            # Authenticate if using Gmail
            if self.use_gmail:
                if not self.gmail_service:
                    if not self._authenticate():
                        return False, 'AUTHENTICATION_FAILED'

                # Create message
                message = self._create_message(to, subject, body, cc, bcc, attachments)

                # Send via Gmail API
                sent_message = self.gmail_service.users().messages().send(
                    userId='me', body=message
                ).execute()

                message_id = sent_message['id']
                self.logger.info(f'Email sent successfully (Message ID: {message_id})')

                # Log the email
                self._log_email({
                    'to': to,
                    'subject': subject,
                    'status': 'sent',
                    'message_id': message_id,
                    'timestamp': datetime.now().isoformat(),
                })

                return True, message_id

            else:
                # Use SMTP
                return self._send_smtp(to, subject, body, cc, bcc, attachments)

        except Exception as e:
            self.logger.error(f'Failed to send email: {e}', exc_info=True)
            return False, str(e)

    def _send_smtp(
        self,
        to: str,
        subject: str,
        body: str,
        cc: str = None,
        bcc: str = None,
        attachments: List[str] = None,
    ) -> Tuple[bool, str]:
        """Send email via SMTP."""
        try:
            # Get SMTP config from environment
            smtp_server = self.smtp_config.get('server', os.getenv('SMTP_SERVER'))
            smtp_port = int(self.smtp_config.get('port', os.getenv('SMTP_PORT', 587)))
            smtp_user = self.smtp_config.get('user', os.getenv('SMTP_USER'))
            smtp_password = self.smtp_config.get('password', os.getenv('SMTP_PASSWORD'))

            if not smtp_server or not smtp_user or not smtp_password:
                return False, 'SMTP configuration missing'

            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject

            if cc:
                message['cc'] = cc

            message.attach(MIMEText(body, 'plain', 'utf-8'))

            # Add attachments
            if attachments:
                for file_path in attachments:
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{Path(file_path).name}"',
                    )
                    message.attach(part)

            # Send via SMTP
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)

            recipients = [to]
            if cc:
                recipients.extend(cc.split(','))
            if bcc:
                recipients.extend(bcc.split(','))

            server.sendmail(smtp_user, recipients, message.as_string())
            server.quit()

            self.logger.info(f'Email sent via SMTP to {to}')

            # Log the email
            self._log_email({
                'to': to,
                'subject': subject,
                'status': 'sent',
                'timestamp': datetime.now().isoformat(),
            })

            return True, 'SMTP_SUCCESS'

        except Exception as e:
            self.logger.error(f'SMTP send failed: {e}')
            return False, str(e)

    def create_draft_file(
        self,
        to: str,
        subject: str,
        body: str,
        attachments: List[str] = None,
        template_name: str = None,
    ) -> Optional[Path]:
        """
        Create email draft file in Plans folder.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            attachments: List of attachment paths
            template_name: Template used (if any)

        Returns:
            Path to created file
        """
        try:
            plans_folder = self.vault_path / 'Plans'
            plans_folder.mkdir(parents=True, exist_ok=True)

            # Determine if approval needed
            needs_approval = not self._is_approved_contact(to)
            if attachments:
                needs_approval = True

            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            subject_safe = self.sanitize_filename(subject[:50])
            filename = f"EMAIL_DRAFT_{to.replace('@', '_')}_{subject_safe}_{timestamp}.md"
            filepath = plans_folder / filename

            # Create content
            content = f'''---
type: email_draft
to: {to}
subject: {subject}
created: {datetime.now().isoformat()}
status: pending_review
requires_approval: {"true" if needs_approval else "false"}
{"template: " + template_name if template_name else ""}
---

## Email Draft

**To:** {to}
**Subject:** {subject}
{"**CC:** " + cc if hasattr(self, 'cc') and self.cc else ""}
{"**BCC:** " + bcc if hasattr(self, 'bcc') and self.bcc else ""}

---

**Body:**

{body}

---

## Attachments

{chr(10).join([f"- {att}" for att in attachments]) if attachments else "None"}

---

## Approval Status

{"⚠️ **Requires Approval** (new contact or has attachments)" if needs_approval else "✅ **Auto-approve OK** (known contact)"}

---

## Suggested Actions

- [ ] Review email content
- [ ] Verify attachments (if any)
- [ ] {"Approve for sending (move to Pending_Approval/)" if needs_approval else "Send directly or move to Approved/"}
- [ ] Edit if needed

---

## Notes

```
Add review notes here...
```
'''

            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f'Created draft file: {filename}')
            return filepath

        except Exception as e:
            self.logger.error(f'Failed to create draft file: {e}')
            return None

    def create_approval_request(
        self,
        draft_file: Path,
    ) -> Optional[Path]:
        """
        Create approval request from draft file.

        Args:
            draft_file: Path to draft file

        Returns:
            Path to created approval file
        """
        try:
            approval_folder = self.vault_path / 'Pending_Approval'
            approval_folder.mkdir(parents=True, exist_ok=True)

            # Read draft
            draft_content = draft_file.read_text(encoding='utf-8')

            # Parse frontmatter (simple parsing)
            import re
            match = re.search(r'^---\s*\n(.*?)\n---\s*\n', draft_content, re.DOTALL)
            frontmatter = {}
            if match:
                for line in match.group(1).split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip().strip('"\'')

            # Extract email body
            body_match = re.search(r'\*\*Body:\*\*\s*\n(.*?)\n---', draft_content, re.DOTALL)
            email_body = body_match.group(1).strip() if body_match else '[Body not found]'

            # Extract attachments
            attachments = []
            att_match = re.search(r'## Attachments\s*\n(.*?)\n---', draft_content, re.DOTALL)
            if att_match and 'None' not in att_match.group(1):
                attachments = [l.strip('- ') for l in att_match.group(1).strip().split('\n')]

            # Create approval file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"EMAIL_APPROVAL_{frontmatter.get('to', 'unknown').replace('@', '_')}_{timestamp}.md"
            filepath = approval_folder / filename

            # Calculate content hash
            content_hash = hashlib.md5(draft_content.encode()).hexdigest()

            # Determine risk level
            risk_level = 'low'
            if '$' in frontmatter.get('subject', ''):
                risk_level = 'medium'
            if any(word in frontmatter.get('subject', '').lower() for word in ['payment', 'invoice', 'contract']):
                risk_level = 'medium'

            file_content = f'''---
type: approval_request
action: email_send
to: {frontmatter.get('to', 'unknown')}
subject: {frontmatter.get('subject', 'unknown')}
content_hash: {content_hash}
created: {datetime.now().isoformat()}
status: pending
risk_level: {risk_level}
---

## Email Send Approval

**To:** {frontmatter.get('to', 'unknown')}
**Subject:** {frontmatter.get('subject', 'unknown')}
{"**Attachments:** " + str(len(attachments)) + " file(s)" if attachments else "**Attachments:** None"}

**Risk Assessment:**
{"✅ Known contact" if self._is_approved_contact(frontmatter.get('to', '')) else "⚠️ New contact"}
{"✅ Standard email" if risk_level == 'low' else "⚠️ Sensitive content"}

---

## Content Preview

{email_body}

---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder with comments.

## To Edit
Move back to Plans/ with edit notes.
'''

            filepath.write_text(file_content, encoding='utf-8')
            self.logger.info(f'Created approval request: {filename}')
            return filepath

        except Exception as e:
            self.logger.error(f'Failed to create approval request: {e}')
            return None

    def execute_approved_email(self, approval_file: Path) -> bool:
        """
        Execute an approved email send.

        Args:
            approval_file: Path to approved file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read approval file
            content = approval_file.read_text(encoding='utf-8')

            # Parse frontmatter
            import re
            match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            frontmatter = {}
            if match:
                for line in match.group(1).split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip().strip('"\'')

            # Extract email body
            body_match = re.search(r'## Content Preview\s*\n(.*?)\n---', content, re.DOTALL)
            email_body = body_match.group(1).strip() if body_match else ''

            # Extract attachments from original draft
            attachments = []
            # Look for draft file reference
            draft_name = approval_file.name.replace('EMAIL_APPROVAL_', 'EMAIL_DRAFT_').replace('.md', '*.md')
            # In production, would search for corresponding draft

            # Send email
            success, result = self.send_email(
                to=frontmatter.get('to', ''),
                subject=frontmatter.get('subject', ''),
                body=email_body,
                attachments=attachments if attachments else None,
                skip_approval=True,
            )

            if success:
                # Move to Done
                done_folder = self.vault_path / 'Done'
                done_folder.mkdir(parents=True, exist_ok=True)
                done_path = done_folder / approval_file.name
                approval_file.rename(done_path)

                self.logger.info(f'Email sent successfully: {approval_file.name}')
                return True
            else:
                self.logger.error(f'Failed to send email: {result}')
                return False

        except Exception as e:
            self.logger.error(f'Failed to execute approved email: {e}')
            return False

    def _log_email(self, email_data: Dict):
        """Log email to Accounting/Email_Log.md."""
        try:
            log_file = self.vault_path / 'Accounting' / 'Email_Log.md'
            log_file.parent.mkdir(parents=True, exist_ok=True)

            # Create or append to log
            if log_file.exists():
                content = log_file.read_text(encoding='utf-8')
            else:
                content = "# Email Log\n\n"

            # Add entry
            entry = f"""## {email_data.get('timestamp', datetime.now().isoformat())[:19]}

- **To:** {email_data.get('to', 'unknown')}
- **Subject:** {email_data.get('subject', 'unknown')}
- **Status:** {email_data.get('status', 'unknown')}
- **Message ID:** {email_data.get('message_id', 'N/A')}

"""

            content += entry
            log_file.write_text(content, encoding='utf-8')

        except Exception as e:
            self.logger.error(f'Failed to log email: {e}')

    def use_template(self, template_name: str, **kwargs) -> str:
        """
        Generate email from template.

        Args:
            template_name: Name of template to use
            **kwargs: Template variables

        Returns:
            Rendered email body
        """
        template = self.TEMPLATES.get(template_name)
        if not template:
            self.logger.error(f'Template not found: {template_name}')
            return ''

        try:
            return template.format(**kwargs)
        except KeyError as e:
            self.logger.error(f'Missing template variable: {e}')
            return template


def main():
    """Main entry point for Email MCP Client."""
    import argparse

    parser = argparse.ArgumentParser(description='Email MCP Client for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--action', choices=['send', 'draft', 'send-approved', 'auth'],
                        default='draft', help='Action to perform')
    parser.add_argument('--to', type=str, default=None, help='Recipient email')
    parser.add_argument('--cc', type=str, default=None, help='CC recipients')
    parser.add_argument('--bcc', type=str, default=None, help='BCC recipients')
    parser.add_argument('--subject', type=str, default=None, help='Email subject')
    parser.add_argument('--body', type=str, default=None, help='Email body')
    parser.add_argument('--attachment', type=str, nargs='+', default=None,
                        help='Attachment file paths')
    parser.add_argument('--file', type=str, default=None, help='Draft/approval file path')
    parser.add_argument('--template', type=str, default=None, help='Email template to use')
    parser.add_argument('--credentials', type=str, default=None,
                        help='Path to Gmail credentials.json')

    args = parser.parse_args()

    # Default credentials path
    credentials_path = args.credentials or os.getenv('GMAIL_CREDENTIALS_PATH')

    try:
        client = EmailMCPClient(
            args.vault_path,
            credentials_path=credentials_path,
        )

        if args.action == 'auth':
            # Authenticate only
            if client._authenticate():
                print('Authentication successful!')
            else:
                print('Authentication failed')
                sys.exit(1)

        elif args.action == 'draft':
            if not args.to or not args.subject:
                print('Error: --to and --subject required for draft action')
                sys.exit(1)

            # Use template if specified
            body = args.body
            if args.template:
                body = client.use_template(args.template)

            draft_file = client.create_draft_file(
                to=args.to,
                subject=args.subject,
                body=body or '',
                attachments=args.attachment,
                template_name=args.template,
            )

            if draft_file:
                print(f'Draft created: {draft_file}')

                # Check if approval needed
                if not client._is_approved_contact(args.to):
                    print('⚠️  This email requires approval. Run with --action send-approved after review.')
            else:
                print('Failed to create draft')
                sys.exit(1)

        elif args.action == 'send':
            if not args.to or not args.subject or not args.body:
                print('Error: --to, --subject, and --body required for send action')
                sys.exit(1)

            success, result = client.send_email(
                to=args.to,
                subject=args.subject,
                body=args.body,
                cc=args.cc,
                bcc=args.bcc,
                attachments=args.attachment,
            )

            if success:
                print(f'Email sent successfully! (Message ID: {result})')
            elif result == 'REQUIRES_APPROVAL':
                print('⚠️  This email requires approval.')
                print('Creating draft file for review...')
                draft_file = client.create_draft_file(
                    to=args.to,
                    subject=args.subject,
                    body=args.body,
                    attachments=args.attachment,
                )
                if draft_file:
                    print(f'Draft created: {draft_file}')
                    print('Please review and move to Pending_Approval/ when ready.')
            else:
                print(f'Failed to send email: {result}')
                sys.exit(1)

        elif args.action == 'send-approved':
            if not args.file:
                # Process all approved files
                approved_folder = Path(args.vault_path) / 'Approved'
                approved_files = list(approved_folder.glob('EMAIL_APPROVAL_*.md'))

                if not approved_files:
                    print('No approved emails found')
                else:
                    for approved_file in approved_files:
                        success = client.execute_approved_email(approved_file)
                        if success:
                            print(f'Sent: {approved_file.name}')
                        else:
                            print(f'Failed: {approved_file.name}')
            else:
                # Send specific approved email
                approval_file = Path(args.file)
                success = client.execute_approved_email(approval_file)
                if success:
                    print(f'Email sent: {approval_file.name}')
                else:
                    print('Failed to send email')
                    sys.exit(1)

    except KeyboardInterrupt:
        print('\nOperation cancelled by user')
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
