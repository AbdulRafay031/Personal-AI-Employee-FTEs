# Silver Tier Setup Guide - AI Employee FTE

Complete guide to building a functional AI Employee assistant with advanced automation capabilities.

**Estimated Setup Time:** 20-30 hours  
**Prerequisites:** Bronze Tier completion

---

## Table of Contents

1. [Overview](#overview)
2. [Silver Tier Requirements](#silver-tier-requirements)
3. [Installation](#installation)
4. [Skill Configuration](#skill-configuration)
5. [Watcher Setup](#watcher-setup)
6. [Approval Workflow](#approval-workflow)
7. [Scheduling](#scheduling)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The Silver Tier transforms your AI Employee from a basic task processor into a **functional assistant** capable of:

- ✅ Multi-channel communication (Email, WhatsApp, LinkedIn)
- ✅ Autonomous task planning with Plan.md files
- ✅ Human-in-the-loop approval for sensitive actions
- ✅ Scheduled operations (daily briefings, weekly audits)
- ✅ Social media automation for lead generation

### What You'll Build

```
┌─────────────────────────────────────────────────────────────┐
│                    SILVER TIER AI EMPLOYEE                  │
├─────────────────────────────────────────────────────────────┤
│  INPUT CHANNELS          │  PROCESSING          │  OUTPUT   │
├──────────────────────────┼──────────────────────┼───────────┤
│  • Gmail Watcher         │  • Plan Generator    │  • Email  │
│  • WhatsApp Watcher      │  • HITL Approval     │  • LinkedIn│
│  • File System Watcher   │  • Orchestrator      │  • Files  │
│  • LinkedIn Scheduler    │  • Scheduler         │  • Logs   │
└──────────────────────────┴──────────────────────┴───────────┘
```

---

## Silver Tier Requirements

### Completed Bronze Tier

Before starting, ensure you have:

- [x] Obsidian vault with Dashboard.md
- [x] Company_Handbook.md with rules
- [x] At least one working watcher (Gmail or File System)
- [x] Orchestrator processing tasks
- [x] Basic folder structure (Inbox, Needs_Action, Done)

### New Silver Tier Components

| Component | Purpose | Time |
|-----------|---------|------|
| WhatsApp Watcher | Monitor WhatsApp Web for messages | 3-4 hours |
| LinkedIn Poster | Automated social media posting | 3-4 hours |
| Email MCP | Send emails with approval | 2-3 hours |
| Plan Generator | Auto-create task plans | 2-3 hours |
| HITL Approval | Human-in-the-loop workflow | 2-3 hours |
| Scheduler | Cron/task scheduler setup | 2-3 hours |
| Integration | Connect all components | 4-6 hours |
| Testing | End-to-end testing | 2-3 hours |

**Total:** 20-30 hours

---

## Installation

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd Personal-AI-Employee-FTEs

# Install Python dependencies
pip install -r requirements.txt

# Additional Silver Tier dependencies
pip install playwright
playwright install chromium

pip install apscheduler
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Step 2: Verify Installation

```bash
# Check Python dependencies
python -c "import playwright; print('Playwright OK')"
python -c "import apscheduler; print('APScheduler OK')"
python -c "from googleapiclient.discovery import build; print('Gmail API OK')"

# Verify skills directory
ls .qwen/skills/
# Should show:
# - browsing-with-playwright
# - whatsapp-watcher
# - linkedin-poster
# - email-mcp
# - plan-generator
# - hitl-approval
# - scheduler
```

### Step 3: Setup Environment Variables

Create `.env` file in project root:

```bash
# OpenRouter API (for AI reasoning)
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Gmail API
GMAIL_CLIENT_ID=your-gmail-client-id
GMAIL_CLIENT_SECRET=your-gmail-client-secret
GMAIL_REDIRECT_URI=http://localhost:8080/callback
GMAIL_CREDENTIALS_PATH=/absolute/path/to/credentials.json
GMAIL_TOKEN_PATH=/absolute/path/to/vault/.gmail_token.json

# WhatsApp Session
WHATSAPP_SESSION_PATH=/absolute/path/to/vault/.whatsapp_session

# LinkedIn Session
LINKEDIN_SESSION_PATH=/absolute/path/to/vault/.linkedin_session

# Email Settings
DEFAULT_FROM=your-email@gmail.com
DRY_RUN=false

# Vault Path
VAULT_PATH=/absolute/path/to/AI_Employee_Vault
```

---

## Skill Configuration

### Available Silver Tier Skills

All skills are located in `.qwen/skills/` directory:

```
.qwen/skills/
├── browsing-with-playwright/     # Browser automation (Bronze)
├── whatsapp-watcher/             # WhatsApp monitoring (NEW)
├── linkedin-poster/              # LinkedIn automation (NEW)
├── email-mcp/                    # Email sending (NEW)
├── plan-generator/               # Task planning (NEW)
├── hitl-approval/                # Approval workflow (NEW)
└── scheduler/                    # Scheduling (NEW)
```

### Skill Usage Reference

| Skill | Command | Purpose |
|-------|---------|---------|
| WhatsApp Watcher | `python watchers/whatsapp_watcher.py /vault --session-path /path/to/session` | Monitor WhatsApp |
| LinkedIn Poster | `python skills/linkedin_poster.py /vault --action draft --topic "Your topic"` | Create LinkedIn posts |
| Email MCP | `python skills/email_mcp_client.py /vault --action draft --to "email@example.com"` | Send emails |
| Plan Generator | `python skills/plan_generator.py /vault --auto-generate` | Generate plans |
| HITL Approval | `python skills/approval_workflow.py /vault --list-pending` | Manage approvals |

---

## Watcher Setup

### WhatsApp Watcher

#### 1. Create Session Directory

```bash
mkdir -p /path/to/vault/.whatsapp_session
chmod 700 /path/to/vault/.whatsapp_session
```

#### 2. First-Time Authentication

```bash
# Run in interactive mode (visible browser)
python watchers/whatsapp_watcher.py /path/to/vault \
  --session-path /path/to/vault/.whatsapp_session \
  --interactive
```

**Steps:**
1. Browser window opens
2. WhatsApp Web QR code appears
3. Scan QR code with WhatsApp mobile app
4. Session saved to `.whatsapp_session/`

#### 3. Configure Keywords

Edit default keywords or add custom ones:

```bash
# Run with custom keywords
python watchers/whatsapp_watcher.py /vault \
  --session-path /path/to/session \
  --keywords "urgent,asap,invoice,payment,help,pricing,quote"
```

#### 4. Test WhatsApp Watcher

```bash
# Send yourself a WhatsApp message with keyword "test"
# Check Needs_Action folder for new file
ls Needs_Action/ | grep WHATSAPP
```

### Gmail Watcher (Already in Bronze)

If not set up:

```bash
# Authenticate Gmail
python watchers/gmail_watcher.py /vault \
  --credentials /path/to/credentials.json \
  --auth-only

# Run watcher
python watchers/gmail_watcher.py /vault \
  --credentials /path/to/credentials.json \
  --interval 120
```

### File System Watcher

```bash
# Create drop folder
mkdir -p /path/to/drop_folder

# Run watcher
python watchers/filesystem_watcher.py /vault \
  --watch-folder /path/to/drop_folder \
  --interval 30
```

---

## Approval Workflow

### Understanding HITL

Human-in-the-Loop (HITL) ensures sensitive actions require human approval:

```
AI detects action needed
        ↓
Creates Approval Request
        ↓
Pending_Approval/
        ↓
Human reviews and moves to:
├── Approved/ → Execute → Done/
├── Rejected/ → Log reason → Done/
└── Plans/ → Needs edits → Revise
```

### Actions Requiring Approval

| Action | Threshold | Approval |
|--------|-----------|----------|
| Email to new contact | Any | ✅ Required |
| Email with attachment | Any | ✅ Required |
| Payment | > $100 | ✅ Required |
| Payment to new vendor | Any | ✅ Required |
| Social media post | Any | ✅ Required |
| File deletion | Any | ✅ Required |

### Managing Approvals

```bash
# List pending approvals
python skills/approval_workflow.py /vault --list-pending

# Execute all approved actions
python skills/approval_workflow.py /vault --execute-approved

# View statistics
python skills/approval_workflow.py /vault --stats

# Send reminders for expiring approvals
python skills/approval_workflow.py /vault --reminders
```

### Manual Approval Process

1. **Review:** Open file in `Pending_Approval/` folder
2. **Decide:**
   - Approve → Move to `Approved/`
   - Reject → Move to `Rejected/` with notes
   - Edit → Move to `Plans/` with comments
3. **Execute:** Orchestrator automatically processes `Approved/` folder

---

## Scheduling

### Option 1: Cron (Linux/Mac)

#### Edit Crontab

```bash
crontab -e
```

#### Add Scheduled Tasks

```bash
# Environment
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
PYTHONPATH=/path/to/Personal-AI-Employee-FTEs

# Process tasks every hour
0 * * * * cd /path/to/Personal-AI-Employee-FTEs && python3 orchestrator.py /vault --once >> /vault/Logs/cron.log 2>&1

# Daily briefing at 8:00 AM
0 8 * * * cd /path/to/Personal-AI-Employee-FTEs && python3 skills/plan_generator.py /vault --auto-generate >> /vault/Logs/cron_plans.log 2>&1

# Execute approved actions every 15 minutes
*/15 * * * * cd /path/to/Personal-AI-Employee-FTEs && python3 skills/approval_workflow.py /vault --execute-approved >> /vault/Logs/cron_approvals.log 2>&1

# Weekly audit on Sunday 10:00 PM
0 22 * * 0 cd /path/to/Personal-AI-Employee-FTEs && python3 skills/weekly_audit.py /vault >> /vault/Logs/cron_audit.log 2>&1
```

### Option 2: Windows Task Scheduler

#### PowerShell Script

```powershell
# Create-SilverTierTasks.ps1
$vaultPath = "C:\path\to\vault"
$projectPath = "C:\path\to\Personal-AI-Employee-FTEs"
$pythonExe = "C:\Python311\python.exe"

# Hourly processing
$action = New-ScheduledTaskAction -Execute $pythonExe `
  -Argument "orchestrator.py $vaultPath --once" `
  -WorkingDirectory $projectPath
$trigger = New-ScheduledTaskTrigger -Once (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "AI Employee - Hourly" `
  -Action $action -Trigger $trigger

# Daily briefing
$action = New-ScheduledTaskAction -Execute $pythonExe `
  -Argument "skills/plan_generator.py $vaultPath --auto-generate" `
  -WorkingDirectory $projectPath
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
Register-ScheduledTask -TaskName "AI Employee - Daily Briefing" `
  -Action $action -Trigger $trigger

# Approval execution
$action = New-ScheduledTaskAction -Execute $pythonExe `
  -Argument "skills/approval_workflow.py $vaultPath --execute-approved" `
  -WorkingDirectory $projectPath
$trigger = New-ScheduledTaskTrigger -Once (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName "AI Employee - Approvals" `
  -Action $action -Trigger $trigger
```

#### Run Script

```powershell
# Run as Administrator
.\Create-SilverTierTasks.ps1

# Verify
Get-ScheduledTask | Where-Object {$_.TaskName -like "AI Employee*"}
```

### Option 3: Python APScheduler

#### Create Scheduler Script

```python
# scheduler.py
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import sys

VAULT = "/path/to/vault"
PYTHON = sys.executable

sched = BlockingScheduler()

# Hourly processing
sched.add_job(
    lambda: subprocess.run([PYTHON, "orchestrator.py", VAULT, "--once"]),
    CronTrigger(minute=0),
    id='hourly'
)

# Daily briefing
sched.add_job(
    lambda: subprocess.run([PYTHON, "skills/plan_generator.py", VAULT, "--auto-generate"]),
    CronTrigger(hour=8),
    id='daily_briefing'
)

# Approval execution
sched.add_job(
    lambda: subprocess.run([PYTHON, "skills/approval_workflow.py", VAULT, "--execute-approved"]),
    CronTrigger(minute='*/15'),
    id='approvals'
)

print("Scheduler started. Press Ctrl+C to stop.")
sched.start()
```

#### Run Scheduler

```bash
# Install APScheduler
pip install apscheduler

# Run
python scheduler.py

# Or as daemon (Linux)
nohup python scheduler.py > scheduler.log 2>&1 &
```

---

## Testing

### End-to-End Test Scenarios

#### Test 1: WhatsApp → Plan → Approval → Email

```bash
# 1. Send WhatsApp message: "Need invoice for January"

# 2. Check action file created
ls Needs_Action/ | grep WHATSAPP

# 3. Generate plan
python skills/plan_generator.py /vault --auto-generate

# 4. Check plan created
ls Plans/ | grep Plan

# 5. Create approval request (manual or automatic)
# File should appear in Pending_Approval/

# 6. Approve (move to Approved/)
mv Pending_Approval/APPROVAL_*.md Approved/

# 7. Execute approved
python skills/approval_workflow.py /vault --execute-approved

# 8. Verify email sent (check logs)
cat Accounting/Email_Log.md
```

#### Test 2: LinkedIn Post Workflow

```bash
# 1. Create draft post
python skills/linkedin_poster.py /vault \
  --action draft \
  --topic "Q1 business achievements" \
  --post-type achievement

# 2. Review draft in Plans/
cat Plans/Plan_linkedin_*.md

# 3. Move to Pending_Approval/ for approval
mv Plans/Plan_linkedin_*.md Pending_Approval/

# 4. Approve (move to Approved/)
mv Pending_Approval/Plan_linkedin_*.md Approved/

# 5. Post (dry run first)
export LINKEDIN_DRY_RUN=true
python skills/linkedin_poster.py /vault --action post --file "Approved/Plan_linkedin_*.md"
```

#### Test 3: Daily Briefing Automation

```bash
# 1. Run plan generator manually
python skills/plan_generator.py /vault --auto-generate

# 2. Check Dashboard.md updated
cat Dashboard.md

# 3. Verify plans created
ls Plans/ | wc -l

# 4. Check logs
cat Logs/orchestrator_*.log
```

### Verification Checklist

```bash
# WhatsApp watcher running
pgrep -f whatsapp_watcher

# Gmail watcher running
pgrep -f gmail_watcher

# Orchestrator running
pgrep -f orchestrator

# Check recent action files
ls -lt Needs_Action/ | head -5

# Check recent plans
ls -lt Plans/ | head -5

# Check pending approvals
ls Pending_Approval/

# Check executed approvals
ls Done/ | tail -5

# View logs
tail -100 Logs/orchestrator_*.log
```

---

## Troubleshooting

### Common Issues

#### WhatsApp Watcher Not Detecting Messages

**Symptoms:** No WHATSAPP files in Needs_Action

**Solutions:**
1. Check session validity:
   ```bash
   rm -rf /path/to/.whatsapp_session/*
   python watchers/whatsapp_watcher.py /vault --session-path /path/to/session --interactive
   ```

2. Verify keywords match:
   ```bash
   # Add more keywords
   python watchers/whatsapp_watcher.py /vault --keywords "urgent,asap,invoice,payment,help,test"
   ```

3. Check browser logs:
   ```bash
   cat Logs/watcher_*.log | grep -i whatsapp
   ```

#### LinkedIn Post Fails

**Symptoms:** Post not publishing, error in logs

**Solutions:**
1. Re-authenticate LinkedIn:
   ```bash
   rm -rf /path/to/.linkedin_session/*
   python skills/linkedin_poster.py /vault --action login --interactive
   ```

2. Check LinkedIn UI changes (selectors may need update)

3. Test in dry-run mode:
   ```bash
   export LINKEDIN_DRY_RUN=true
   python skills/linkedin_poster.py /vault --action post --file "Approved/TEST.md"
   ```

#### Approval Not Executing

**Symptoms:** Files stay in Approved/ folder

**Solutions:**
1. Manually execute:
   ```bash
   python skills/approval_workflow.py /vault --execute-approved
   ```

2. Check orchestrator running:
   ```bash
   ps aux | grep orchestrator
   ```

3. Verify file format:
   ```bash
   # Should have type: approval_request in frontmatter
   head -20 Approved/APPROVAL_*.md
   ```

#### Scheduler Not Running

**Symptoms:** Scheduled tasks not executing

**Solutions:**

**Cron:**
```bash
# Check cron daemon
sudo systemctl status cron

# View cron logs
grep CRON /var/log/syslog

# Verify crontab
crontab -l
```

**Windows Task Scheduler:**
```powershell
# Check task status
Get-ScheduledTask -TaskName "AI Employee*"

# View task history
Get-ScheduledTaskInfo -TaskName "AI Employee - Hourly"

# Run manually
Start-ScheduledTask -TaskName "AI Employee - Hourly"
```

**APScheduler:**
```bash
# Check if process running
ps aux | grep scheduler

# Restart
pkill -f scheduler
nohup python scheduler.py > scheduler.log 2>&1 &
```

### Debug Mode

Enable verbose logging:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Run with verbose flag
python orchestrator.py /vault --verbose

# Check detailed logs
tail -f Logs/orchestrator_*.log
```

---

## Silver Tier Completion Checklist

### Core Components

- [ ] WhatsApp Watcher installed and authenticated
- [ ] LinkedIn Poster configured and tested
- [ ] Email MCP set up with Gmail API
- [ ] Plan Generator creating plans automatically
- [ ] HITL Approval workflow functional
- [ ] Scheduler running (cron/Task Scheduler/APScheduler)

### Integration Tests

- [ ] WhatsApp message → Plan created → Approval requested → Email sent
- [ ] LinkedIn post drafted → Approved → Published
- [ ] Daily briefing generated at scheduled time
- [ ] Approved actions executed automatically
- [ ] Logs updated for all actions

### Documentation

- [ ] Business_Goals.md updated with LinkedIn strategy
- [ ] Company_Handbook.md includes approval thresholds
- [ ] Contacts/Approved_Recipients.md populated
- [ ] Schedule configuration documented
- [ ] Testing procedures documented

### Monitoring

- [ ] Dashboard.md updating automatically
- [ ] Logs being written to Logs/ folder
- [ ] Approval audit log maintained
- [ ] Email log tracking sent messages
- [ ] Social media analytics tracked

---

## Next Steps: Gold Tier

After completing Silver Tier, consider Gold Tier additions:

1. **Odoo Accounting Integration** - Self-hosted ERP
2. **Multi-Platform Social** - Facebook, Twitter, Instagram
3. **Weekly CEO Briefing** - Automated business audits
4. **Ralph Wiggum Loop** - Autonomous multi-step completion
5. **Cloud Deployment** - 24/7 always-on operation

---

## Resources

### Documentation

- [Main Blueprint](Personal%20AI%20Employee%20Hackathon%200_%20Building_Antonomous%20FTEs%20in%202026.md)
- [Bronze Tier Guide](README.md)
- [Skill Documentation](.qwen/skills/*/SKILL.md)

### Support

- Wednesday Research Meeting: 10:00 PM PKT
- Zoom: https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- YouTube: https://www.youtube.com/@panaversity

### Code Repositories

- Orchestrator: `orchestrator.py`
- Watchers: `watchers/` directory
- Skills: `skills/` and `.qwen/skills/` directories

---

*Silver Tier Setup Guide v1.0*  
*Last Updated: 2026-01-07*  
*Compatible with: Personal AI Employee FTEs Hackathon*
