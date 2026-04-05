# 🎯 START HERE - Rafay's AI Employee Setup

**Follow these steps EXACTLY in order**

---

## 📖 STEP 1: Read These 3 Files First (15 minutes)

**Read in this order:**

### 1. QUICK_START.md (5 min)
**Location:** `C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs\QUICK_START.md`

**What you'll learn:**
- 5-minute setup overview
- What packages to install
- How to get API keys
- How to start the system

### 2. WORKFLOW_GUIDE.md (10 min)
**Location:** `C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs\WORKFLOW_GUIDE.md`

**What you'll learn:**
- Complete workflow explanation
- How WhatsApp monitoring works
- How email sending works
- How LinkedIn posting works
- Real examples with your email/WhatsApp

### 3. This File - START_HERE.md (5 min)
**What you'll learn:**
- Exact steps to follow
- What to do if errors occur
- Testing checklist

---

## ⚙️ STEP 2: Install Python Packages (5 minutes)

### Open Command Prompt:
1. Press `Windows + R`
2. Type: `cmd`
3. Press `Enter`

### Navigate to Project:
```bash
cd "C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs"
```

### Install Packages:
```bash
pip install -r requirements.txt
```

### Install Playwright:
```bash
pip install playwright
playwright install chromium
```

**Wait for installation to complete** (may take 2-3 minutes)

---

## 🔑 STEP 3: Get Your FREE API Keys (10 minutes)

### A. OpenRouter API Key (FREE) - 5 minutes

1. **Go to:** https://openrouter.ai/
2. **Click:** "Sign In" (top right)
3. **Sign up with:** rafay16031@gmail.com
4. **Verify email** (check inbox)
5. **Click:** Your name → "Keys"
6. **Click:** "Create Key"
7. **Name it:** "AI Employee"
8. **Copy the key** (starts with `sk-or-v1-`)

**Save this key somewhere safe!**

### B. Gmail App Password (FREE) - 5 minutes

1. **Go to:** https://myaccount.google.com/security
2. **Sign in with:** rafay16031@gmail.com
3. **Enable 2-Factor Authentication** (if not already enabled)
   - Click "2-Step Verification"
   - Follow steps to enable
4. **Go to:** https://myaccount.google.com/apppasswords
5. **Select app:** "Mail"
6. **Select device:** "Other (Custom name)"
7. **Type:** "AI Employee"
8. **Click:** "Generate"
9. **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)

**Save this password somewhere safe!**

---

## 📝 STEP 4: Create .env File (3 minutes)

### Copy Example File:
```bash
copy .env.example .env
```

### Edit .env File:
1. **Open:** `.env` file in Notepad
2. **Find and replace these lines:**

```bash
# Line 10: Replace with your OpenRouter key
OPENROUTER_API_KEY=sk-or-v1-YOUR-ACTUAL-KEY-HERE

# Line 29: Replace with your Gmail app password
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop

# Line 59: Your WhatsApp number (already set)
YOUR_WHATSAPP_NUMBER=923161163799
```

3. **Save** the file
4. **Close** Notepad

---

## ✅ STEP 5: Run Verification Script (2 minutes)

### Run:
```bash
setup_verify.bat
```

### Expected Output:
```
========================================
  AI Employee - Setup Verification
========================================

[1/8] Checking Python installation...
Python 3.11.x
[OK] Python found

[2/8] Checking pip...
[OK] pip found

[3/8] Checking required packages...
[OK] playwright installed
[OK] openai installed
[OK] python-dotenv installed
...

[4/8] Checking Playwright browsers...
[OK] Playwright working

[5/8] Checking vault structure...
[OK] AI_Employee_Vault exists
[OK] Needs_Action folder exists
...

[6/8] Checking .env file...
[OK] .env file found

[7/8] Checking skills...
[OK] Skills directory exists
[OK] WhatsApp Watcher skill found
[OK] LinkedIn Poster skill found
[OK] Email MCP skill found
...

[8/8] Checking watcher scripts...
[OK] WhatsApp Watcher script found
[OK] Orchestrator script found

========================================
  Setup Verification Complete!
========================================
```

### If You See [OK] for Everything:
✅ **Ready to start!**

### If You See [FAIL] or [MISSING]:
❌ **Fix the issue before proceeding**
- [FAIL] Python → Install Python from https://python.org/
- [MISSING] packages → Run: `pip install -r requirements.txt`
- [FAIL] Playwright → Run: `playwright install chromium`

---

## 🚀 STEP 6: Authenticate WhatsApp (3 minutes)

### Run:
```bash
python watchers/whatsapp_watcher.py AI_Employee_Vault ^
  --session-path AI_Employee_Vault\.whatsapp_session ^
  --interactive
```

### What Happens:
1. **Browser window opens**
2. **WhatsApp Web QR code appears**
3. **Open WhatsApp on your phone** (03161163799)
4. **Tap:** Menu (⋮) → "Linked Devices"
5. **Tap:** "Link a Device"
6. **Scan QR code** with phone camera
7. **Browser shows WhatsApp Web**
8. **Close browser window**

### Success Message:
```
WhatsApp Watcher initialized
Session saved to: AI_Employee_Vault\.whatsapp_session
```

---

## 🔗 STEP 7: Authenticate LinkedIn (2 minutes)

### Run:
```bash
python skills/linkedin_poster.py AI_Employee_Vault ^
  --action login ^
  --session-path AI_Employee_Vault\.linkedin_session ^
  --interactive
```

### What Happens:
1. **Browser window opens**
2. **LinkedIn login page appears**
3. **Log in with your LinkedIn account**
4. **Close browser window after login**

