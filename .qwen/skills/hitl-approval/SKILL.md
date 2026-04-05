# HITL Approval Workflow Skill

Human-in-the-Loop (HITL) approval system for sensitive actions. Ensures human oversight for payments, communications, and other critical operations.

## Overview

This skill enables your AI Employee to:
- Automatically detect actions requiring human approval
- Create structured approval request files
- Track approval status and history
- Execute approved actions safely
- Maintain audit logs of all approvals

## Architecture

```
AI detects sensitive action
        ↓
Creates Approval Request File
        ↓
Pending_Approval/
        ↓
Human reviews and moves to:
├── Approved/ → Execute action → Done/
├── Rejected/ → Log rejection → Done/
└── Plans/ → Needs edits → Revise
```

## Approval Categories

### Category 1: Financial Transactions

| Action | Threshold | Approval Required |
|--------|-----------|-------------------|
| Payment to known vendor | < $50 | Auto-approve |
| Payment to known vendor | $50-$500 | Require approval |
| Payment to known vendor | > $500 | Require approval + justification |
| Payment to new vendor | Any amount | Require approval |
| Invoice generation | Any amount | Require approval |
| Refund processing | Any amount | Require approval |

### Category 2: Communications

| Action | Condition | Approval Required |
|--------|-----------|-------------------|
| Email to known contact | Routine | Auto-approve |
| Email to new contact | First email | Require approval |
| Email with attachment | Any | Require approval |
| Bulk email (>10 recipients) | Any | Require approval |
| Social media post | Any | Require approval |
| WhatsApp reply | Routine | Auto-approve |
| WhatsApp reply | Sensitive topic | Require approval |

### Category 3: File Operations

| Action | Condition | Approval Required |
|--------|-----------|-------------------|
| Create file in vault | Any | Auto-approve |
| Move file within vault | Any | Auto-approve |
| Delete file | Any | Require approval |
| Export data outside vault | Any | Require approval |
| Modify system config | Any | Require approval |

## Approval Request File Format

### Standard Template

```markdown
---
type: approval_request
action: email_send
category: communication
created: 2026-01-07T10:30:00Z
expires: 2026-01-08T10:30:00Z
status: pending
priority: medium
risk_level: low
---

# Approval Request: Send Email to Client

## Action Details

**Action Type:** Email Send
**Category:** Communication
**Created:** 2026-01-07 10:30 AM
**Expires:** 2026-01-08 10:30 AM (24 hours)
**Risk Level:** Low

---

## What Will Be Done

**To:** client@example.com
**Subject:** Invoice #123 - January 2026
**Attachments:** 1 file (invoice.pdf)

---

## Content Preview

Dear Client,

Please find attached invoice #123 for $1,500 for consulting services in January 2026.

Invoice Details:
- Services: Consulting
- Amount: $1,500
- Due Date: January 31, 2026

Payment can be made via bank transfer or credit card.

Best regards,
Your Company

---

## Why This Requires Approval

⚠️ **Reason:** Financial transaction (invoice send)

This action requires human approval because:
- Involves sending financial document
- Contains payment information
- Represents business transaction

---

## Risk Assessment

| Factor | Status |
|--------|--------|
| Known contact | ✅ Yes |
| Standard amount | ✅ Yes ($1,500) |
| Proper documentation | ✅ Yes |
| Within policy | ✅ Yes |

**Overall Risk:** Low

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
```

### Payment Approval Example

