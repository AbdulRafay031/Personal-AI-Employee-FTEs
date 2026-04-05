# Plan.md Generator Skill (Claude Reasoning Loop)

Automatically generate structured Plan.md files for complex multi-step tasks. Enables Claude Code to break down tasks into actionable steps with checkboxes.

## Overview

This skill enables your AI Employee to:
- Analyze incoming tasks from `/Needs_Action/` folder
- Generate structured Plan.md files with clear objectives and steps
- Track progress via checkboxes
- Request approval for sensitive actions
- Move tasks to `/Done/` upon completion

## Architecture

```
Needs_Action/ → Plan Generator → Plans/Plan_<task>_<date>.md
                                       ↓
                                  Checkboxes for each step
                                       ↓
                                  Approval requests (if needed)
                                       ↓
                                  Done/ (when complete)
```

## What is a Plan.md File?

A Plan.md is a structured markdown file that breaks down a complex task into manageable steps:

```markdown
---
type: plan
task: Send invoice to Client A
created: 2026-01-07T10:00:00Z
status: in_progress
priority: high
estimated_steps: 5
completed_steps: 2
---

# Plan: Send invoice to Client A

## Objective
Generate and send January 2026 invoice to Client A for consulting services.

## Context
- Client requested invoice via WhatsApp on 2026-01-07
- Agreed amount: $1,500
- Services: Consulting for January 2026
- Payment terms: Net 30

## Steps

- [x] Identify client details (email, billing info)
- [x] Calculate invoice amount
- [ ] Generate invoice PDF
- [ ] Create email draft with invoice attachment
- [ ] Request approval (HITL required for new invoice)
- [ ] Send email after approval
- [ ] Log transaction to Accounting/
- [ ] Move task to Done/

## Approval Required

| Step | Action | Reason |
|------|--------|--------|
| 5 | Send email with invoice | New invoice, requires human verification |

## Notes

```
2026-01-07 10:00: Created plan
2026-01-07 10:05: Completed steps 1-2
```

## Related Files

- Source: `Needs_Action/WHATSAPP_client_a_20260107.md`
- Draft: `Plans/EMAIL_DRAFT_client_a_invoice.md`
- Approval: `Pending_Approval/EMAIL_APPROVAL_client_a.md`
```

## Usage

### Basic Usage

```bash
# Generate plan for all tasks in Needs_Action
python plan_generator.py /path/to/vault

# Generate plan for specific task
python plan_generator.py /path/to/vault --task-file "Needs_Action/WHATSAPP_client_a.md"

# Update existing plan progress
python plan_generator.py /path/to/vault --update-plan "Plans/Plan_invoice_client_a.md"
```

### Command Line Options

```bash
python plan_generator.py /vault \
  --task-file "path/to/task.md" \
  --update-plan "path/to/plan.md" \
  --auto-generate \
  --include-approval-steps \
  --dry-run
```

| Option | Default | Description |
|--------|---------|-------------|
| `--task-file` | None | Specific task file to process |
| `--update-plan` | None | Update existing plan progress |
| `--auto-generate` | False | Auto-generate plans for all Needs_Action tasks |
| `--include-approval-steps` | True | Include approval request steps |
| `--dry-run` | False | Generate plan without saving |

## Plan Templates

### Invoice Processing Plan

```markdown
---
type: plan
category: finance
task: Process invoice request
created: {{timestamp}}
status: pending
priority: high
---

# Plan: {{task_title}}

## Objective
{{objective_description}}

## Context
- Client: {{client_name}}
- Amount: {{amount}}
- Service: {{service_type}}
- Requested via: {{communication_channel}}

## Steps

- [ ] Identify client details (email, billing info)
- [ ] Verify service completion/delivery
- [ ] Calculate invoice amount
- [ ] Generate invoice PDF
- [ ] Create email draft with invoice attachment
- [ ] Request approval (HITL required)
- [ ] Send email after approval
- [ ] Log transaction to Accounting/
- [ ] Move task to Done/

## Approval Required

| Step | Action | Reason |
|------|--------|--------|
| 6 | Send invoice email | Financial transaction requires human verification |

## Notes

```
{{initial_notes}}
```
```

### Email Response Plan

```markdown
---
type: plan
category: communication
task: Respond to email
created: {{timestamp}}
status: pending
---

# Plan: Respond to {{sender}}

## Objective
Draft and send response to email from {{sender}} regarding {{subject}}.

## Context
- Sender: {{sender_name}} ({{sender_type}})
- Subject: {{email_subject}}
- Received: {{received_date}}
- Priority: {{priority_level}}

## Steps

- [ ] Read and understand email content
- [ ] Determine response needed
- [ ] Draft response
- [ ] {{approval_step}}
- [ ] Send response
- [ ] Archive original email
- [ ] Move task to Done/

## Approval Required

{{approval_table}}

## Notes

```
{{notes}}
```
```