### Success Message:
```
LinkedIn Poster initialized
Session saved to: AI_Employee_Vault\.linkedin_session
```

---

## 🧪 STEP 7: Test the System (5 minutes)

### Test 1: Send Yourself WhatsApp Message

1. **From another phone**, send WhatsApp to 03161163799:
   ```
   test invoice
   ```

2. **Wait 30 seconds**

3. **Check folder:**
   ```bash
   dir AI_Employee_Vault\Needs_Action
   ```

4. **You should see:**
   ```
   WHATSAPP_*.md file created!
   ```

### Test 2: Check Dashboard

1. **Open:**
   ```bash
   start AI_Employee_Vault\Dashboard.md
   ```

2. **You should see:**
   - Status table
   - Recent activity
   - Business metrics

### Test 3: Create Email Draft

1. **Run:**
   ```bash
   python skills/email_mcp_client.py AI_Employee_Vault ^
     --action draft ^
     --to "rafay16031@gmail.com" ^
     --subject "Test Email" ^
     --body "This is a test from your AI Employee!"
   ```

2. **Check:**
   ```bash
   dir AI_Employee_Vault\Plans
   ```

3. **You should see:**
   ```
   EMAIL_DRAFT_*.md file created!
   ```

---

## ▶️ STEP 8: Start AI Employee (1 minute)

### Run:
```bash
start_ai_employee.bat
```

### What Opens:
1. **Window 1:** WhatsApp Watcher (monitoring messages)
2. **Window 2:** Orchestrator (processing tasks)
3. **Window 3:** Approval Processor (executing approved actions)

### Keep These Windows Open!
- **Minimize** them (don't close)
- They run in background
- AI works while you do other tasks

---

## 📋 STEP 9: Daily Usage Routine

### Morning (2 minutes):

1. **Open Dashboard:**
   ```bash
   start AI_Employee_Vault\Dashboard.md
   ```

2. **Check Pending Approvals:**
   ```bash
   dir AI_Employee_Vault\Pending_Approval
   ```

3. **Approve items:**
   - Open each file
   - Read content
   - If OK → Move to `Approved/` folder

### Throughout Day:
- AI monitors WhatsApp automatically
- AI checks emails automatically
- AI creates plans automatically
- You just approve when asked

### Evening (1 minute):

1. **Check completed tasks:**
   ```bash
   dir AI_Employee_Vault\Done /od
   ```

---

## 🆘 Troubleshooting

### Problem: setup_verify.bat shows [FAIL]

**Solution:**
```bash
# If Python missing:
# Download from https://python.org/ and install

# If packages missing:
pip install -r requirements.txt

# If Playwright fails:
playwright install chromium
```

### Problem: WhatsApp QR code not showing

**Solution:**
```bash
# Delete session and retry
rmdir /s /q AI_Employee_Vault\.whatsapp_session
mkdir AI_Employee_Vault\.whatsapp_session

python watchers/whatsapp_watcher.py AI_Employee_Vault ^
  --session-path AI_Employee_Vault\.whatsapp_session ^
  --interactive
```

### Problem: .env file errors

**Solution:**
1. Open `.env` in Notepad
2. Make sure NO quotes around values
3. Make sure no spaces around `=`
4. Save and retry

### Problem: start_ai_employee.bat closes immediately

**Solution:**
- Check `.env` file exists
- Check AI_Employee_Vault folder exists
- Run `setup_verify.bat` first to verify

---

## ✅ Final Checklist

After completing all steps, verify:

- [ ] Read QUICK_START.md
- [ ] Read WORKFLOW_GUIDE.md
- [ ] Python packages installed
- [ ] OpenRouter API key obtained
- [ ] Gmail app password obtained
- [ ] .env file created and filled
- [ ] setup_verify.bat shows all [OK]
- [ ] WhatsApp authenticated (QR scanned)
- [ ] LinkedIn authenticated (logged in)
- [ ] Test WhatsApp message created file in Needs_Action/
- [ ] Test email draft created file in Plans/
- [ ] start_ai_employee.bat runs successfully
- [ ] Three terminal windows open and running

**If ALL checked → 🎉 You're ready!**

---

## 📚 Next Steps

Now that setup is complete:

1. **Read Daily Usage Guide:**
   - `WORKFLOW_GUIDE.md` → "Daily Usage Guide" section

2. **Configure Your Preferences:**
   - Edit `AI_Employee_Vault\Business_Goals.md`
   - Edit `AI_Employee_Vault\Company_Handbook.md`

3. **Start Using:**
   - Send test WhatsApp messages
   - Create email drafts
   - Approve actions
   - Check dashboard daily

4. **Get Help:**
   - Wednesday Meetings: 10:00 PM PKT
   - Zoom: https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1

---

## 📞 Quick Reference

| File | Purpose |
|------|---------|
| `QUICK_START.md` | 5-minute overview |
| `WORKFLOW_GUIDE.md` | Complete workflow |
| `SILVER_TIER_SETUP.md` | Detailed Silver Tier guide |
| `.env.example` | Configuration template |
| `setup_verify.bat` | Verify installation |
| `start_ai_employee.bat` | Start system |

| Command | What it does |
|---------|-------------|
| `setup_verify.bat` | Checks everything installed |
| `start_ai_employee.bat` | Starts all services |
| `dir AI_Employee_Vault\Pending_Approval` | See items needing approval |
| `start AI_Employee_Vault\Dashboard.md` | Open dashboard |

---

**🎯 Ready? Start with STEP 1 - Read the files!**

*Last Updated: 2026-03-31*
*Created for: Rafay (rafay16031@gmail.com)*
