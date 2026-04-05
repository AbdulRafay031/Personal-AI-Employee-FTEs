# Email MCP Integration Skill

Send, draft, and manage emails via Model Context Protocol (MCP) server with human-in-the-loop approval.

## Overview

This skill enables your AI Employee to:
- Send emails via Gmail API or SMTP
- Create draft emails for human review
- Manage email templates
- Track sent emails in vault
- Implement human-in-the-loop approval for sensitive emails

## Architecture

```
AI Employee → Email MCP Server → Gmail API/SMTP → Recipient
     ↓
Vault (Logs & Approval Files)
```

## ⚠️ Important Notes

1. **Credential Security:** Never store email credentials in vault files
2. **Approval Required:** Always require approval for emails to new contacts
3. **Rate Limiting:** Gmail API has rate limits (100 emails/minute for G Suite)
4. **Spam Prevention:** Don't send bulk emails without proper warming

## Setup

### Prerequisites

1. **Gmail API Setup:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download `credentials.json`

2. **Node.js installed:** (for MCP server)
   ```bash
   node --version  # Should be v18+
   ```

3. **Python installed:** (for email actions)
   ```bash
   python --version  # Should be 3.10+
   ```

### Installation Options

#### Option A: Gmail API (Recommended)

```bash
# Install Gmail MCP server
npm install -g @anthropic/mcp-server-gmail

# Or use open-source alternative
git clone https://github.com/your-org/email-mcp.git
cd email-mcp
npm install
```

#### Option B: SMTP (Self-hosted)

```bash
# Install Python dependencies
pip install python-dotenv
pip install sendmail  # or use smtplib (built-in)
```

## Configuration

### Gmail API Configuration

Create `.env` file in project root:

```bash
# Email Configuration
GMAIL_CLIENT_ID=your-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_REDIRECT_URI=http://localhost:8080/callback
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_TOKEN_PATH=/path/to/vault/.gmail_token.json

# Email Settings
DEFAULT_FROM=your-email@gmail.com
DRY_RUN=false
MAX_RECIPIENTS=10
```

### MCP Server Configuration

Add to `~/.config/claude-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/email-mcp/index.js"],
      "env": {
        "GMAIL_CLIENT_ID": "your-client-id",
        "GMAIL_CLIENT_SECRET": "your-client-secret",
        "GMAIL_REDIRECT_URI": "http://localhost:8080/callback"
      }
    }
  ]
}
```

## Usage

### Basic Usage

```bash
# Send email (with approval)
python email_mcp_client.py /path/to/vault --action send \
  --to "recipient@example.com" \
  --subject "Invoice #123" \
  --body "Please find attached..."

# Create draft
python email_mcp_client.py /path/to/vault --action draft \
  --to "client@example.com" \
  --subject "Project Update"

# Check inbox
python email_mcp_client.py /path/to/vault --action check-inbox
```

### Command Line Options

```bash
python email_mcp_client.py /vault \
  --action send|draft|check-inbox|send-approved \
  --to "recipient@example.com" \
  --cc "cc@example.com" \
  --bcc "bcc@example.com" \
  --subject "Email subject" \
  --body "Email body text" \
  --attachment "/path/to/file.pdf" \
  --priority high|normal|low \
  --template "invoice|followup|meeting"
```

| Option | Default | Description |
|--------|---------|-------------|
| `--action` | draft | Action: send, draft, check-inbox, send-approved |
| `--to` | None | Recipient email (required for send/draft) |
| `--cc` | None | CC recipients (comma-separated) |
| `--bcc` | None | BCC recipients (comma-separated) |
| `--subject` | None | Email subject |
| `--body` | None | Email body (markdown supported) |
| `--attachment` | None | Path to attachment |
| `--priority` | normal | Email priority: high, normal, low |
| `--template` | None | Use predefined template |

## Email Templates

### Invoice Template

```markdown
Subject: Invoice #{{invoice_number}} - {{company_name}}

Dear {{client_name}},

Please find attached invoice #{{invoice_number}} for {{amount}}.

**Invoice Details:**
- Invoice Number: {{invoice_number}}
- Amount: ${{amount}}
- Due Date: {{due_date}}
- Services: {{services}}

Payment can be made via:
- Bank Transfer: {{bank_details}}
- Credit Card: {{payment_link}}

If you have any questions, please don't hesitate to reach out.

Best regards,
{{your_name}}
{{your_company}}
```

