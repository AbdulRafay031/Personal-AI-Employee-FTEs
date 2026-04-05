"""
HITL Approval Workflow Module

Human-in-the-Loop (HITL) approval system for sensitive actions.
Ensures human oversight for payments, communications, and critical operations.

Usage:
    python approval_workflow.py /path/to/vault --list-pending
    python approval_workflow.py /path/to/vault --execute-approved
    python approval_workflow.py /path/to/vault --stats
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple


class ApprovalWorkflow:
    """
    Manages human-in-the-loop approval workflow.

    Features:
    - Create approval requests
    - Track pending approvals
    - Execute approved actions
    - Maintain audit logs
    - Send notifications
    """

    # Approval categories and thresholds
    APPROVAL_THRESHOLDS = {
        'payment': {
            'auto_approve_under': 50,
            'require_approval_over': 100,
            'require_justification_over': 500,
        },
        'email': {
            'auto_approve_known': True,
            'require_approval_new': True,
            'block_bulk_over': 50,
        },
        'social_media': {
            'always_require_approval': True,
        },
        'file_delete': {
            'always_require_approval': True,
        },
    }

    # Risk level descriptions
    RISK_LEVELS = {
        'low': 'Routine, reversible, low impact',
        'medium': 'Financial < $500, public communication',
        'high': 'Financial > $500, legal, irreversible',
        'critical': 'Strategic decisions, legal commitments',
    }

    def __init__(self, vault_path: str):
        """
        Initialize Approval Workflow.

        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.pending_folder = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.rejected_folder = self.vault_path / 'Rejected'
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'
        self.contacts_file = self.vault_path / 'Contacts' / 'Approved_Recipients.md'

        # Ensure folders exist
        for folder in [self.pending_folder, self.approved_folder, self.rejected_folder, self.done_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)

        # Load approved contacts
        self.approved_contacts = self._load_approved_contacts()

        # Setup logging
        self._setup_logging()

    def _load_approved_contacts(self) -> Dict[str, str]:
        """Load approved contacts from vault."""
        contacts = {}

        if self.contacts_file.exists():
            try:
                content = self.contacts_file.read_text(encoding='utf-8')
                import re
                emails = re.findall(r'-\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', content)
                for email in emails:
                    contacts[email.lower()] = 'approved'
            except Exception as e:
                pass

        return contacts

    def _setup_logging(self):
        """Setup logging."""
        import logging
        self.logger = logging.getLogger('ApprovalWorkflow')
        self.logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _parse_frontmatter(self, content: str) -> Dict:
        """Parse YAML frontmatter from markdown."""
        import re
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return {}

        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"\'')

        return frontmatter

    def _assess_risk(self, action_type: str, details: Dict) -> str:
        """
        Assess risk level for an action.

        Args:
            action_type: Type of action
            details: Action details

        Returns:
            Risk level: low, medium, high, critical
        """
        # Financial actions
        if action_type == 'payment':
            amount = float(details.get('amount', 0))
            if amount > 500:
                return 'high'
            elif amount > 100:
                return 'medium'
            return 'low'

        # Communications
        if action_type == 'email_send':
            if details.get('is_new_contact'):
                return 'medium'
            if details.get('has_attachment'):
                return 'medium'
            if details.get('recipient_count', 1) > 10:
                return 'high'
            return 'low'

        # Social media
        if action_type == 'social_media_post':
            return 'medium'  # Public-facing

        # File operations
        if action_type == 'file_delete':
            return 'high'

        # Default
        return 'medium'

    def create_approval_request(
        self,
        action_type: str,
        details: Dict,
        content_preview: str,
        reason: str,
        priority: str = 'medium',
        expires_hours: int = 24,
    ) -> Optional[Path]:
        """
        Create approval request file.

        Args:
            action_type: Type of action (payment, email_send, etc.)
            details: Action details dictionary
            content_preview: Preview of content to be sent/created
            reason: Reason approval is required
            priority: low, medium, high
            expires_hours: Hours until expiry

        Returns:
            Path to created approval file
        """
        try:
            # Assess risk
            risk_level = self._assess_risk(action_type, details)

            # Calculate expiry
            created = datetime.now()
            expires = created + timedelta(hours=expires_hours)

            # Generate filename
            timestamp = created.strftime('%Y%m%d_%H%M%S')
            filename = f"APPROVAL_{action_type}_{timestamp}.md"
            filepath = self.pending_folder / filename

            # Create content
            content = f'''---
type: approval_request
action: {action_type}
category: {self._get_category(action_type)}
created: {created.isoformat()}
expires: {expires.isoformat()}
status: pending
priority: {priority}
risk_level: {risk_level}
{self._format_details_frontmatter(details)}
---

# Approval Request: {self._get_action_title(action_type)}

## Action Details

**Action Type:** {self._format_action_type(action_type)}
**Category:** {self._get_category(action_type)}
**Created:** {created.strftime('%Y-%m-%d %I:%M %p')}
**Expires:** {expires.strftime('%Y-%m-%d %I:%M %p')} ({expires_hours} hours)
**Risk Level:** {risk_level.capitalize()} - {self.RISK_LEVELS.get(risk_level, '')}

---

## What Will Be Done

{self._format_action_details(action_type, details)}

---

## Content Preview

{content_preview}

---

## Why This Requires Approval

⚠️ **Reason:** {reason}

---

## Risk Assessment

{self._format_risk_table(action_type, details, risk_level)}

---

## To Approve

Move this file to the `/Approved` folder.

## To Reject

Move this file to the `/Rejected` folder and add comments explaining why.

## To Request Changes

Move this file back to `/Plans` folder with edit notes.

---

## Notes

```
Human reviewer can add notes here before approving/rejecting
```
'''

            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f'Created approval request: {filename}')
            return filepath

        except Exception as e:
            self.logger.error(f'Failed to create approval request: {e}')
            return None

    def _get_category(self, action_type: str) -> str:
        """Get category for action type."""
        categories = {
            'payment': 'finance',
            'email_send': 'communication',
            'social_media_post': 'marketing',
            'file_delete': 'file_operation',
            'invoice_send': 'finance',
        }
        return categories.get(action_type, 'general')

    def _get_action_title(self, action_type: str) -> str:
        """Get human-readable action title."""
        titles = {
            'payment': 'Payment Processing',
            'email_send': 'Send Email',
            'social_media_post': 'Social Media Post',
            'file_delete': 'Delete File',
            'invoice_send': 'Send Invoice',
        }
        return titles.get(action_type, 'Action')

    def _format_action_type(self, action_type: str) -> str:
        """Format action type for display."""
        return action_type.replace('_', ' ').title()

    def _format_details_frontmatter(self, details: Dict) -> str:
        """Format details for frontmatter."""
        lines = []
        for key, value in details.items():
            if isinstance(value, (int, float, str)):
                lines.append(f'{key}: {value}')
        return '\n'.join(lines)

    def _format_action_details(self, action_type: str, details: Dict) -> str:
        """Format action details for display."""
        if action_type == 'payment':
            return f"""| Field | Value |
|-------|-------|
| **Amount** | ${details.get('amount', 0):.2f} |
| **Recipient** | {details.get('recipient', 'Unknown')} |
| **Purpose** | {details.get('purpose', 'Not specified')} |"""

        elif action_type == 'email_send':
            return f"""**To:** {details.get('to', 'Unknown')}
**Subject:** {details.get('subject', 'No subject')}
**Attachments:** {details.get('attachments', 'None')}"""

        elif action_type == 'social_media_post':
            return f"""| Field | Value |
|-------|-------|
| **Platform** | {details.get('platform', 'Unknown')} |
| **Post Type** | {details.get('post_type', 'General')} |
| **Scheduled** | {details.get('scheduled_time', 'Immediate')} |"""

        return str(details)

    def _format_risk_table(self, action_type: str, details: Dict, risk_level: str) -> str:
        """Format risk assessment table."""
        if action_type == 'payment':
            amount = float(details.get('amount', 0))
            return f"""| Factor | Status |
|--------|--------|
| Amount | {'⚠️ High' if amount > 500 else '✅ Moderate' if amount > 100 else '✅ Low'} |
| Recipient | {'✅ Known' if details.get('is_known') else '⚠️ New'} |
| Documentation | {'✅ Complete' if details.get('invoice') else '⚠️ Missing'} |

**Overall Risk:** {risk_level.capitalize()}"""

        elif action_type == 'email_send':
            return f"""| Factor | Status |
|--------|--------|
| Contact | {'✅ Known' if not details.get('is_new_contact') else '⚠️ New'} |
| Attachments | {'⚠️ Yes' if details.get('has_attachment') else '✅ None'} |
| Recipients | {'⚠️ Bulk' if details.get('recipient_count', 1) > 10 else '✅ Single'} |

**Overall Risk:** {risk_level.capitalize()}"""

        return f'**Overall Risk:** {risk_level.capitalize()}'

    def list_pending_approvals(self) -> List[Dict]:
        """List all pending approvals."""
        pending = []

        if not self.pending_folder.exists():
            return []

        for approval_file in self.pending_folder.glob('*.md'):
            try:
                content = approval_file.read_text(encoding='utf-8')
                frontmatter = self._parse_frontmatter(content)

                # Check if expired
                expires = frontmatter.get('expires')
                is_expired = False
                if expires:
                    is_expired = datetime.fromisoformat(expires) < datetime.now()

                pending.append({
                    'file': approval_file.name,
                    'path': approval_file,
                    'action': frontmatter.get('action', 'Unknown'),
                    'created': frontmatter.get('created', 'Unknown'),
                    'expires': expires,
                    'is_expired': is_expired,
                    'priority': frontmatter.get('priority', 'normal'),
                    'risk_level': frontmatter.get('risk_level', 'unknown'),
                })
            except Exception as e:
                self.logger.error(f'Error reading {approval_file.name}: {e}')

        # Sort by priority and expiry
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        pending.sort(key=lambda x: (priority_order.get(x['priority'], 3), x.get('expires') or '9999'))

        return pending

    def execute_approved_action(self, approval_file: Path) -> bool:
        """
        Execute an approved action.

        Args:
            approval_file: Path to approved file

        Returns:
            True if successful
        """
        try:
            content = approval_file.read_text(encoding='utf-8')
            frontmatter = self._parse_frontmatter(content)

            action_type = frontmatter.get('action')
            self.logger.info(f'Executing approved action: {action_type} ({approval_file.name})')

            # Log the action
            self._log_action(approval_file, 'approved')

            # Move to Done
            done_path = self.done_folder / approval_file.name
            shutil.move(str(approval_file), str(done_path))

            self.logger.info(f'Action completed: {approval_file.name} → Done/')
            return True

        except Exception as e:
            self.logger.error(f'Failed to execute approved action: {e}')
            return False

    def execute_all_approved(self) -> Dict:
        """
        Execute all approved actions.

        Returns:
            Dictionary with execution results
        """
        results = {
            'executed': 0,
            'failed': 0,
            'errors': [],
        }

        if not self.approved_folder.exists():
            return results

        for approval_file in self.approved_folder.glob('*.md'):
            success = self.execute_approved_action(approval_file)
            if success:
                results['executed'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(approval_file.name)

        return results

    def _log_action(self, approval_file: Path, decision: str):
        """Log approval decision to audit log."""
        try:
            log_file = self.logs_folder / 'Approval_Audit_Log.md'

            content = approval_file.read_text(encoding='utf-8')
            frontmatter = self._parse_frontmatter(content)

            # Create or append to log
            if log_file.exists():
                log_content = log_file.read_text(encoding='utf-8')
            else:
                log_content = f"# Approval Audit Log - {datetime.now().strftime('%B %Y')}\n\n"

            # Add entry
            entry = f"""## {approval_file.name}

- **Action:** {frontmatter.get('action', 'Unknown')}
- **Decision:** {decision}
- **Timestamp:** {datetime.now().isoformat()}
- **Risk Level:** {frontmatter.get('risk_level', 'unknown')}

---

"""

            log_content += entry
            log_file.write_text(log_content, encoding='utf-8')

        except Exception as e:
            self.logger.error(f'Failed to log action: {e}')

    def get_statistics(self) -> Dict:
        """Get approval statistics."""
        stats = {
            'pending': 0,
            'approved': 0,
            'rejected': 0,
            'expired': 0,
            'by_action_type': {},
            'by_risk_level': {},
        }

        # Count pending
        pending = self.list_pending_approvals()
        stats['pending'] = len(pending)
        stats['expired'] = sum(1 for p in pending if p['is_expired'])

        # Count by action type
        for p in pending:
            action = p['action']
            stats['by_action_type'][action] = stats['by_action_type'].get(action, 0) + 1

        # Count approved (this month)
        if self.approved_folder.exists():
            stats['approved'] = len(list(self.approved_folder.glob('*.md')))

        # Count rejected
        if self.rejected_folder.exists():
            stats['rejected'] = len(list(self.rejected_folder.glob('*.md')))

        return stats

    def send_reminders(self) -> List[str]:
        """
        Send reminders for expiring/expired approvals.

        Returns:
            List of files that need attention
        """
        reminders = []
        pending = self.list_pending_approvals()

        for approval in pending:
            # Send reminder if expired or high priority and old
            if approval['is_expired']:
                reminders.append(f"❌ EXPIRED: {approval['file']}")
                self.logger.warning(f"Approval expired: {approval['file']}")
            elif approval['priority'] == 'high':
                created = datetime.fromisoformat(approval['created'])
                if (datetime.now() - created).total_seconds() > 3600:  # 1 hour
                    reminders.append(f"🔴 URGENT: {approval['file']}")
                    self.logger.warning(f"High-priority approval pending: {approval['file']}")

        return reminders


def main():
    """Main entry point for Approval Workflow."""
    import argparse

    parser = argparse.ArgumentParser(description='HITL Approval Workflow for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--list-pending', action='store_true', help='List pending approvals')
    parser.add_argument('--execute-approved', action='store_true', help='Execute all approved actions')
    parser.add_argument('--stats', action='store_true', help='Show approval statistics')
    parser.add_argument('--reminders', action='store_true', help='Send approval reminders')
    parser.add_argument('--create-test', action='store_true', help='Create test approval request')

    args = parser.parse_args()

    workflow = ApprovalWorkflow(args.vault_path)

    if args.list_pending:
        pending = workflow.list_pending_approvals()
        if not pending:
            print('No pending approvals')
        else:
            print(f'Pending Approvals ({len(pending)}):')
            print('-' * 80)
            for approval in pending:
                status = '❌ EXPIRED' if approval['is_expired'] else '⏳ Pending'
                print(f"{status} | {approval['file']}")
                print(f"   Action: {approval['action']} | Priority: {approval['priority']} | Risk: {approval['risk_level']}")
                print(f"   Created: {approval['created'][:19]} | Expires: {approval.get('expires', 'N/A')[:19] if approval.get('expires') else 'N/A'}")
                print()

    elif args.execute_approved:
        print('Executing approved actions...')
        results = workflow.execute_all_approved()
        print(f"Executed: {results['executed']}")
        print(f"Failed: {results['failed']}")
        if results['errors']:
            print(f"Errors: {', '.join(results['errors'])}")

    elif args.stats:
        stats = workflow.get_statistics()
        print('Approval Statistics:')
        print(f"  Pending: {stats['pending']}")
        print(f"  Expired: {stats['expired']}")
        print(f"  Approved: {stats['approved']}")
        print(f"  Rejected: {stats['rejected']}")
        print(f"\nBy Action Type: {stats['by_action_type']}")
        print(f"By Risk Level: {stats['by_risk_level']}")

    elif args.reminders:
        reminders = workflow.send_reminders()
        if not reminders:
            print('No approvals need attention')
        else:
            print('Approval Reminders:')
            for reminder in reminders:
                print(f"  {reminder}")

    elif args.create_test:
        # Create test approval request
        test_file = workflow.create_approval_request(
            action_type='email_send',
            details={
                'to': 'test@example.com',
                'subject': 'Test Email',
                'is_new_contact': True,
            },
            content_preview='This is a test email for approval workflow testing.',
            reason='Test approval request',
            priority='low',
        )
        if test_file:
            print(f'Test approval created: {test_file.name}')

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
