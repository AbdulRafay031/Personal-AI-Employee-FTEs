# 🤖 LinkedIn Job Auto-Applier - Phase 1

## ✅ PHASE 1 COMPLETE!

**Status:** Local Automation - Runs when laptop is ON  
**Schedule:** Every 4 hours (Windows Task Scheduler)  
**Applications/Day:** 20 (to avoid LinkedIn ban)

---

## 🎯 NEW FEATURES (Updated)

### 🔥 Priority-Based Application System

| Priority | Location | Time Posted | Action |
|----------|----------|-------------|--------|
| **P1 - HIGHEST** | Karachi, Pakistan | Last 24 hours | ⚡ Apply IMMEDIATELY |
| **P2 - HIGH** | Remote (UAE, USA, UK, Japan, Australia) | Last 24 hours | ⚡ Apply IMMEDIATELY |
| **P3 - MEDIUM** | Remote (Worldwide) | Last 24 hours | ✓ Apply today |
| **P4 - LOW** | Any location | Older than 24h | ⏳ Queue for later |

### 🌍 Location Preferences

```
Priority 1: Karachi, Pakistan (Local)
Priority 2: Remote positions in:
  - UAE (Dubai)
  - USA (United States)
  - UK (United Kingdom)
  - Japan (Tokyo)
  - Australia (Sydney)
Priority 3: Remote (Worldwide)
```

### 💰 Paid-Only Filter

✅ Automatically filters out unpaid internships  
✅ Detects salary/stipend mentions  
✅ Skips "volunteer" or "unpaid" positions

---

## 📋 What Phase 1 Does

| Feature | Status | Description |
|---------|--------|-------------|
| **LinkedIn Login** | ✅ Automatic | Uses saved session |
| **Job Search** | ✅ Automatic | Karachi → Remote (UAE,USA,UK,Japan,AU) |
| **Time Priority** | ✅ Automatic | Last 24 hours FIRST |
| **Location Filter** | ✅ Automatic | Matches preferred locations |
| **Paid Filter** | ✅ Automatic | Skips unpaid positions |
| **Easy Apply** | ✅ Automatic | Auto-fills applications |
| **Resume Upload** | ✅ Automatic | If resume.pdf exists |
| **Tracking** | ✅ Automatic | Saves to Obsidian vault |
| **Scheduling** | ✅ Automatic | Windows Task Scheduler |
| **24/7 Running** | ⚠️ Laptop must be ON | Runs when computer is on |

---

## 🚀 Quick Start (3 Steps)

### Step 1: Update Your Profile

Edit: `AI_Employee_Vault\profile.yaml`

```yaml
full_name: "Abdul Rafay"
email: "rafay16031@gmail.com"
phone: "+92 316 1163799"

titles:
  - "Frontend Developer"
  - "AI Developer"
  - "MERN Stack Developer"
  - "Agentic AI Engineer"

search_keywords:
  - "Frontend Developer Internship"
  - "AI Developer Internship"
  - "MERN Stack Developer"
  - "Remote"
```

### Step 2: Add Your Resume

Save your resume as PDF:
```
AI_Employee_Vault\resume.pdf
```

### Step 3: Setup Scheduler

Run as Administrator:
```bash
setup_job_scheduler.bat
```

---

## 📁 Folder Structure

```
AI_Employee_Vault/
├── profile.yaml              # Your profile data
├── resume.pdf                # Your resume (add this)
├── Jobs/
│   ├── Applied/              # Successfully applied jobs
│   ├── Saved/                # Jobs found (not yet applied)
│   └── .processed_jobs.json  # Track processed jobs
├── Logs/
│   └── job_applier_*.log     # Daily logs
└── .linkedin_jobs_session/   # Browser session
```

---

## 🎯 How It Works

```
┌─────────────────────────────────────────────────┐
│  EVERY 4 HOURS (when laptop is ON)              │
├─────────────────────────────────────────────────┤
│ 1. Launch browser with saved session            │
│ 2. Navigate to LinkedIn Jobs                    │
│ 3. Search for keywords (Frontend, AI, MERN...)  │
│ 4. Filter "Easy Apply" jobs only                │
│ 5. For each relevant job:                       │
│    a. Extract job details                       │
│    b. Check if already applied                  │
│    c. Check relevance to your skills            │
│    d. Click "Easy Apply"                        │
│    e. Auto-fill phone, upload resume            │
│    f. Submit application                        │
│    g. Save to Jobs/Applied/                     │
│ 6. Stop after 20 applications (daily limit)     │
│ 7. Log results                                  │
└─────────────────────────────────────────────────┘
```

---

## ⚙️ Configuration