```markdown
---
type: approval_request
action: payment
category: finance
created: 2026-01-07T14:00:00Z
expires: 2026-01-08T14:00:00Z
status: pending
priority: high
risk_level: medium
amount: 2500.00
currency: USD
recipient: AWS (aws.amazon.com)
---

# Approval Request: Payment to AWS

## Payment Details

| Field | Value |
|-------|-------|
| **Amount** | $2,500.00 USD |
| **Recipient** | AWS (Amazon Web Services) |
| **Account** | ****1234 (Business Checking) |
| **Purpose** | Monthly cloud infrastructure |
| **Due Date** | January 15, 2026 |
| **Invoice** | AWS-INV-2026-01 |

---

## Why This Requires Approval

⚠️ **Reason:** Payment > $100 to recurring vendor

This action requires human approval because:
- Amount exceeds $100 threshold
- Business expense requires verification
- Monthly recurring charge audit

---

## Verification Checklist

- [x] Invoice received and verified
- [x] Service usage matches expected
- [x] Account balance sufficient
- [ ] **Your approval needed**

---

## Risk Assessment

| Factor | Status |
|--------|--------|
| Known vendor | ✅ Yes (recurring) |
| Invoice verified | ✅ Yes |
| Within budget | ✅ Yes |
| Unusual amount | ⚠️ 20% higher than last month |

**Overall Risk:** Medium (due to amount increase)

---

## Vendor History

| Month | Amount |
|-------|--------|
| Dec 2025 | $2,083 |
| Nov 2025 | $2,156 |
| Oct 2025 | $1,987 |

**Note:** 20% increase due to holiday traffic

---

## To Approve

Move this file to the `/Approved` folder.

Payment will be processed within 24 hours of approval.

## To Reject

Move this file to the `/Rejected` folder with comments.

Example rejection reasons:
- "Invoice discrepancy - contact vendor"
- "Insufficient funds - delay payment"
- "Service no longer needed - cancel"

---

## Notes

```
Add any special instructions or concerns here
```
```

### Social Media Post Approval

```markdown
---
type: approval_request
action: social_media_post
category: marketing
platform: LinkedIn
created: 2026-01-07T09:00:00Z
scheduled_time: 2026-01-07T12:00:00Z
status: pending
risk_level: low
---

# Approval Request: LinkedIn Post

## Post Details

| Field | Value |
|-------|-------|
| **Platform** | LinkedIn |
| **Post Type** | Achievement |
| **Scheduled** | January 7, 2026 at 12:00 PM PST |
| **Estimated Reach** | 500-1,000 impressions |

---

## Content Preview

🎉 Excited to share our Q4 achievements!

This quarter, we've:
✅ Completed 15 client projects
✅ Achieved 98% client satisfaction
✅ Grew team by 40%

Thank you to our amazing clients and partners!

#Business #Growth #Q4Results #Success

---

## Why This Requires Approval

⚠️ **Reason:** All social media posts require human approval

This action requires human approval because:
- Public-facing content
- Represents company brand
- May attract media attention

---

## Content Checklist

- [x] Facts verified (numbers accurate)
- [x] Brand voice aligned
- [x] No sensitive information
- [x] Hashtags relevant
- [ ] **Your approval needed**

---

## To Approve

Move this file to the `/Approved` folder.

Post will be published at scheduled time.

## To Reject

Move this file to the `/Rejected` folder with edit suggestions.

---

## Notes

```

```
```

## Usage

### Basic Workflow

```bash
# 1. AI creates approval request
# File appears in: Pending_Approval/APPROVAL_REQUEST_*.md

# 2. Human reviews files
ls Pending_Approval/

# 3. Human moves file based on decision
mv Pending_Approval/APPROVAL_*.md Approved/   # To approve
mv Pending_Approval/APPROVAL_*.md Rejected/   # To reject
mv Pending_Approval/APPROVAL_*.md Plans/      # Needs edits

# 4. Orchestrator detects and executes
python approval_workflow.py /vault --execute-approved
```

### Command Line Interface

```bash
# List pending approvals
python approval_workflow.py /vault --list-pending

# Review specific approval
python approval_workflow.py /vault --review "APPROVAL_email_*.md"

# Execute all approved actions
python approval_workflow.py /vault --execute-approved

# Show approval statistics
python approval_workflow.py /vault --stats

# Send reminder for expiring approvals
python approval_workflow.py /vault --send-reminders
```

## Integration with Orchestrator

### Auto-Detection

