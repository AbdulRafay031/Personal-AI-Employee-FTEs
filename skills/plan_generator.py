"""
Plan Generator Module

Automatically generates structured Plan.md files for complex multi-step tasks.
Enables Claude Code to break down tasks into actionable steps with checkboxes.

Usage:
    python plan_generator.py /path/to/vault --auto-generate
    python plan_generator.py /path/to/vault --task-file "Needs_Action/WHATSAPP_client.md"
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class PlanGenerator:
    """
    Generates and manages Plan.md files for task tracking.

    Features:
    - Automatic plan generation from task files
    - Progress tracking via checkboxes
    - Approval step detection
    - Plan templates for common task types
    """

    # Plan templates for different task types
    TEMPLATES = {
        'invoice_request': '''---
type: plan
category: finance
task: {task_title}
created: {timestamp}
status: pending
priority: high
estimated_steps: 9
completed_steps: 0
source_file: {source_file}
---

# Plan: {task_title}

## Objective
Generate and send invoice to {client_name} for {service_type}.

## Context
- **Client:** {client_name} ({client_email})
- **Amount:** {amount}
- **Service:** {service_type}
- **Requested via:** {communication_channel}
- **Payment Terms:** Net 30

## Steps

- [ ] Read message and extract invoice request
- [ ] Identify client details (email, billing info)
- [ ] Verify client exists in approved contacts
- [ ] Generate invoice PDF
- [ ] Create email draft with invoice attachment
- [ ] Request approval (HITL required for new invoice)
- [ ] Send email after approval
- [ ] Log transaction to Accounting/Current_Month.md
- [ ] Move task to Done/

## Approval Required

| Step | Action | Reason |
|------|--------|--------|
| 6 | Send invoice email | Financial transaction requires human verification |

## Notes

```
{initial_notes}
```

## Related Files

- **Source:** `Needs_Action/{source_filename}`
- **Invoice:** `Invoices/` (to be created)
- **Draft:** `Plans/EMAIL_DRAFT_*.md` (to be created)
- **Approval:** `Pending_Approval/EMAIL_APPROVAL_*.md` (to be created)
''',

        'email_response': '''---
type: plan
category: communication
task: {task_title}
created: {timestamp}
status: pending
priority: {priority}
estimated_steps: 7
completed_steps: 0
source_file: {source_file}
---

# Plan: {task_title}

## Objective
Draft and send response to email from {sender_name} regarding {subject}.

## Context
- **Sender:** {sender_name} ({sender_email})
- **Subject:** {subject}
- **Received:** {received_date}
- **Priority:** {priority_level}
- **Contact Type:** {contact_type}

## Steps

- [ ] Read and understand email content
- [ ] Determine response needed
- [ ] Draft response
- [ ] {approval_step}
- [ ] Send response
- [ ] Archive original email
- [ ] Move task to Done/

## Approval Required

{approval_table}

## Draft Points

{draft_points}

## Notes

```
{initial_notes}
```

## Related Files

- **Source:** `Needs_Action/{source_filename}`
''',

        'whatsapp_response': '''---
type: plan
category: communication
task: {task_title}
created: {timestamp}
status: pending
priority: {priority}
estimated_steps: 6
completed_steps: 0
---

# Plan: {task_title}

## Objective
Respond to WhatsApp message from {contact_name}.

## Context
- **Contact:** {contact_name}
- **Message:** {message_preview}
- **Received:** {received_date}
- **Priority:** {priority_level}
- **Keywords Detected:** {keywords}

## Steps

- [ ] Read WhatsApp message
- [ ] Determine appropriate response
- [ ] Draft response message
- [ ] {approval_step}
- [ ] Send response via WhatsApp
- [ ] Mark message as read
- [ ] Move task to Done/

## Approval Required

{approval_table}

## Notes

```
{initial_notes}
```
''',

        'social_media_post': '''---
type: plan
category: marketing
task: {task_title}
created: {timestamp}
status: pending
priority: medium
estimated_steps: 9
completed_steps: 0
---

# Plan: {task_title}

## Objective
Create and publish {post_type} post about {topic} on {platform}.

## Context
- **Platform:** {platform}
- **Post Type:** {post_type}
- **Topic:** {topic}
- **Goal:** {engagement_goal}

## Steps

- [ ] Research topic and gather key points
- [ ] Draft post content
- [ ] Add relevant hashtags
- [ ] Review brand voice alignment
- [ ] Create approval request
- [ ] Schedule/post after approval
- [ ] Monitor engagement (first 24h)
- [ ] Respond to comments (if needed)
- [ ] Log to analytics
- [ ] Move task to Done/

## Approval Required

| Step | Action | Reason |
|------|--------|--------|
| 5 | Publish post | All social media posts require human approval |

## Content Guidelines

- **Tone:** {brand_tone}
- **Hashtags:** 3-5 relevant
- **Emojis:** Moderate (2-4)
- **Call-to-action:** Include

## Notes

```
{initial_notes}
```
''',

        'file_processing': '''---
type: plan
category: document
task: {task_title}
created: {timestamp}
status: pending
priority: {priority}
estimated_steps: 6
completed_steps: 0
---

# Plan: {task_title}

## Objective
Process and categorize file: {filename}.

## Context
- **File:** {filename}
- **Category:** {file_category}
- **Size:** {file_size}
- **Received:** {received_date}

## Steps

- [ ] Read file content (if text-based)
- [ ] Determine file category and purpose
- [ ] Extract key information
- [ ] Move to appropriate vault folder
- [ ] Create metadata/notes if needed
- [ ] Log to Dashboard
- [ ] Move task to Done/

## Notes

```
{initial_notes}
```
''',

        'general': '''---
type: plan
category: general
task: {task_title}
created: {timestamp}
status: pending
priority: {priority}
estimated_steps: 5
completed_steps: 0
source_file: {source_file}
---

# Plan: {task_title}

## Objective
{objective}

## Context
{context}

## Steps

- [ ] Analyze task requirements
- [ ] Determine required actions
- [ ] Execute actions
- [ ] {approval_step}
- [ ] Verify completion
- [ ] Move task to Done/

## Approval Required

{approval_table}

## Notes

```
{initial_notes}
```

## Related Files

- **Source:** `Needs_Action/{source_filename}`
''',
    }

    def __init__(self, vault_path: str):
        """
        Initialize Plan Generator.

        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.plans_folder = self.vault_path / 'Plans'
        self.needs_action_folder = self.vault_path / 'Needs_Action'
        self.contacts_file = self.vault_path / 'Contacts' / 'Approved_Recipients.md'

        # Ensure folders exist
        self.plans_folder.mkdir(parents=True, exist_ok=True)

        # Load approved contacts
        self.approved_contacts = self._load_approved_contacts()

    def _load_approved_contacts(self) -> Dict[str, str]:
        """Load approved contacts from vault."""
        contacts = {}

        if self.contacts_file.exists():
            try:
                content = self.contacts_file.read_text(encoding='utf-8')
                emails = re.findall(r'-\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', content)
                for email in emails:
                    contacts[email.lower()] = 'approved'
            except Exception:
                pass

        return contacts

    def _parse_frontmatter(self, content: str) -> Dict:
        """Parse YAML frontmatter from markdown."""
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return {}

        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"\'')

        return frontmatter

    def _detect_task_type(self, task_file: Path) -> str:
        """Detect task type from file content."""
        content = task_file.read_text(encoding='utf-8')
        frontmatter = self._parse_frontmatter(content)

        task_type = frontmatter.get('type', 'general').lower()

        # Refine based on content
        content_lower = content.lower()

        if task_type == 'email':
            if 'invoice' in content_lower or 'payment' in content_lower:
                return 'invoice_request'
            return 'email_response'

        elif task_type == 'whatsapp':
            if 'invoice' in content_lower or 'payment' in content_lower:
                return 'invoice_request'
            return 'whatsapp_response'

        elif task_type == 'file_drop':
            if 'invoice' in content_lower:
                return 'invoice_request'
            return 'file_processing'

        elif 'linkedin' in content_lower or 'social' in content_lower:
            return 'social_media_post'

        return 'general'

    def _extract_task_info(self, task_file: Path) -> Dict:
        """Extract task information for plan generation."""
        content = task_file.read_text(encoding='utf-8')
        frontmatter = self._parse_frontmatter(content)

        info = {
            'task_title': frontmatter.get('subject', frontmatter.get('type', 'Unknown Task')),
            'timestamp': datetime.now().isoformat(),
            'source_file': f"Needs_Action/{task_file.name}",
            'source_filename': task_file.name,
            'priority': frontmatter.get('priority', 'medium'),
            'priority_level': frontmatter.get('priority', 'medium').capitalize(),
            'initial_notes': f"{datetime.now().strftime('%Y-%m-%d %H:%M')}: Plan created",
        }

        # Extract specific fields based on type
        if frontmatter.get('type') == 'email':
            info['sender_name'] = frontmatter.get('sender', 'Unknown')
            info['sender_email'] = frontmatter.get('sender_email', '')
            info['subject'] = frontmatter.get('subject', 'No Subject')
            info['received_date'] = frontmatter.get('received', '')
            info['contact_type'] = 'New' if info['sender_email'] not in self.approved_contacts else 'Known'
            info['approval_step'] = 'Request approval (new contact)' if info['contact_type'] == 'New' else 'Send directly'
            info['draft_points'] = '- Review email content\n- Draft appropriate response'
            info['approval_table'] = '| 4 | Send response | ' + ('New contact requires human review' if info['contact_type'] == 'New' else 'Standard approval') + ' |'

        elif frontmatter.get('type') == 'whatsapp':
            info['contact_name'] = frontmatter.get('sender', 'Unknown')
            info['message_preview'] = content[:200] + '...' if len(content) > 200 else content
            info['received_date'] = frontmatter.get('received', '')
            info['keywords'] = frontmatter.get('keywords', 'none')

        return info

    def _requires_approval(self, task_type: str, info: Dict) -> bool:
        """Determine if task requires human approval."""
        # Financial tasks always require approval
        if task_type in ['invoice_request']:
            return True

        # New contact emails
        if info.get('contact_type') == 'New':
            return True

        # Social media posts
        if task_type == 'social_media_post':
            return True

        # Check for large amounts
        content_lower = str(info).lower()
        if '$' in content_lower:
            amounts = re.findall(r'\$[\d,]+', content_lower)
            for amount in amounts:
                try:
                    value = float(amount.replace('$', '').replace(',', ''))
                    if value > 100:
                        return True
                except ValueError:
                    pass

        return False

    def generate_plan(self, task_file: Path, template_name: str = None) -> Optional[Path]:
        """
        Generate Plan.md file for a task.

        Args:
            task_file: Path to task file in Needs_Action
            template_name: Specific template to use (auto-detected if None)

        Returns:
            Path to created plan file
        """
        try:
            # Detect task type
            task_type = template_name or self._detect_task_type(task_file)

            # Extract task info
            info = self._extract_task_info(task_file)

            # Get template
            template = self.TEMPLATES.get(task_type, self.TEMPLATES['general'])

            # Fill template
            plan_content = template.format(**info)

            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            task_title_safe = self.sanitize_filename(info['task_title'][:50])
            filename = f"Plan_{task_title_safe}_{timestamp}.md"
            filepath = self.plans_folder / filename

            # Write file
            filepath.write_text(plan_content, encoding='utf-8')

            return filepath

        except Exception as e:
            print(f"Error generating plan: {e}")
            return None

    def update_plan_progress(self, plan_file: Path) -> bool:
        """
        Update plan progress based on completed steps.

        Args:
            plan_file: Path to plan file

        Returns:
            True if updated successfully
        """
        try:
            content = plan_file.read_text(encoding='utf-8')

            # Count checkboxes
            all_checkboxes = re.findall(r'- \[.\]', content)
            completed_checkboxes = re.findall(r'- \[x\]', content)

            total = len(all_checkboxes)
            completed = len(completed_checkboxes)

            if total == 0:
                return False

            # Update frontmatter
            content = re.sub(
                r'completed_steps: \d+',
                f'completed_steps: {completed}',
                content
            )
            content = re.sub(
                r'estimated_steps: \d+',
                f'estimated_steps: {total}',
                content
            )

            # Check if complete
            if completed == total:
                content = re.sub(
                    r'status: \w+',
                    'status: completed',
                    content
                )
                # Add completion timestamp if not already present
                if '**Completed:**' not in content:
                    content += f'\n\n**Completed:** {datetime.now().isoformat()}\n'

            plan_file.write_text(content, encoding='utf-8')
            return True

        except Exception as e:
            print(f"Error updating plan: {e}")
            return False

    def is_plan_complete(self, plan_file: Path) -> bool:
        """Check if plan is complete."""
        try:
            content = plan_file.read_text(encoding='utf-8')

            # Check status
            frontmatter = self._parse_frontmatter(content)
            if frontmatter.get('status') == 'completed':
                return True

            # Check checkboxes
            all_checkboxes = re.findall(r'- \[.\]', content)
            completed_checkboxes = re.findall(r'- \[x\]', content)

            return len(all_checkboxes) > 0 and len(all_checkboxes) == len(completed_checkboxes)

        except Exception:
            return False

    def sanitize_filename(self, name: str) -> str:
        """Sanitize string for use as filename."""
        invalid_chars = '<>:"/\\|？*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name[:100]


