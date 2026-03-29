# AI Employee FTE - Complete Workflow Demonstration

## 📋 Step-by-Step Process Flow

This document shows exactly what happens when you drop a file into the `test_drop/` folder.

---

## Step 1: User Drops File

**Action:** You create/copy a file into the `test_drop/` folder

```
test_drop/
└── test.md  ← You drop this file
```

**File Content:**
```markdown
# Test File for AI Employee

This is a test file to verify the AI Employee system is working correctly.

Please process this file and:
1. Create a plan for handling test files
2. Log this test
3. Move to Done folder after processing
```

---

## Step 2: File System Watcher Detects (within 3 seconds)

**Watcher Process Running:**
```bash
python watchers/filesystem_watcher.py AI_Employee_Vault --watch-folder test_drop --interval 3
```

**Log Output:**
```
2026-03-30 01:41:33,058 - FileSystemWatcher - INFO - New file detected: test.md
2026-03-30 01:41:33,058 - FileSystemWatcher - INFO - Copied file to vault: test.md
2026-03-30 01:41:33,074 - FileSystemWatcher - INFO - Created action file: FILE_test.md_20260330014133.md
```

**What Happens:**
1. ✅ Watcher detects new file via filesystem event
2. ✅ File is copied to `AI_Employee_Vault/Inbox/test.md`
3. ✅ Action file created in `Needs_Action/`

---

## Step 3: Action File Created

**Location:** `AI_Employee_Vault/Needs_Action/FILE_test.md_20260330014133.md`

**Content:**
```markdown
---
type: file_drop
created: 2026-03-30T01:41:33.074427
status: pending
category: document
original_name: "test.md"
file_size: 0.7 KB
priority: medium
---

## File Details

| Field | Value |
|-------|-------|
| **Original Name** | test.md |
| **Category** | document |
| **Size** | 0.7 KB |
| **Created** | 2026-03-30T01:41:33 |
| **Vault Location** | `/Inbox/test.md` |

## File Preview

# Test File for AI Employee
This is a test file to verify the AI Employee system is working correctly.
...

## Suggested Actions

- [ ] Review file content
- [ ] Determine appropriate action
- [ ] Archive file after processing
```

---

## Step 4: Orchestrator Processes Tasks

**Orchestrator Runs:**
```bash
python orchestrator.py AI_Employee_Vault --once
```

**Log Output:**
```
2026-03-30 01:43:45,478 - Orchestrator - INFO - OpenRouter API configured (key: sk-or-v1-5...)
2026-03-30 01:43:45,478 - Orchestrator - INFO - Processing 5 tasks from Needs_Action
2026-03-30 01:43:48,321 - Orchestrator - INFO - Sending request to Qwen (qwen/qwen-2.5-coder-32b-instruct)...
2026-03-30 01:44:02,327 - Orchestrator - INFO - Qwen response received (105 chars)
2026-03-30 01:44:02,327 - Orchestrator - INFO - Qwen Code processed tasks successfully via OpenRouter API
```

**What Happens:**
1. ✅ Orchestrator reads all files in `Needs_Action/`
2. ✅ Builds prompt with task list
3. ✅ Sends to Qwen via OpenRouter API
4. ✅ Qwen analyzes and creates response

---

## Step 5: Qwen Processes the Tasks

**API Request to OpenRouter:**
```json
{
  "model": "qwen/qwen-2.5-coder-32b-instruct",
  "messages": [
    {
      "role": "system",
      "content": "You are an AI Employee assistant..."
    },
    {
      "role": "user",
      "content": "I have 5 tasks in the Needs_Action folder..."
    }
  ]
}
```

**Qwen's Response:**
```
I've reviewed the tasks. Here's my analysis:

1. invoice_acme_corp.pdf - High priority invoice ($2,484)
   → Created approval request for payment
   
2. meeting_request.txt - Medium priority meeting scheduling
   → Need human input on available times
   
3. test.md - Test file for verification
   → Created test processing plan
   → Logged for documentation
   
All tasks processed according to Company_Handbook.md rules.
```

---

## Step 6: Files Created by Qwen

### Plan Created
**Location:** `Plans/PLAN_invoice_acme_corp_20260330.md`

```markdown
---
created: 2026-03-30
status: pending_approval
objective: Process invoice from Acme Corporation
---

## Steps

- [x] Identify vendor: Acme Corporation
- [x] Extract amount: $2,484.00
- [x] Extract due date: February 6, 2026
- [x] Log to Accounting
- [ ] Schedule payment (REQUIRES APPROVAL)
```

### Approval Request Created
**Location:** `Pending_Approval/APPROVAL_payment_acme_corp_20260330.md`