```python
# In orchestrator.py
def check_pending_approvals(self):
    """Check for expired or urgent approvals."""
    approval_folder = self.vault_path / 'Pending_Approval'
    
    for approval_file in approval_folder.glob('*.md'):
        content = approval_file.read_text()
        frontmatter = self._parse_frontmatter(content)
        
        # Check expiry
        expires = frontmatter.get('expires')
        if expires and datetime.fromisoformat(expires) < datetime.now():
            self.logger.warning(f'Approval expired: {approval_file.name}')
            self._notify_human(f'Approval expired: {approval_file.name}')
        
        # Check priority
        if frontmatter.get('priority') == 'high':
            created = datetime.fromisoformat(frontmatter.get('created'))
            if (datetime.now() - created).total_seconds() > 3600:  # 1 hour
                self.logger.warning(f'High-priority approval pending: {approval_file.name}')
```

### Execution Handler

```python
def execute_approved_action(self, approval_file: Path) -> bool:
    """Execute an approved action."""
    content = approval_file.read_text(encoding='utf-8')
    frontmatter = self._parse_frontmatter(content)
    
    action_type = frontmatter.get('action')
    
    if action_type == 'email_send':
        return self._execute_email_send(approval_file)
    elif action_type == 'payment':
        return self._execute_payment(approval_file)
    elif action_type == 'social_media_post':
        return self._execute_social_post(approval_file)
    else:
        self.logger.error(f'Unknown action type: {action_type}')
        return False
```

## Risk Assessment Matrix

### Risk Levels

| Level | Description | Examples |
|-------|-------------|----------|
| **Low** | Routine, reversible, low impact | Email to known contact, file organization |
| **Medium** | Financial < $500, public communication | Invoice send, social media post |
| **High** | Financial > $500, legal, irreversible | Large payment, contract signing |
| **Critical** | Strategic decisions, legal commitments | Partnership agreements, major expenses |

### Auto-Assessment Rules

```python
def assess_risk(action_type: str, details: Dict) -> str:
    """Automatically assess risk level."""
    
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
    
    # Default
    return 'medium'
```

## Approval Notifications

### Email Notification

```python
def send_approval_notification(approval_file: Path, method: str = 'email'):
    """Send notification for pending approval."""
    content = approval_file.read_text()
    frontmatter = _parse_frontmatter(content)
    
    subject = f"Approval Required: {frontmatter.get('action', 'Action')} ({frontmatter.get('priority', 'normal')})"
    
    body = f"""
A new action requires your approval:

**Action:** {frontmatter.get('action')}
**Created:** {frontmatter.get('created')}
**Expires:** {frontmatter.get('expires')}
**Risk Level:** {frontmatter.get('risk_level')}

File location: Pending_Approval/{approval_file.name}

To approve: Move to /Approved folder
To reject: Move to /Rejected folder
"""
    
    send_email(to='human@example.com', subject=subject, body=body)
```

### WhatsApp Notification

```python
def send_whatsapp_notification(approval_file: Path):
    """Send urgent approval notification via WhatsApp."""
    content = approval_file.read_text()
    frontmatter = _parse_frontmatter(content)
    
    if frontmatter.get('priority') == 'high':
        message = f"""
🔴 URGENT APPROVAL NEEDED

Action: {frontmatter.get('action')}
Priority: {frontmatter.get('priority')}
Expires: {frontmatter.get('expires')}

Please review in Pending_Approval folder.
"""
        send_whatsapp(to='human_number', text=message)
```

## Audit Logging

### Approval Log Format

```markdown
# Approval Audit Log - January 2026

## Approved Actions

| Date | Action | Type | Risk | Approved By | Notes |
|------|--------|------|------|-------------|-------|
| Jan 7 10:45 | Email to Client A | email_send | low | Human | Routine invoice |
| Jan 7 14:30 | Payment to AWS | payment | medium | Human | Monthly infra |
| Jan 7 15:00 | LinkedIn Post | social_post | low | Human | Q4 achievements |

## Rejected Actions

| Date | Action | Type | Reason |
|------|--------|------|--------|
| Jan 5 09:00 | Payment to Vendor X | payment | Invoice discrepancy |

## Statistics

- **Total Approvals:** 15
- **Approved:** 14 (93%)
- **Rejected:** 1 (7%)
- **Average Review Time:** 2.3 hours
```

### Log Entry Function