### Daily Application Limit

Edit `linkedin_job_applier.py`:
```python
self.max_applications_per_day = 20  # Change this
self.delay_between_applications = 120  # Seconds between applications
```

### Search Keywords

Edit `AI_Employee_Vault/profile.yaml`:
```yaml
search_keywords:
  - "Frontend Developer Internship"
  - "AI Developer"
  - "MERN Stack"
  - "Remote"
  - "Entry Level"
```

### Exclude Keywords

Jobs with these words will be skipped:
```yaml
exclude_keywords:
  - "Senior"
  - "Lead"
  - "Manager"
  - "5+ years"
  - "10+ years"
```

---

## 📊 View Applications

### Check Applied Jobs

```bash
# View all applied jobs
dir AI_Employee_Vault\Jobs\Applied\

# Open specific job
start AI_Employee_Vault\Jobs\Applied\Job_*.md
```

### Check Logs

```bash
# View today's log
start AI_Employee_Vault\Logs\job_applier_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log
```

### Check Dashboard

The Dashboard.md will be updated with:
- Jobs found today
- Applications submitted
- Success rate

---

## 🔧 Manual Commands

### Run Once Manually

```bash
python linkedin_job_applier.py --max-jobs 20
```

### Run in Background (Headless)

```bash
python linkedin_job_applier.py --max-jobs 20 --headless
```

### Check Scheduled Task

```bash
# View task
schtasks /Query /TN "LinkedIn_Job_AutoApplier"

# Run manually
schtasks /Run /TN "LinkedIn_Job_AutoApplier"

# Delete task
schtasks /Delete /TN "LinkedIn_Job_AutoApplier" /F
```

---

## ⚠️ Important Warnings

### 1. LinkedIn Rate Limits

- **Max 20 applications/day** (to avoid ban)
- **2 minute delay** between applications
- LinkedIn may show CAPTCHA after many applications

### 2. Account Safety

- ✅ Uses your real LinkedIn account
- ✅ Applies only to relevant jobs
- ✅ Human-like delays between actions
- ⚠️ Don't increase application limit too high
- ⚠️ Solve CAPTCHAs manually if they appear

### 3. Laptop Must Be ON

- Phase 1 runs ONLY when laptop is on
- For 24/7: Wait for Phase 2 (Cloud Deployment)

---

## 🎯 Expected Results

### Per Day (when laptop is on):
- **Jobs Scanned:** 50-100
- **Relevant Found:** 10-20
- **Applications Submitted:** 10-20 (limit)

### Per Week:
- **Applications:** 50-100
- **Interviews:** 2-5 (typical 3-5% response rate)
- **Offers:** 0-2 (depends on market)

---

## 🐛 Troubleshooting

### "Playwright not installed"

```bash
pip install playwright
playwright install chromium
```

### "Login timeout"

1. Browser will open
2. Login to LinkedIn manually
3. Script will continue automatically

### "No Easy Apply jobs found"

- LinkedIn may not have Easy Apply jobs for your keywords
- Try different keywords in profile.yaml
- Wait for new jobs to be posted

### "Application failed"

- Check log file for details
- Some jobs require additional info not in your profile
- Manual application may be needed

---

## 📈 Phase 1 Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Setup Time | 10 min | ✅ Complete |
| First Run | < 5 min | Ready |
| Applications/Day | 20 | Configured |
| Success Rate | > 90% | Testing |
| Ban Risk | Low | ✅ Safe limits |

---

## 🚀 What's Next: Phase 2

**Phase 2: Cloud Deployment** (Coming Next)

- ✅ Runs 24/7 (even when laptop is OFF)
- ✅ AWS/Google Cloud Free Tier
- ✅ WhatsApp notifications for new jobs
- ✅ Remote approval workflow
- ✅ Cloud-Local sync

**Estimated Setup:** 1-2 hours  
**Cost:** Rs. 0 (Free Tier) or Rs. 500-1000/month (VPS)

---

## ✅ Phase 1 Checklist

- [ ] Profile updated in `AI_Employee_Vault/profile.yaml`
- [ ] Resume saved as `AI_Employee_Vault/resume.pdf`
- [ ] Scheduler setup: `setup_job_scheduler.bat`
- [ ] Test run: `python linkedin_job_applier.py`
- [ ] Check logs in `AI_Employee_Vault/Logs/`
- [ ] Verify applications in `AI_Employee_Vault/Jobs/Applied/`

---

**🎉 PHASE 1 COMPLETE! READY TO START!**

Run `setup_job_scheduler.bat` to begin automatic job applications!

---

**Questions?** Check logs in `AI_Employee_Vault/Logs/job_applier_*.log`