### Follow-up Template

```markdown
Subject: Following up on {{topic}}

Hi {{contact_name}},

Hope you're doing well!

I wanted to follow up on our previous conversation about {{topic}}.

{{custom_message}}

Would you have time for a quick call this week to discuss further?

Looking forward to hearing from you.

Best regards,
{{your_name}}
```

### Meeting Request Template

```markdown
Subject: Meeting Request: {{meeting_topic}}

Dear {{recipient_name}},

I hope this email finds you well.

I'd like to schedule a meeting to discuss {{meeting_topic}}.

**Proposed Times:**
- {{time_option_1}}
- {{time_option_2}}
- {{time_option_3}}

**Meeting Details:**
- Duration: {{duration}}
- Location: {{location/Zoom link}}
- Attendees: {{attendees}}

Please let me know which time works best for you.

Best regards,
{{your_name}}
```

## Approval Workflow

### Step 1: AI Creates Email Draft

```markdown
---
type: email_draft
to: client@example.com
subject: Invoice #123 - $1,500
created: 2026-01-07T10:00:00Z
status: pending_review
requires_approval: true
---

## Email Draft

**To:** client@example.com
**Subject:** Invoice #123 - $1,500
**Priority:** normal

---

**Body:**

Dear Client,

Please find attached invoice #123 for $1,500 for services rendered in January 2026.

Invoice Details:
- Services: Consulting services
- Amount: $1,500
- Due Date: January 31, 2026

Payment can be made via bank transfer or credit card.

Best regards,
Your Company

---

## Attachments

- /Vault/Invoices/2026-01_Invoice_123.pdf

---

## Suggested Actions

- [ ] Review email content
- [ ] Verify attachment is correct
- [ ] Approve for sending (move to Pending_Approval/)
- [ ] Edit if needed

---

## Notes

```
Add review notes here...
```
```

### Step 2: Human Review

1. Review draft in `Plans/` or `Inbox/`
2. Edit content if needed
3. Move to `Pending_Approval/` for sending approval

### Step 3: Create Approval Request

```markdown
---
type: approval_request
action: email_send
to: client@example.com
subject: Invoice #123 - $1,500
created: 2026-01-07T10:30:00Z
status: pending
risk_level: low
---

## Email Send Approval

**To:** client@example.com
**Subject:** Invoice #123 - $1,500
**Attachments:** 1 file (invoice.pdf)

**Risk Assessment:**
- ✅ Known contact (paid before)
- ✅ Amount < $100
- ✅ Standard invoice email

---

## Content Preview

[Email body content here]

---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder with comments.

## To Edit
Move back to Plans/ with edit notes.
```

### Step 4: Execute Send

```bash
# Orchestrator detects approved file
python email_mcp_client.py /vault --action send-approved
```

## Contact Management

### Approved Senders List

Maintain `Contacts/Approved_Recipients.md`:

```markdown
# Approved Email Recipients

These contacts can receive emails without additional approval:

## High Trust (Auto-approve up to $500)
- client@example.com (Client A - paid 10+ times)
- partner@company.com (Business Partner)

## Medium Trust (Require approval)
- new@client.com (New contact - first email)
- vendor@supplier.com (Vendor - occasional contact)

## Do Not Email
- spam@example.com
- competitor@rival.com
```

### Contact Trust Levels

| Trust Level | Auto-approve Limit | Approval Required |
|-------------|-------------------|-------------------|
| High | $500 or routine emails | Only for > $500 |
| Medium | None | All emails |
| Low | None | All emails + human review |
| Blocked | N/A | Never email |

## Integration with Orchestrator

### Automated Email Flow

```
1. Gmail Watcher detects incoming email
        ↓
2. Creates action file in Needs_Action/
        ↓
3. AI processes and drafts response
        ↓
4. Creates approval request (if needed)
        ↓
5. Human approves (moves to Approved/)
        ↓
6. Email MCP sends email
        ↓
7. Logs to Accounting/Email_Log.md
```

### Example: Invoice Request Response