```python
def log_approval_decision(approval_file: Path, decision: str, notes: str = ''):
    """Log approval decision to audit log."""
    log_file = vault_path / 'Logs' / 'Approval_Audit_Log.md'
    
    content = approval_file.read_text()
    frontmatter = _parse_frontmatter(content)
    
    entry = f"""
| {datetime.now().strftime('%b %d %H:%M')} | {frontmatter.get('action', 'Unknown')} | {frontmatter.get('action_type', 'N/A')} | {frontmatter.get('risk_level', 'N/A')} | Human | {notes[:50]} |
"""
    
    if log_file.exists():
        log_content = log_file.read_text()
        # Insert after header
        log_content = log_content.replace('## Approved Actions\n', f'## Approved Actions\n{entry}')
    else:
        log_content = f"# Approval Audit Log - {datetime.now().strftime('%B %Y')}\n\n## Approved Actions\n{entry}\n"
    
    log_file.write_text(log_content)
```

## Best Practices

### For Humans Reviewing Approvals

1. **Review within 24 hours** - Don't let approvals expire
2. **Check all details** - Verify amounts, recipients, content
3. **Add notes** - Document why you approved/rejected
4. **Be consistent** - Apply same standards each time
5. **Escalate if unsure** - When in doubt, seek second opinion

### For AI Creating Approval Requests

1. **Be specific** - Clearly state what will be done
2. **Provide context** - Explain why this action is needed
3. **Assess risk honestly** - Don't downplay risks
4. **Include all details** - Attach relevant files, links
5. **Set reasonable expiry** - Give human enough time to review

### Approval File Organization

```
Pending_Approval/
├── FINANCE_*.md       # Payment approvals
├── EMAIL_*.md         # Email send approvals
├── SOCIAL_*.md        # Social media approvals
└── FILE_*.md          # File operation approvals

Approved/
├── 2026-01/           # Organize by month
│   ├── EMAIL_*.md
│   └── FINANCE_*.md
└── 2025-12/

Rejected/
└── (same structure)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Approval not detected | Check file has valid frontmatter with `type: approval_request` |
| Action not executing | Verify file moved to Approved/ folder |
| Wrong risk level | Manually edit risk_level in frontmatter |
| Approval expired | Create new approval request with updated info |
| Notification not sent | Check notification configuration |

## Advanced Features

### Bulk Approval

```markdown
---
type: bulk_approval_request
category: finance
created: 2026-01-07T10:00:00Z
actions_count: 5
total_amount: 3750.00
---

# Bulk Approval: Weekly Vendor Payments

## Summary

Approve 5 vendor payments totaling $3,750.00

## Actions

1. Payment to AWS - $2,500 (monthly infrastructure)
2. Payment to Adobe - $60 (monthly software)
3. Payment to Office 365 - $15 (monthly software)
4. Payment to Internet Provider - $175 (monthly)
5. Payment to Cleaning Service - $1,000 (monthly)

## To Approve All

Move this file to /Approved folder.

## To Review Individually

Files moved to individual approval requests in Pending_Approval/
```

### Delegation Rules

```python
# Delegation configuration
DELEGATION_RULES = {
    'payment': {
        'auto_approve_under': 50,  # Auto-approve payments under $50
        'require_approval_over': 100,  # Require approval over $100
        'require_justification_over': 500,  # Require written justification
    },
    'email': {
        'auto_approve_known': True,  # Auto-approve emails to known contacts
        'require_approval_new': True,  # Require approval for new contacts
        'block_bulk_over': 50,  # Block bulk emails over 50 recipients
    }
}
```

## Related Skills

- **email-mcp:** Email sending with approval
- **plan-generator:** Task planning with approval steps
- **whatsapp-watcher:** Message monitoring
- **linkedin-poster:** Social media with approval

## Next Steps

After setting up HITL workflow:
1. Configure approval thresholds for your business
2. Set up notification preferences
3. Create approval templates for common actions
4. Train team on approval process
5. Review and adjust thresholds monthly

---

*Skill Version: 1.0.0*
*Compatible with: Silver Tier AI Employee*
*Last Updated: 2026-01-07*