### Social Media Post Plan

```markdown
---
type: plan
category: marketing
task: Create and post social media content
created: {{timestamp}}
status: pending
---

# Plan: {{platform}} Post - {{topic}}

## Objective
Create and publish {{post_type}} post about {{topic}} to generate engagement.

## Context
- Platform: {{platform}}
- Post Type: {{post_type}}
- Topic: {{topic}}
- Scheduled Time: {{scheduled_time}}
- Goal: {{engagement_goal}}

## Steps

- [ ] Research topic and gather key points
- [ ] Draft post content
- [ ] Add relevant hashtags
- [ ] Review brand voice alignment
- [ ] Create approval request
- [ ] Schedule/post after approval
- [ ] Monitor engagement
- [ ] Respond to comments (if needed)
- [ ] Log to analytics
- [ ] Move task to Done/

## Approval Required

| Step | Action | Reason |
|------|--------|--------|
| 5 | Publish post | All social media posts require human approval |

## Content Guidelines

- Tone: {{brand_tone}}
- Hashtags: 3-5 relevant
- Emojis: Moderate (2-4)
- Call-to-action: Include

## Notes

```
{{notes}}
```
```

## Integration with Orchestrator

### Automatic Plan Generation

Add to `orchestrator.py`:

```python
def process_needs_action(self):
    """Process all files in Needs_Action folder."""
    tasks = self._get_task_files('Needs_Action')

    if not tasks:
        return

    for task in tasks:
        # Generate plan for each task
        plan_file = self._generate_plan(task.path)

        if plan_file:
            self.logger.info(f'Generated plan: {plan_file.name}')

    self._update_dashboard()
```

### Plan Progress Tracking

```python
def update_plan_progress(self, plan_file: Path):
    """Update plan progress based on completed steps."""
    content = plan_file.read_text(encoding='utf-8')

    # Count checkboxes
    import re
    all_checkboxes = re.findall(r'- \[.\]', content)
    completed_checkboxes = re.findall(r'- \[x\]', content)

    total = len(all_checkboxes)
    completed = len(completed_checkboxes)

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
    if completed == total and total > 0:
        content = re.sub(
            r'status: \w+',
            'status: completed',
            content
        )
        # Add completion timestamp
        content += f'\n\n**Completed:** {datetime.now().isoformat()}\n'

    plan_file.write_text(content, encoding='utf-8')
```

## Task Type Detection

### Automatic Categorization

```python
def detect_task_type(task_file: Path) -> str:
    """Detect task type from file content."""
    content = task_file.read_text(encoding='utf-8')

    # Parse frontmatter
    import re
    match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return 'general'

    frontmatter = match.group(1)

    # Detect type
    if 'type: email' in frontmatter:
        return 'email_response'
    elif 'type: whatsapp' in frontmatter:
        if 'invoice' in content.lower() or 'payment' in content.lower():
            return 'invoice_request'
        else:
            return 'whatsapp_response'
    elif 'type: file_drop' in frontmatter:
        if 'invoice' in content.lower():
            return 'invoice_processing'
        else:
            return 'file_processing'
    elif 'linkedin' in content.lower():
        return 'social_media_post'

    return 'general'
```

## Approval Step Detection

### Automatic Approval Requirements

```python
def requires_approval(task_type: str, content: str) -> bool:
    """Determine if task requires human approval."""
    # Financial tasks
    if task_type in ['invoice_request', 'invoice_processing', 'payment']:
        return True

    # New contact emails
    if 'sender_email' in content:
        # Check if new contact
        if not is_known_contact(content):
            return True

    # Social media posts
    if task_type == 'social_media_post':
        return True

    # Large payments
    if '$' in content:
        import re
        amounts = re.findall(r'\$[\d,]+', content)
        for amount in amounts:
            value = float(amount.replace('$', '').replace(',', ''))
            if value > 100:  # > $100 requires approval
                return True

    return False
```

## Example Plans

### Example 1: Invoice Request from WhatsApp