```python
# In orchestrator or custom script
def handle_invoice_request(email_data):
    """Handle invoice request from client."""
    
    # 1. Generate invoice PDF
    invoice_path = generate_invoice(
        client=email_data['from'],
        amount=1500,
        services="Consulting"
    )
    
    # 2. Create email draft
    draft_content = f"""
    Dear {email_data['from_name']},
    
    Please find attached the invoice for {email_data['subject']}.
    
    Amount: $1,500
    Due Date: January 31, 2026
    
    Best regards,
    Your Company
    """
    
    # 3. Create approval request
    approval = create_approval_request(
        to=email_data['from'],
        subject="Invoice #123",
        body=draft_content,
        attachment=invoice_path
    )
    
    return approval
```

## Email Logging

### Sent Email Log

Create `Accounting/Email_Log.md`:

```markdown
# Email Log - January 2026

## Sent Emails

| Date | To | Subject | Status | Approved By |
|------|-----|---------|--------|-------------|
| Jan 7 | client@example.com | Invoice #123 | Sent | Human |
| Jan 7 | partner@company.com | Project Update | Sent | Auto |

## Email Metrics

- **Total Sent:** 15
- **Auto-approved:** 8
- **Human-approved:** 7
- **Bounced:** 0
- **Replied:** 5
```

### Log Entry Format

```python
def log_email(email_data):
    """Log sent email to vault."""
    log_file = vault_path / 'Accounting' / 'Email_Log.md'
    
    entry = f"""
## {email_data['timestamp']}

- **To:** {email_data['to']}
- **Subject:** {email_data['subject']}
- **Status:** {email_data['status']}
- **Approval:** {email_data['approval_type']}
- **Approved By:** {email_data['approved_by']}
- **Attachments:** {', '.join(email_data.get('attachments', []))}
"""
    
    append_to_log(log_file, entry)
```

## MCP Tools Reference

### Available Email MCP Tools

```python
# Tool: email_send
{
    "name": "email_send",
    "description": "Send an email via Gmail API",
    "inputSchema": {
        "type": "object",
        "properties": {
            "to": {"type": "string"},
            "cc": {"type": "string"},
            "bcc": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"},
            "attachments": {"type": "array"}
        },
        "required": ["to", "subject", "body"]
    }
}

# Tool: email_create_draft
{
    "name": "email_create_draft",
    "description": "Create a draft email",
    "inputSchema": {
        "type": "object",
        "properties": {
            "to": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"}
        }
    }
}

# Tool: email_search
{
    "name": "email_search",
    "description": "Search emails",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "maxResults": {"type": "integer"}
        }
    }
}
```

## Testing

### Test Email Send (Dry Run)

```bash
# Enable dry run mode
export DRY_RUN=true

# Test send
python email_mcp_client.py /vault --action send \
  --to "test@example.com" \
  --subject "Test Email" \
  --body "This is a test"

# Should log: [DRY RUN] Would have sent email to test@example.com
```

### Test with Known Contact

```bash
# Create test contact file
cat > Contacts/Approved_Recipients.md << EOF
# Approved Recipients
- test@example.com (Test Contact)
EOF

# Test email to approved contact
python email_mcp_client.py /vault --action send \
  --to "test@example.com" \
  --subject "Test" \
  --body "Test body"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-run OAuth flow, check credentials.json |
| Rate limit exceeded | Wait 1 minute, reduce send frequency |
| Attachment too large | Gmail limit is 25MB, use Google Drive link |
| Email not sending | Check DRY_RUN env var, verify Gmail API enabled |
| MCP server not found | Verify installation and path in mcp.json |
| Token expired | Delete token file, re-authenticate |

## Security Considerations

### ⚠️ Critical Security Rules

1. **Never commit credentials:**
   ```bash
   # Add to .gitignore
   .env
   credentials.json
   token.json
   .gmail_token.json
   ```

2. **Use environment variables:**
   ```bash
   export GMAIL_CLIENT_ID="your-id"
   export GMAIL_CLIENT_SECRET="your-secret"
   ```

3. **Restrict API scopes:**
   ```python
   SCOPES = ['https://www.googleapis.com/auth/gmail.send']
   # Don't request full mailbox access
   ```

4. **Implement approval workflow:**
   - Always require approval for new contacts
   - Require approval for emails with attachments
   - Require approval for bulk sends (>10 recipients)

### Recommended Safeguards

```bash
# Set file permissions
chmod 600 .env
chmod 600 credentials.json
chmod 600 /path/to/vault/.gmail_token.json
```

## Advanced Configuration

### Custom Email Rules

Create `Rules/Email_Rules.md`:

```markdown
# Email Sending Rules