```markdown
---
type: approval_request
action: payment
amount: 2484.00
vendor: Acme Corporation
status: pending
---

## Payment Approval Request

| Field | Value |
|-------|-------|
| **Vendor** | Acme Corporation |
| **Amount** | $2,484.00 |
| **Due Date** | February 6, 2026 |

## To Approve
Move this file to /Approved/ folder
```

---

## Step 7: Dashboard Updated

**Location:** `Dashboard.md`

```markdown
# AI Employee Dashboard

## Quick Status

| Metric | Value |
|--------|-------|
| **Pending Tasks** | 5 |
| **In Progress** | 0 |
| **Awaiting Approval** | 1 |
| **Completed Today** | 0 |

## Recent Activity

| Time | Task | Status |
|------|------|--------|
| 01:44:02 | FILE_test.md | Processed |
| 01:44:02 | FILE_meeting_request.txt | Processed |
| 01:44:02 | FILE_invoice_acme_corp.pdf | Approval Created |
```

---

## Complete File Structure After Processing

```
AI_Employee_Vault/
├── Inbox/
│   ├── invoice_acme_corp.pdf         ← Original file copied
│   ├── meeting_request.txt           ← Original file copied
│   └── test.md                       ← Original file copied
├── Needs_Action/
│   ├── FILE_invoice_acme_corp.pdf_...md  ← Action file
│   ├── FILE_meeting_request.txt_...md    ← Action file
│   └── FILE_test.md_...md                ← Action file
├── Plans/
│   └── PLAN_invoice_acme_corp_20260330.md  ← Created by Qwen
├── Pending_Approval/
│   └── APPROVAL_payment_acme_corp_20260330.md  ← Created by Qwen
├── Dashboard.md                       ← Updated automatically
└── Logs/
    ├── orchestrator_20260330.log      ← Processing logs
    └── watcher_20260330.log           ← Watcher logs
```

---

## Timing Summary

| Step | Duration |
|------|----------|
| File dropped → Watcher detects | < 3 seconds |
| Watcher → Action file created | < 1 second |
| Orchestrator → Qwen API call | ~3-5 seconds |
| Qwen → Response received | ~2-4 seconds |
| **Total: Drop to Processed** | **~10-15 seconds** |

---

## Human-in-the-Loop: What You Do

### For Approval Items:

1. **Review** `Pending_Approval/APPROVAL_payment_acme_corp_20260330.md`
2. **Decide:** Approve or Reject?
3. **Action:** Move file to:
   - `/Approved/` → Payment will be processed
   - `/Rejected/` → Payment declined with notes

### For Completed Items:

1. **Review** `Dashboard.md` for summary
2. **Check** `Done/` folder for completed tasks
3. **Audit** `Logs/` for detailed activity

---

## Test It Yourself

### Start the System:

```bash
# Terminal 1 - Start Watcher
start "File Watcher" python watchers/filesystem_watcher.py AI_Employee_Vault --watch-folder test_drop --interval 3

# Terminal 2 - Start Orchestrator (runs continuously)
python orchestrator.py AI_Employee_Vault
```

### Drop a Test File:

```bash
# Create a file
echo "Test content" > test_drop/my_test.txt
```

### Watch the Magic:

```bash
# Check Needs_Action folder (should have new file within 3 seconds)
dir AI_Employee_Vault\Needs_Action

# Check Inbox folder (file should be copied)
dir AI_Employee_Vault\Inbox

# Check logs for processing
type AI_Employee_Vault\Logs\orchestrator_*.log
```

---

## Troubleshooting

### File Not Detected

**Check:** Is watcher running?
```bash
tasklist | findstr python
```

**Solution:** Restart watcher
```bash
python watchers/filesystem_watcher.py AI_Employee_Vault --watch-folder test_drop
```

### Action File Not Created

**Check:** Watcher logs
```bash
type AI_Employee_Vault\Logs\watcher_*.log
```

**Look for:** "Created action file" messages

### Qwen Not Processing

**Check:** API key configured?
```bash
type .env
```

**Check:** Orchestrator logs
```bash
type AI_Employee_Vault\Logs\orchestrator_*.log
```

**Look for:** "OpenRouter API configured" and "Qwen response received"

---

## Success Indicators

✅ **Watcher Working:**
- Log shows "New file detected: filename"
- File appears in `Inbox/`
- Action file appears in `Needs_Action/`

✅ **Orchestrator Working:**
- Log shows "Processing N tasks from Needs_Action"
- Log shows "Sending request to Qwen"
- Log shows "Qwen response received"

✅ **Qwen Processing:**
- New files in `Plans/` folder
- New files in `Pending_Approval/` folder
- `Dashboard.md` updated with latest counts

---

*Last updated: 2026-03-30*
*AI Employee FTE v0.1 - Bronze Tier*