def main():
    """Main entry point for Plan Generator."""
    import argparse

    parser = argparse.ArgumentParser(description='Plan Generator for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--task-file', type=str, default=None,
                        help='Specific task file to process')
    parser.add_argument('--update-plan', type=str, default=None,
                        help='Update existing plan progress')
    parser.add_argument('--auto-generate', action='store_true',
                        help='Auto-generate plans for all Needs_Action tasks')
    parser.add_argument('--dry-run', action='store_true',
                        help='Generate plan without saving')

    args = parser.parse_args()

    generator = PlanGenerator(args.vault_path)

    if args.update_plan:
        # Update existing plan
        plan_file = Path(args.update_plan)
        if not plan_file.exists():
            print(f'Plan file not found: {plan_file}')
            sys.exit(1)

        success = generator.update_plan_progress(plan_file)
        if success:
            print(f'Plan updated: {plan_file.name}')
            if generator.is_plan_complete(plan_file):
                print('✓ Plan is complete!')
        else:
            print('Failed to update plan')
            sys.exit(1)

    elif args.task_file:
        # Generate plan for specific task
        task_file = Path(args.task_file)
        if not task_file.exists():
            print(f'Task file not found: {task_file}')
            sys.exit(1)

        if args.dry_run:
            print('Dry run mode - generating plan preview...')
            # Would generate and print without saving
        else:
            plan_file = generator.generate_plan(task_file)
            if plan_file:
                print(f'Plan generated: {plan_file.name}')
            else:
                print('Failed to generate plan')
                sys.exit(1)

    elif args.auto_generate:
        # Generate plans for all tasks in Needs_Action
        if not generator.needs_action_folder.exists():
            print('Needs_Action folder not found')
            sys.exit(1)

        task_files = list(generator.needs_action_folder.glob('*.md'))

        if not task_files:
            print('No tasks found in Needs_Action folder')
        else:
            print(f'Found {len(task_files)} tasks to process')

            for task_file in task_files:
                plan_file = generator.generate_plan(task_file)
                if plan_file:
                    print(f'  ✓ {task_file.name} → {plan_file.name}')
                else:
                    print(f'  ✗ {task_file.name} → Failed')

            print(f'\nGenerated {len([f for f in generator.plans_folder.glob("*.md")])} plans total')

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
