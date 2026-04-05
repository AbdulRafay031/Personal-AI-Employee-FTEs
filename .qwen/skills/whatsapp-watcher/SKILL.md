# WhatsApp Watcher Skill

Monitor WhatsApp Web for incoming messages and create action files in the Obsidian vault. Uses Playwright for browser automation.

## Overview

This skill enables your AI Employee to:
- Monitor WhatsApp Web 24/7 for new messages
- Detect keyword-triggered messages (urgent, invoice, payment, help)
- Create structured action files in `/Needs_Action/` folder
- Track processed messages to avoid duplicates
- Support multiple chat monitoring

## Architecture

```
WhatsApp Web → Playwright Browser → WhatsApp Watcher → Obsidian Vault
                                            ↓
                                    Needs_Action/WHATSAPP_<contact>_<timestamp>.md
```

## Setup

### Prerequisites

1. **Playwright installed:**
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **WhatsApp Web account:** Must have WhatsApp Web enabled on your phone

3. **Session storage:** Create a folder for persistent browser session:
   ```bash
   mkdir -p /path/to/vault/.whatsapp_session
   ```

### Installation

```bash
# Install the skill (if using Qwen agent)
# Or manually copy this skill to your .qwen/skills/ directory

# Verify Playwright installation
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

## Usage

### Basic Usage

```bash
python watchers/whatsapp_watcher.py /path/to/vault --session-path /path/to/vault/.whatsapp_session
```

### Command Line Options

```bash
python watchers/whatsapp_watcher.py /path/to/vault \
  --session-path /path/to/session \
  --interval 30 \
  --keywords "urgent,invoice,payment,help,asap" \
  --headless
```

| Option | Default | Description |
|--------|---------|-------------|
| `--session-path` | Required | Path to store WhatsApp Web session |
| `--interval` | 30 | Check interval in seconds |
| `--keywords` | urgent,invoice,payment,help | Comma-separated trigger keywords |
| `--headless` | False | Run browser in headless mode |
| `--vip-contacts` | None | Comma-separated VIP contact names (always notify) |

## Action File Format

When a message is detected, creates a file like:

```markdown
---
type: whatsapp
from: John Doe
contact_id: john_doe_123
received: 2026-01-07T10:30:00Z
priority: high
status: pending
keywords: invoice, payment
---

## Message Details

| Field | Value |
|-------|-------|
| **From** | John Doe |
| **Contact ID** | john_doe_123 |
| **Received** | 2026-01-07T10:30:00Z |
| **Priority** | high |
| **Keywords Detected** | invoice, payment |

---

## Message Content

Hey, can you send me the invoice for January?

---

## Suggested Actions

- [ ] Extract invoice details
- [ ] Generate invoice PDF
- [ ] Send via email (requires approval)
- [ ] Log to Accounting

---

## Notes

```
Add processing notes here...
```
```

## Keyword Detection

### Default Keywords

| Keyword | Priority | Action |
|---------|----------|--------|
| urgent | high | Create high-priority task, notify immediately |
| asap | high | Create high-priority task |
| invoice | high | Create accounting task |
| payment | high | Create payment task |
| help | high | Create task, notify human |

### Custom Keywords

Add custom keywords via command line or environment:

```bash
# Via command line
python watchers/whatsapp_watcher.py /vault --keywords "urgent,invoice,payment,help,pricing,quote"

# Via environment variable
export WHATSAPP_KEYWORDS="urgent,invoice,payment,help,pricing,quote"
```

## VIP Contact Handling

Mark certain contacts as VIP for immediate notification:

```bash
python watchers/whatsapp_watcher.py /vault \
  --vip-contacts "Spouse,Business Partner,Primary Client"
