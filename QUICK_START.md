# 🚀 Quick Start Guide - AI Employee for Rafay

**Email:** rafay16031@gmail.com  
**WhatsApp:** 03161163799  
**Cost:** 100% FREE

---

## ⚡ 5-Minute Setup

### Step 1: Install Python Packages (2 minutes)

```bash
cd C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs

pip install -r requirements.txt
pip install playwright
playwright install chromium
```

### Step 2: Create .env File (2 minutes)

```bash
# Copy the example
copy .env.example .env

# Edit .env file and fill in:
# 1. OPENROUTER_API_KEY - Get from https://openrouter.ai/ (free)
# 2. GMAIL_APP_PASSWORD - Get from Google Account settings
# 3. YOUR_WHATSAPP_NUMBER = 923161163799
```

**Get OpenRouter API Key (FREE):**
1. Go to https://openrouter.ai/
2. Sign up with rafay16031@gmail.com
3. Click "Keys" → "Create Key"
4. Copy key to .env file

**Get Gmail App Password (FREE):**
1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication
3. Go to https://myaccount.google.com/apppasswords
4. Create app password for "Mail"
5. Copy to .env file

### Step 3: Verify Setup (30 seconds)

```bash
setup_verify.bat
```

Should show all [OK] messages.

### Step 4: Start AI Employee (30 seconds)

```bash
start_ai_employee.bat
```

Three windows will open:
- WhatsApp Watcher
- Orchestrator
- Approval Processor

---

## 📱 How to Use

### Test WhatsApp Monitoring

1. **Send yourself a WhatsApp message:** "test invoice"
2. **Check folder:** `AI_Employee_Vault\Needs_Action\`
3. **New file appears:** `WHATSAPP_*.md`
4. **AI creates plan:** `AI_Employee_Vault\Plans\Plan_*.md`

### Check Status

Open: `AI_Employee_Vault\Dashboard.md`

Shows:
- Pending tasks
- Completed today
- Recent activity

### Approve Actions

When AI needs your approval:

1. **Check folder:** `AI_Employee_Vault\Pending_Approval\`
2. **Open file** and read what AI wants to do
3. **If OK:** Move file to `AI_Employee_Vault\Approved\`
4. **AI executes automatically**

---

## 🎯 What You Can Do

### 1. WhatsApp Message Monitoring

**Setup:**
```bash
# First time - scan QR code
python watchers/whatsapp_watcher.py AI_Employee_Vault ^
  --session-path AI_Employee_Vault\.whatsapp_session ^
  --interactive
```

**How it works:**
- Someone sends: "Need invoice for January"
- AI detects keyword "invoice"
- Creates task in `Needs_Action/`
- AI drafts response
- Asks for your approval
- Sends after you approve

### 2. Email Sending

**Draft email:**
```bash
python skills/email_mcp_client.py AI_Employee_Vault ^
  --action draft ^
  --to "client@example.com" ^
  --subject "Invoice #123" ^
  --body "Please find attached invoice..."
```

**Check draft:** `AI_Employee_Vault\Plans\EMAIL_DRAFT_*.md`

**Approve and send:** Move to `Approved/` folder

### 3. LinkedIn Posts

**Create post:**
```bash
python skills/linkedin_poster.py AI_Employee_Vault ^
  --action draft ^
  --topic "New business milestone" ^
  --post-type achievement
```

**Review:** `AI_Employee_Vault\Plans\Plan_linkedin_*.md`

**Post:** Move to `Approved/` → AI publishes

---

## 📁 Folder Structure You Need

```
AI_Employee_Vault/
├── Dashboard.md              ← Check this daily
├── Needs_Action/             ← New tasks appear here
├── Plans/                    ← AI creates drafts here
├── Pending_Approval/         ← Needs YOUR decision
├── Approved/                 ← You approved → AI executes
├── Done/                     ← Completed tasks
└── Logs/                     ← Everything recorded
```

---

## 🔧 Daily Routine

### Morning (2 minutes)

```bash
# 1. Open Dashboard
start AI_Employee_Vault\Dashboard.md

# 2. Check pending approvals
dir AI_Employee_Vault\Pending_Approval

# 3. Approve items (move to Approved folder)
```

### Throughout Day

- WhatsApp messages auto-monitored
- New tasks appear in `Needs_Action/`
- AI creates plans automatically
- You approve via `Pending_Approval/`

### Evening (1 minute)

```bash
# Check what was completed
dir AI_Employee_Vault\Done
```

---

## 💰 Cost: Rs. 0 (Completely Free!)

| Service | Cost | Why |
|---------|------|-----|
| Gmail | FREE | 15GB free storage |
| WhatsApp Web | FREE | Uses your existing number |
| LinkedIn | FREE | Basic account works |
| Playwright | FREE | Open-source |
| Qwen AI | FREE | OpenRouter free tier |
| **TOTAL** | **FREE** | 🎉 |

---

## 🆘 Troubleshooting

### WhatsApp Not Working

```bash
# Delete session and re-authenticate
rmdir /s /q AI_Employee_Vault\.whatsapp_session
mkdir AI_Employee_Vault\.whatsapp_session

python watchers/whatsapp_watcher.py AI_Employee_Vault ^
  --session-path AI_Employee_Vault\.whatsapp_session ^
  --interactive
```

### Email Not Sending

1. Check Gmail app password is correct in `.env`
2. Enable 2FA on Google Account
3. Test with dry run:
   ```bash
   set DRY_RUN=true
   python skills/email_mcp_client.py AI_Employee_Vault --action send ^
     --to "rafay16031@gmail.com" ^
     --subject "Test" ^
     --body "Test email"
   ```

### AI Not Responding

1. Check orchestrator is running (terminal window open)
2. Check logs: `AI_Employee_Vault\Logs\orchestrator_*.log`
3. Restart: Close all windows → Run `start_ai_employee.bat`

---

## 📚 Full Documentation

- **Complete Workflow:** `WORKFLOW_GUIDE.md`
- **Silver Tier Setup:** `SILVER_TIER_SETUP.md`
- **Skill Documentation:** `.qwen\skills\*\SKILL.md`

---

## 📞 Support

- **Wednesday Meetings:** 10:00 PM PKT
- **Zoom:** https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **YouTube:** https://www.youtube.com/@panaversity

---

## ✅ First Test Checklist

After setup, verify everything works:

- [ ] Send WhatsApp message with "test"
- [ ] Check `Needs_Action/` for new file
- [ ] Check `Plans/` for generated plan
- [ ] Create test email draft
- [ ] Move to `Approved/` and verify sends
- [ ] Check `Dashboard.md` updates

**If all pass → You're ready! 🎉**

---

*Quick Start Guide v1.0 - For Rafay*  
*Last Updated: 2026-03-31*
