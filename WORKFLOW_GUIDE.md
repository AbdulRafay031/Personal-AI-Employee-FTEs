# Complete Workflow Guide - Free Services Setup

**For:** Rafay (rafay16031@gmail.com)  
**Goal:** 100% Free AI Employee for Email, WhatsApp, and LinkedIn automation

---

## 📋 Table of Contents

1. [Complete Workflow Explanation](#complete-workflow-explanation)
2. [Free Services Setup](#free-services-setup)
3. [Step-by-Step Configuration](#step-by-step-configuration)
4. [Daily Usage Guide](#daily-usage-guide)
5. [Example Scenarios](#example-scenarios)

---

## Complete Workflow Explanation

### How The AI Employee Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR AI EMPLOYEE WORKFLOW                    │
└─────────────────────────────────────────────────────────────────┘

INPUT → PROCESSING → APPROVAL → ACTION → LOGGING
  ↓         ↓           ↓          ↓         ↓
Email    Reads      You decide  Sends    Records
WhatsApp messages   approve    emails   everything
Files    Plans      or reject  posts    in vault
```

### Real Example: Client Asks for Invoice via WhatsApp

```
1. INPUT: Client sends WhatsApp: "Hey, can you send me the invoice?"
        ↓
2. WATCHER: WhatsApp Watcher detects message + keyword "invoice"
        ↓
3. ACTION FILE: Creates Needs_Action/WHATSAPP_client_invoice.md
        ↓
4. PLAN GENERATOR: Creates Plans/Plan_send_invoice_client.md
        ↓
5. EMAIL MCP: Drafts email with invoice attached
        ↓
6. APPROVAL: Creates Pending_Approval/EMAIL_invoice_client.md
        ↓
7. YOU: Review and move file to Approved/ folder
        ↓
8. EXECUTE: Sends email to client
        ↓
9. LOG: Records everything in Accounting/Email_Log.md
```

### Folder Structure You'll Use

```
AI_Employee_Vault/
├── Dashboard.md              ← Your main control panel
├── Needs_Action/             ← New tasks arrive here
├── Plans/                    ← AI creates plans here
├── Pending_Approval/         ← Needs YOUR decision
├── Approved/                 ← You approved, AI executes
├── Done/                     ← Completed tasks
└── Logs/                     ← Everything recorded here
```

---

## Free Services Setup

### ❗ Important: Your Contact Info

**DO NOT put your actual phone number/email in code files!**

Instead, we'll use secure configuration:

```bash
# Create .env file (NEVER commit to GitHub)
# File: Personal-AI-Employee-FTEs/.env
```

### Service 1: Email - Gmail (100% Free)

**Why Gmail:**
- ✅ Completely free
- ✅ 15GB storage
- ✅ Easy API setup
- ✅ Reliable

**Setup Steps:**

#### Step 1: Enable Gmail API

1. Go to: https://console.cloud.google.com/
2. Create new project (name: "AI Employee")
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`

#### Step 2: Alternative - SMTP (Easier, No API Needed)

Use Gmail SMTP directly (no API setup):

```python
# In .env file
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=rafay16031@gmail.com
SMTP_PASSWORD=your-app-password  # Generate from Google Account settings
```

**Generate App Password:**
1. Go to: https://myaccount.google.com/security
2. Enable 2-Factor Authentication
3. Go to: https://myaccount.google.com/apppasswords
4. Create app password for "Mail"
5. Use this password (NOT your regular password)

---

### Service 2: WhatsApp - Playwright Browser Automation (100% Free)

**Why Browser Automation:**
- ✅ Completely free (no API costs)
- ✅ Uses WhatsApp Web directly
- ✅ No phone number registration needed
- ✅ Works with your existing WhatsApp

**⚠️ Security Note:**
- Your WhatsApp number (03161163799) stays on YOUR phone
- Session stored locally in vault
- NEVER share session files

**Setup:**

```bash
# Install Playwright
pip install playwright
playwright install chromium

# Create session folder
mkdir -p AI_Employee_Vault/.whatsapp_session
```

**First-Time Login:**

```bash
# Run interactive mode (you'll scan QR code)
python watchers/whatsapp_watcher.py AI_Employee_Vault \
  --session-path AI_Employee_Vault/.whatsapp_session \
  --interactive
```

1. Browser opens with WhatsApp Web QR code
2. Scan with your phone (03161163799)
3. Session saved automatically
4. Done! Now monitors your WhatsApp

---

### Service 3: LinkedIn - Browser Automation (100% Free)

**Why Browser Automation:**
- ✅ Free (no API needed)
- ✅ Uses LinkedIn.com directly
- ✅ Full control over posts

**Setup:**

```bash
# Create session folder
mkdir -p AI_Employee_Vault/.linkedin_session

# First-time login
python skills/linkedin_poster.py AI_Employee_Vault \
  --action login \
  --session-path AI_Employee_Vault/.linkedin_session \
  --interactive
```

1. Browser opens LinkedIn login
2. Log in with your account
3. Session saved
4. Ready to post!

---

### Service 4: AI Reasoning - Qwen via OpenRouter (Free Tier)

**Options:**

#### Option A: OpenRouter Free Tier (Recommended)

1. Go to: https://openrouter.ai/
2. Create account with rafay16031@gmail.com
3. Get free API key
4. Free models available:
   - Qwen 2.5 Coder (free)
   - Other open-source models

```bash
# In .env file
OPENROUTER_API_KEY=your-free-api-key
QWEN_MODEL=qwen/qwen-2.5-coder-32b-instruct
```

#### Option B: Local AI (Completely Free, No API)

If you have good GPU:

```bash
# Install Ollama
# Download from: https://ollama.ai/

# Download free model
ollama pull qwen2.5-coder

# Use local model
export OPENROUTER_API_KEY=local
export QWEN_MODEL=ollama/qwen2.5-coder
```

---

## Step-by-Step Configuration

### Step 1: Create .env File

Create file: `Personal-AI-Employee-FTEs/.env`

```bash
# ===========================================
# AI Employee Configuration
# For: Rafay (rafay16031@gmail.com)
# ===========================================

# --- AI Model (Choose ONE) ---

# Option A: OpenRouter (Free Tier)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
QWEN_MODEL=qwen/qwen-2.5-coder-32b-instruct

# Option B: Local Ollama (Uncomment if using)
# OPENROUTER_API_KEY=local
# QWEN_MODEL=ollama/qwen2.5-coder

# --- Gmail Configuration ---
GMAIL_SMTP_SERVER=smtp.gmail.com
GMAIL_SMTP_PORT=587
GMAIL_USER=rafay16031@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# --- WhatsApp Configuration ---
WHATSAPP_SESSION_PATH=AI_Employee_Vault/.whatsapp_session
WHATSAPP_KEYWORDS=urgent,asap,invoice,payment,help,quote,pricing

# --- LinkedIn Configuration ---
LINKEDIN_SESSION_PATH=AI_Employee_Vault/.linkedin_session
LINKEDIN_POSTING_TIME=09:00

# --- Vault Configuration ---
VAULT_PATH=AI_Employee_Vault

# --- Safety Settings ---
DRY_RUN=false
MAX_EMAILS_PER_DAY=50
REQUIRE_APPROVAL=true
```

### Step 2: Install All Dependencies

```bash
cd Personal-AI-Employee-FTEs

# Install Python packages
pip install -r requirements.txt
pip install playwright
playwright install chromium

# Verify installation
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright OK')"
python -c "import openai; print('✅ OpenAI Client OK')"
```

### Step 3: Authenticate Services

```bash
# 1. WhatsApp Authentication
python watchers/whatsapp_watcher.py AI_Employee_Vault \
  --session-path AI_Employee_Vault/.whatsapp_session \
  --interactive

# 2. LinkedIn Authentication
python skills/linkedin_poster.py AI_Employee_Vault \
  --action login \
  --session-path AI_Employee_Vault/.linkedin_session \
  --interactive

# 3. Gmail Test (SMTP)
python skills/email_mcp_client.py AI_Employee_Vault \
  --action draft \
  --to "rafay16031@gmail.com" \
  --subject "Test Email" \
  --body "This is a test from your AI Employee!"
```

### Step 4: Configure Your Business Goals

Edit: `AI_Employee_Vault/Business_Goals.md`

```markdown
---
last_updated: 2026-03-31
owner: Rafay
email: rafay16031@gmail.com
whatsapp: 03161163799
---

# Business Goals

## Q2 2026 Objectives

### Revenue Target
- Monthly goal: PKR 500,000
- Current MTD: PKR 0

### Active Projects
1. [Your Project 1]
2. [Your Project 2]

## LinkedIn Strategy

### Posting Schedule
- Frequency: 3 times per week
- Days: Tuesday, Wednesday, Thursday
- Time: 9:00 AM PKT

### Content Themes
1. Business updates
2. Industry insights
3. Client success stories

### Brand Voice
- Professional yet approachable
- Urdu + English mix acceptable
- Focus on value delivery

## Email Rules

### Auto-approve These Contacts
- [Add frequent contacts here]

### Always Require Approval
- New contacts
- Payments over PKR 10,000
- Contract-related emails

## WhatsApp Keywords

Always notify immediately:
- urgent
- asap
- emergency
- payment received
- invoice
```

### Step 5: Update Company Handbook

Edit: `AI_Employee_Vault/Company_Handbook.md`

```markdown
---
version: 1.0
owner: Rafay
---

# Company Handbook

## Approval Thresholds

### Payments
- Under PKR 5,000: Auto-approve to known vendors
- PKR 5,000 - 50,000: Require approval
- Over PKR 50,000: Require approval + written justification

### Emails
- Known contacts: Auto-draft, auto-send if < 100 words
- New contacts: Always require approval
- Attachments: Always require approval

### Social Media
- All posts: Require approval before publishing
- Comments: Auto-monitor, flag for review
```

---

## Daily Usage Guide

### Morning Routine (5 minutes)

```bash
# 1. Check Dashboard
cat AI_Employee_Vault/Dashboard.md

# 2. Check pending approvals
ls AI_Employee_Vault/Pending_Approval/

# 3. Review overnight activity
tail -50 AI_Employee_Vault/Logs/orchestrator_*.log
```

### Processing Tasks

**When you see files in `Pending_Approval/`:**

1. **Review:** Open file and read content
2. **Decide:**
   - ✅ Approve → Move to `Approved/`
   - ❌ Reject → Move to `Rejected/` with notes
   - ✏️ Edit → Move to `Plans/` with comments

**Example:**

```bash
# See what needs approval
ls AI_Employee_Vault/Pending_Approval/

# Output might show:
# - EMAIL_APPROVAL_invoice_client.md
# - LINKEDIN_POST_achievement.md

# Review file
cat AI_Employee_Vault/Pending_Approval/EMAIL_APPROVAL_invoice_client.md

# If OK, approve:
mv AI_Employee_Vault/Pending_Approval/EMAIL_APPROVAL_invoice_client.md \
   AI_Employee_Vault/Approved/

# AI will execute automatically (if orchestrator running)
```

### Creating LinkedIn Posts

```bash
# AI drafts post
python skills/linkedin_poster.py AI_Employee_Vault \
  --action draft \
  --topic "New business milestone" \
  --post-type achievement

# Review draft
cat AI_Employee_Vault/Plans/Plan_linkedin_*.md

# If good, move to approval
mv AI_Employee_Vault/Plans/Plan_linkedin_*.md \
   AI_Employee_Vault/Pending_Approval/

# After you approve (move to Approved/), post:
python skills/linkedin_poster.py AI_Employee_Vault \
  --action post \
  --file "AI_Employee_Vault/Approved/Plan_linkedin_*.md"
```

### Checking Email Log

```bash
# View sent emails
cat AI_Employee_Vault/Accounting/Email_Log.md
```

---

## Example Scenarios

### Scenario 1: Client Asks for Invoice via WhatsApp

**What Happens:**

1. Client (03001234567) sends: "Bhai, invoice bhej do January ki"
2. WhatsApp Watcher detects keyword "invoice"
3. Creates: `Needs_Action/WHATSAPP_03001234567_20260331.md`
4. Plan Generator creates: `Plans/Plan_send_invoice.md`
5. Email MCP drafts email with invoice
6. Creates: `Pending_Approval/EMAIL_APPROVAL_invoice.md`
7. **YOU review and approve**
8. Email sent to client
9. Logged in `Accounting/Email_Log.md`

**Your Actions:**
- Wait for approval notification
- Review draft in Pending_Approval/
- Move to Approved/ if correct
- Done! ✅

---

### Scenario 2: Post LinkedIn Update

**What Happens:**

1. You tell AI: "Post about our new service launch"
2. AI drafts LinkedIn post
3. Creates: `Plans/Plan_linkedin_service_launch.md`
4. **YOU review content**
5. Move to Pending_Approval/
6. AI schedules for 9:00 AM tomorrow
7. **YOU give final approval**
8. Post published at scheduled time

**Your Actions:**
- Review draft content
- Approve for scheduling
- Final approve before posting
- Post goes live! ✅

---

### Scenario 3: Daily Briefing

**Every morning at 8:00 AM:**

AI automatically:
1. Checks overnight WhatsApp messages
2. Checks new emails
3. Reviews pending tasks
4. Creates daily summary

**You receive:** `Briefings/2026-03-31_Morning_Briefing.md`

```markdown
# Morning Briefing - March 31, 2026

## Overnight Activity
- WhatsApp messages: 3 (1 urgent)
- Emails: 5 new (2 require response)
- Pending approvals: 2

## Today's Priorities
1. Send invoice to Client A (approved, ready to send)
2. Respond to urgent WhatsApp from Partner
3. Review LinkedIn post draft

## Revenue This Month
- Total: PKR 125,000
- Invoices sent: 8
- Invoices paid: 5
```

---

### Scenario 4: Payment Received Notification

**What Happens:**

1. Bank SMS/Email: "PKR 50,000 received from ABC Corp"
2. You forward email to AI or drop in folder
3. AI logs to accounting
4. Updates Dashboard
5. Marks invoice as paid
6. Sends thank you email to client (with approval)

**Your Actions:**
- Forward payment confirmation
- AI handles rest automatically! ✅

---

## Running The System

### Option 1: Manual (Start/Stop When Needed)

```bash
# Start watchers (run in separate terminals)

# Terminal 1: WhatsApp Watcher
python watchers/whatsapp_watcher.py AI_Employee_Vault \
  --session-path AI_Employee_Vault/.whatsapp_session

# Terminal 2: Orchestrator
python orchestrator.py AI_Employee_Vault --interval 60

# Terminal 3: Gmail Watcher (if using)
python watchers/gmail_watcher.py AI_Employee_Vault \
  --credentials credentials.json
```

### Option 2: Automated (Runs All Day)

Create `start_all.bat` (Windows):

```batch
@echo off
start "WhatsApp Watcher" python watchers/whatsapp_watcher.py AI_Employee_Vault --session-path AI_Employee_Vault/.whatsapp_session
timeout /t 5
start "Orchestrator" python orchestrator.py AI_Employee_Vault --interval 60
timeout /t 5
start "Approval Processor" python skills/approval_workflow.py AI_Employee_Vault --execute-approved
echo AI Employee started!
```

**Run:** Double-click `start_all.bat`

### Option 3: Windows Task Scheduler (Fully Automatic)

```powershell
# Create-ScheduledTasks.ps1

$vault = "C:\path\to\AI_Employee_Vault"
$project = "C:\path\to\Personal-AI-Employee-FTEs"
$python = "C:\Python311\python.exe"

# WhatsApp Watcher (runs at login)
$action = New-ScheduledTaskAction -Execute $python `
  -Argument "watchers/whatsapp_watcher.py $vault --session-path $vault\.whatsapp_session" `
  -WorkingDirectory $project
$trigger = New-ScheduledTaskTrigger -AtLogon
Register-ScheduledTask -TaskName "AI Employee - WhatsApp" `
  -Action $action -Trigger $trigger -User $env:USERNAME

# Orchestrator (every hour)
$action = New-ScheduledTaskAction -Execute $python `
  -Argument "orchestrator.py $vault --once" `
  -WorkingDirectory $project
$trigger = New-ScheduledTaskTrigger -Once (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
Register-ScheduledTask -TaskName "AI Employee - Hourly" `
  -Action $action -Trigger $trigger

# Daily Briefing (8 AM daily)
$action = New-ScheduledTaskAction -Execute $python `
  -Argument "skills/plan_generator.py $vault --auto-generate" `
  -WorkingDirectory $project
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
Register-ScheduledTask -TaskName "AI Employee - Daily Briefing" `
  -Action $action -Trigger $trigger
```

**Run as Administrator:**
```powershell
.\Create-ScheduledTasks.ps1
```

---

## Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| Gmail | FREE | 15GB storage included |
| WhatsApp Web | FREE | Uses your existing number |
| LinkedIn | FREE | Basic account sufficient |
| Playwright | FREE | Open-source library |
| Qwen AI (OpenRouter) | FREE TIER | ~1000 requests/day free |
| Local AI (Ollama) | FREE | If you have good GPU |
| **TOTAL** | **FREE** | 🎉 |

---

## Security Checklist

- [ ] `.env` file in `.gitignore` (never commit!)
- [ ] Session folders not synced to cloud
- [ ] App passwords used (not regular passwords)
- [ ] 2FA enabled on Google account
- [ ] Regular backup of vault (except sessions)
- [ ] Approval workflow enabled for sensitive actions

```bash
# Add to .gitignore
.env
*.session
.whatsapp_session/
.linkedin_session/
.gmail_token.json
credentials.json
```

---

## Quick Start Commands

```bash
# 1. Start everything
bash start_all.sh  # or start_all.bat on Windows

# 2. Check status
ls AI_Employee_Vault/Needs_Action/
ls AI_Employee_Vault/Pending_Approval/
cat AI_Employee_Vault/Dashboard.md

# 3. Process approvals
mv AI_Employee_Vault/Pending_Approval/*.md AI_Employee_Vault/Approved/

# 4. View logs
tail -f AI_Employee_Vault/Logs/orchestrator_*.log

# 5. Stop everything
taskkill /F /IM python.exe  # Windows
# or
pkill -f python  # Linux/Mac
```

---

## Support & Resources

- **Documentation:** `SILVER_TIER_SETUP.md`
- **Skill Docs:** `.qwen/skills/*/SKILL.md`
- **Blueprint:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`

---

*Workflow Guide v1.0 - Created for Rafay*  
*Last Updated: 2026-03-31*  
*All services: 100% FREE*