```

VIP messages always get:
- `priority: high` in frontmatter
- Immediate notification (if notification system configured)
- Bypass keyword filtering (all messages captured)

## Session Management

### First-Time Setup

1. Run watcher in interactive mode:
   ```bash
   python watchers/whatsapp_watcher.py /vault --session-path /path/to/session --interactive
   ```

2. Scan QR code with WhatsApp mobile app

3. Session saved to `/path/to/session/`

### Session Refresh

If session expires:
```bash
# Delete old session
rm -rf /path/to/session/*

# Re-authenticate
python watchers/whatsapp_watcher.py /vault --session-path /path/to/session --interactive
```

### Session Security

- **NEVER sync session folder** to cloud (add to `.gitignore`)
- **NEVER share session files** (contains authentication tokens)
- Store session in secure location with restricted permissions

```bash
# Set restrictive permissions (Linux/Mac)
chmod 700 /path/to/session
```

## Integration with Orchestrator

The watcher creates files in `/Needs_Action/`. The orchestrator processes them:

```bash
# Orchestrator automatically detects new WhatsApp files
python orchestrator.py /path/to/vault --model qwen-2.5-coder-32b-instruct
```

### Example Flow

1. **Message arrives:** "Hey, send me the invoice"
2. **Watcher detects:** Keyword "invoice" matched
3. **Action file created:** `Needs_Action/WHATSAPP_john_doe_20260107103000.md`
4. **Orchestrator processes:** Reads file, creates plan
5. **Plan created:** `Plans/PLAN_invoice_john_doe.md`
6. **Approval requested:** `Pending_Approval/EMAIL_invoice_john_doe.md`
7. **Human approves:** Move file to `/Approved/`
8. **Email MCP sends:** Invoice sent via email
9. **Task completed:** Files moved to `/Done/`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code not appearing | Run with `--interactive` flag, ensure browser window visible |
| Session expires quickly | Check internet connection, re-authenticate |
| Messages not detected | Verify keywords match message content (case-insensitive) |
| Browser crashes | Increase `--interval`, reduce resource usage |
| Playwright errors | Run `playwright install chromium` |
| WhatsApp Web disconnects | Check phone connection, restart watcher |

## Security Considerations

### ⚠️ Important Warnings

1. **Terms of Service:** WhatsApp Web automation may violate WhatsApp ToS. Use at your own risk.

2. **Rate Limiting:** Don't send automated replies too frequently (WhatsApp may ban your number)

3. **Privacy:** Session files contain authentication tokens - never share or commit to git

4. **Backup:** Regularly backup important chats - automation doesn't replace official backups

### Recommended Safeguards

```bash
# Add to .gitignore
.whatsapp_session/
*.session
token.json
```

```bash
# Set file permissions
chmod 600 /path/to/vault/.whatsapp_session/*
```

## Advanced Configuration

### Custom Message Filtering

Create a custom filter script:

```python
# custom_filter.py
def should_process(message: dict) -> bool:
    """Custom logic to filter messages."""
    # Only process messages from business contacts
    business_contacts = ['client1', 'client2']
    return message.get('contact_id') in business_contacts
```

### Notification Integration

Integrate with notification system for urgent messages:

```python
# In whatsapp_watcher.py, add after line 150:
if priority == 'high':
    send_notification(f"Urgent WhatsApp from {from_name}: {snippet}")
```

### Multi-Account Support

Run multiple watchers with different session paths:

```bash
# Personal account
python watchers/whatsapp_watcher.py /vault --session-path /vault/.whatsapp_personal &

# Business account
python watchers/whatsapp_watcher.py /vault --session-path /vault/.whatsapp_business &
```

## Testing

### Test Message Detection

```bash
# Create a test message file
cat > /tmp/test_whatsapp.json << EOF
{
  "from": "Test User",
  "contact_id": "test_123",
  "text": "Urgent: Need invoice ASAP",
  "timestamp": "2026-01-07T10:30:00Z"
}
EOF

# Test action file creation
python -c "
from pathlib import Path
from watchers.whatsapp_watcher import WhatsAppWatcher

watcher = WhatsAppWatcher('/path/to/vault', '/tmp/session')
watcher.create_action_file({
    'from': 'Test User',
    'contact_id': 'test_123',
    'text': 'Urgent: Need invoice ASAP',
    'timestamp': '2026-01-07T10:30:00Z'
})
print('Test action file created')
"
```

## Performance Tuning

### Optimize Check Interval

| Use Case | Recommended Interval |
|----------|---------------------|
| High-volume business | 15-30 seconds |
| Personal use | 60-120 seconds |
| Low-priority monitoring | 300 seconds |

### Resource Usage

- **Memory:** ~200MB per browser instance
- **CPU:** <5% when idle, spikes during checks
- **Network:** Minimal (WhatsApp Web maintains WebSocket)

### Reduce Resource Usage

```bash
# Run headless (no GUI)
python watchers/whatsapp_watcher.py /vault --headless

# Increase interval
python watchers/whatsapp_watcher.py /vault --interval 120

# Limit processed messages cache
export WHATSAPP_MAX_CACHE=500
```

## Example Deployment

### Systemd Service (Linux)

```ini
# /etc/systemd/system/whatsapp-watcher.service
[Unit]
Description=WhatsApp Watcher for AI Employee
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/Personal-AI-Employee-FTEs
ExecStart=/usr/bin/python3 watchers/whatsapp_watcher.py /path/to/vault --session-path /path/to/session --headless
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable whatsapp-watcher
sudo systemctl start whatsapp-watcher
sudo systemctl status whatsapp-watcher
```

### Windows Task Scheduler

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "watchers/whatsapp_watcher.py C:/vault --session-path C:/vault/.whatsapp_session"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "WhatsApp Watcher" -Action $action -Trigger $trigger
```

## Metrics & Monitoring

### Log File Location

```
/vault/Logs/watcher_YYYYMMDD.log
```

### Key Metrics to Monitor

- Messages processed per hour
- Average processing time
- Session expiry events
- Error rate

### Sample Log Output

```
2026-01-07 10:30:00 - WhatsAppWatcher - INFO - Initialized WhatsAppWatcher
2026-01-07 10:30:15 - WhatsAppWatcher - INFO - Starting WhatsAppWatcher (interval: 30s)
2026-01-07 10:31:00 - WhatsAppWatcher - INFO - New message from John Doe
2026-01-07 10:31:01 - WhatsAppWatcher - INFO - Created action file: WHATSAPP_john_doe_20260107103100.md
```

## API Reference

### WhatsAppWatcher Class

```python
class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str, **kwargs)
    def check_for_updates(self) -> List[Dict]
    def create_action_file(self, message: Dict) -> Path
    def run(self)
```

### Message Dict Format

```python
{
    'from': str,           # Display name
    'contact_id': str,     # Unique contact identifier
    'text': str,           # Message content
    'timestamp': str,      # ISO format timestamp
    'is_group': bool,      # Whether from group chat
    'group_name': str,     # Group name (if applicable)
}
```

## Related Skills

- **browsing-with-playwright:** Core browser automation
- **gmail-watcher:** Email monitoring
- **filesystem-watcher:** File drop monitoring
- **email-mcp:** Send email responses

## Next Steps

After setting up WhatsApp watcher:
1. Configure keywords for your use case
2. Set up VIP contacts for priority handling
3. Integrate with orchestrator for automated processing
4. Add notification system for urgent messages
5. Consider LinkedIn poster skill for outbound messaging

---

*Skill Version: 1.0.0*
*Compatible with: Silver Tier AI Employee*
*Last Updated: 2026-01-07*