## Auto-approve Conditions
- [x] Reply to known contact (in Approved_Recipients)
- [x] Email thread continuation (same subject)
- [x] Meeting confirmations
- [x] Invoice sends to existing clients

## Require Approval Conditions
- [ ] New contact (first email)
- [ ] Attachments included
- [ ] Bulk send (>5 recipients)
- [ ] Payment requests
- [ ] Contract-related emails

## Never Auto-send
- [ ] Emails to competitors
- [ ] Legal/attorney communications
- [ ] Media/press inquiries
- [ ] Complaints/negative feedback
```

### Email Scheduling

```python
# Schedule email for optimal send time
def schedule_email(email_data, send_time):
    """Schedule email for specific time."""
    
    # Store in Scheduled folder
    scheduled_file = vault_path / 'Scheduled' / f"EMAIL_{send_time.isoformat()}.md"
    
    content = f"""---
type: scheduled_email
send_time: {send_time.isoformat()}
status: scheduled
---

{email_data}
"""
    
    scheduled_file.write_text(content)
    
    # Cron job will process at send_time
```

## Performance Tuning

### Batch Sending

```python
# Send multiple emails efficiently
def batch_send_emails(emails: List[Dict], batch_size: int = 10):
    """Send emails in batches to avoid rate limits."""
    
    for i in range(0, len(emails), batch_size):
        batch = emails[i:i + batch_size]
        
        for email in batch:
            send_email(email)
            time.sleep(1)  # 1 second between emails
        
        if i + batch_size < len(emails):
            time.sleep(60)  # 1 minute between batches
```

### Rate Limits

| Email Type | Limit |
|------------|-------|
| Gmail (free) | 500 emails/day |
| Gmail (G Suite) | 2,000 emails/day |
| Gmail API | 100 emails/minute |
| SMTP | Varies by provider |

## Example Deployment

### Systemd Service for Email Processing

```ini
# /etc/systemd/system/email-processor.service
[Unit]
Description=Email Processor for AI Employee
After=network.target

[Service]
Type=oneshot
User=youruser
WorkingDirectory=/path/to/Personal-AI-Employee-FTEs
ExecStart=/usr/bin/python3 email_mcp_client.py /path/to/vault --action send-approved
Environment="DRY_RUN=false"
```

```bash
# Run every 15 minutes
*/15 * * * * /usr/bin/systemctl start email-processor.service
```

## Metrics & Monitoring

### Log File Location

```
/vault/Logs/email_mcp_YYYYMMDD.log
```

### Key Metrics to Monitor

- Emails sent per day
- Approval rate (approved vs rejected)
- Bounce rate
- Response rate
- Average send time

### Sample Log Output

```
2026-01-07 10:00:00 - EmailMCP - INFO - Initialized Email MCP
2026-01-07 10:00:05 - EmailMCP - INFO - Authentication successful
2026-01-07 10:00:10 - EmailMCP - INFO - Sending email to client@example.com
2026-01-07 10:00:15 - EmailMCP - INFO - Email sent successfully (Message ID: abc123)
2026-01-07 10:00:16 - EmailMCP - INFO - Email logged to Accounting/Email_Log.md
```

## Related Skills

- **gmail-watcher:** Incoming email monitoring
- **whatsapp-watcher:** Cross-platform messaging
- **linkedin-poster:** Social media integration
- **browsing-with-playwright:** Web automation

## Next Steps

After setting up Email MCP:
1. Configure Gmail API credentials
2. Set up approved contacts list
3. Create email templates for common scenarios
4. Test approval workflow with test emails
5. Integrate with orchestrator for automated responses
6. Consider adding email analytics tracking

---

*Skill Version: 1.0.0*
*Compatible with: Silver Tier AI Employee*
*Last Updated: 2026-01-07*