```markdown
---
type: plan
category: finance
task: Send invoice to John Doe
created: 2026-01-07T10:30:00Z
status: in_progress
priority: high
estimated_steps: 8
completed_steps: 3
source_file: Needs_Action/WHATSAPP_john_doe_20260107103000.md
---

# Plan: Send Invoice to John Doe

## Objective
Generate and send January 2026 invoice to John Doe for consulting services.

## Context
- **Client:** John Doe (john.doe@example.com)
- **Amount:** $1,500
- **Service:** Consulting for January 2026
- **Requested via:** WhatsApp message on 2026-01-07
- **Payment Terms:** Net 30

## Steps

- [x] Read WhatsApp message and extract request
- [x] Identify client details (email: john.doe@example.com)
- [x] Verify client exists in approved contacts
- [ ] Generate invoice PDF (#123, $1,500, Jan 2026)
- [ ] Create email draft with invoice attachment
- [ ] Request approval (HITL required for new invoice)
- [ ] Send email after approval
- [ ] Log transaction to Accounting/Current_Month.md
- [ ] Move task to Done/

## Approval Required

| Step | Action | Reason |
|------|--------|--------|
| 6 | Send invoice email | Financial transaction, new invoice |

## Notes

```
2026-01-07 10:30: Plan created
2026-01-07 10:32: Steps 1-3 completed - client verified
```

## Related Files

- **Source:** `Needs_Action/WHATSAPP_john_doe_20260107103000.md`
- **Invoice:** `Invoices/2026-01_Invoice_123_John_Doe.pdf` (to be created)
- **Draft:** `Plans/EMAIL_DRAFT_john_doe_invoice.md` (to be created)
- **Approval:** `Pending_Approval/EMAIL_APPROVAL_john_doe.md` (to be created)
```

### Example 2: Email Response

```markdown
---
type: plan
category: communication
task: Respond to client inquiry
created: 2026-01-07T11:00:00Z
status: pending
priority: medium
estimated_steps: 6
completed_steps: 0
---

# Plan: Respond to Sarah Smith - Project Inquiry

## Objective
Draft and send professional response to Sarah Smith's inquiry about our services.

## Context
- **Sender:** Sarah Smith (sarah@newclient.com)
- **Subject:** Inquiry about consulting services
- **Received:** 2026-01-07 10:45 AM
- **Priority:** Medium (new potential client)
- **Contact Type:** New (not in approved contacts)

## Steps

- [ ] Read and understand email content
- [ ] Research sender/company
- [ ] Draft professional response
- [ ] Include service overview and pricing
- [ ] Request approval (new contact)
- [ ] Send email after approval
- [ ] Add sender to CRM/contacts
- [ ] Move task to Done/

## Approval Required

| Step | Action | Reason |
|------|--------|--------|
| 5 | Send response | New contact requires human review |

## Draft Points

- Thank for interest
- Attach service overview PDF
- Include pricing range
- Suggest call for detailed discussion
- Professional sign-off

## Notes

```

```

## Related Files

- **Source:** `Needs_Action/EMAIL_sarah_newclient_com_abc123.md`
```

## Best Practices

### Plan Quality Checklist

- [ ] Clear, specific objective
- [ ] All necessary context included
- [ ] Steps are actionable and sequential
- [ ] Approval requirements identified
- [ ] Related files linked
- [ ] Notes section for progress tracking

### When to Create Plans

**Create Plan.md for:**
- Multi-step tasks (3+ steps)
- Tasks requiring approval
- Complex financial transactions
- Social media content creation
- Client communications

**Skip Plan.md for:**
- Simple file moves
- Auto-approved routine tasks
- Single-action items

### Plan Maintenance

- Update progress daily
- Mark steps complete as you go
- Add notes for significant events
- Archive completed plans after 30 days

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Plan not generating | Check task file has valid frontmatter |
| Wrong template used | Verify task type detection logic |
| Approval not requested | Check requires_approval() thresholds |
| Progress not updating | Ensure checkbox format is `- [ ]` |
| Plan not completing | Verify all checkboxes are marked `- [x]` |

## Advanced Features

### Plan Dependencies

```markdown
## Step Dependencies

- Step 4 requires Step 3 completion
- Step 6 requires human approval
- Step 7 requires Step 6 success
```

### Time Estimates

```markdown
## Time Estimates

| Step | Estimated Time | Actual Time |
|------|---------------|-------------|
| 1-3 | 5 minutes | 4 minutes |
| 4-5 | 10 minutes | - |
| 6-7 | 5 minutes | - |
| **Total** | **20 minutes** | **4 minutes** |
```

### Risk Assessment

```markdown
## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Client email bounce | Low | Medium | Verify email before send |
| Invoice amount error | Low | High | Human approval required |
| Attachment missing | Medium | Low | Checklist before send |
```

## Related Skills

- **whatsapp-watcher:** Incoming message detection
- **email-mcp:** Email sending with approval
- **linkedin-poster:** Social media automation
- **HITL-workflow:** Approval management

## Next Steps

After setting up Plan Generator:
1. Configure plan templates for your use cases
2. Set up automatic plan generation in orchestrator
3. Integrate with approval workflow
4. Add progress tracking to Dashboard.md
5. Archive old plans monthly

---

*Skill Version: 1.0.0*
*Compatible with: Silver Tier AI Employee*
*Last Updated: 2026-01-07*
