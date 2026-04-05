# 🚀 AWS EC2 QUICK START - 30 MINUTE DEPLOYMENT

## ⏱️ Time Estimate: 30 Minutes Total

| Step | Time | Status |
|------|------|--------|
| 1. Create AWS Account | 10 min | ⏳ |
| 2. Launch EC2 Instance | 5 min | ⏳ |
| 3. Connect via SSH | 5 min | ⏳ |
| 4. Run Setup Commands | 5 min | ⏳ |
| 5. Upload Files | 3 min | ⏳ |
| 6. Test Deployment | 2 min | ⏳ |
| **TOTAL** | **30 min** | 🔄 |

---

## 📝 PRE-REQUISITES

Before starting, make sure you have:

- [ ] Email address (for AWS account)
- [ ] Phone number (for verification)
- [ ] Credit/Debit card (for verification - won't be charged)
- [ ] 30 minutes of uninterrupted time
- [ ] Your LinkedIn login credentials

---

## 🎯 STEP-BY-STEP DEPLOYMENT

### STEP 1: Create AWS Account (10 minutes)

** URL:** https://portal.aws.amazon.com/billing/signup

```
1. Enter email address → Continue
2. Create password → Continue
3. Contact info:
   - Full Name: Abdul Rafay
   - Phone: +92 316 1163799
   - Address: Karachi, Pakistan
4. Payment information:
   - Enter your card details
   - (Verification charge: $1, refunded)
5. Identity verification:
   - Enter SMS code
6. Support plan:
   - Select: Basic (Free)
7. Click: "Complete Sign Up"
8. Wait for activation email (5-15 minutes)
```

✅ **Done when:** You receive "Your AWS Account is Ready" email

---

### STEP 2: Launch EC2 Instance (5 minutes)

**🔗 URL:** https://console.aws.amazon.com/ec2/

```
1. Login to AWS Console
2. Click: "Launch instance" (orange button)

3. Configure:
   Name: ai-job-applier
   AMI: Ubuntu Server 22.04 LTS
   Instance type: t2.micro (Free Tier)
   
4. Key pair:
   Click: "Create new key pair"
   Name: ai-job-applier-key
   Download: ai-job-applier-key.pem
   ⚠️ SAVE THIS FILE! You can't download again!
   
5. Network:
   ✓ Allow SSH from anywhere
   
6. Storage: 8 GiB (default)

7. Click: "Launch instance"

8. Wait: Instance state → "running" (2-5 minutes)

9. Copy: Public IP (e.g., 54.123.45.67)
```

✅ **Done when:** Instance shows "running" and you have Public IP

---

### STEP 3: Connect via SSH (5 minutes)

**On your laptop (PowerShell):**

```powershell
# 1. Navigate to key file
cd C:\Users\YourUsername\Downloads

# 2. Set permissions
icacls ai-job-applier-key.pem /inheritance:r
icacls ai-job-applier-key.pem /grant %USERNAME%:F

# 3. Connect (replace with your IP)
ssh -i "ai-job-applier-key.pem" ubuntu@54.123.45.67

# 4. Type "yes" when asked
# 5. You should see: ubuntu@ip-xxx-xxx-xxx-xxx:~$
```

✅ **Done when:** You see Ubuntu welcome message

---

### STEP 4: Run Setup Commands (5 minutes)

**In SSH session, copy-paste these commands:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install -y python3 python3-pip python3-venv

# Install Chromium
sudo apt install -y chromium-browser

# Create directory
mkdir -p ~/ai-job-applier
cd ~/ai-job-applier

# Setup Python
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Install Playwright
pip install playwright pyyaml
playwright install chromium
playwright install-deps chromium

# Create folders
mkdir -p AI_Employee_Vault/Jobs/Applied
mkdir -p AI_Employee_Vault/Jobs/Saved
mkdir -p AI_Employee_Vault/Logs
mkdir -p AI_Employee_Vault/.linkedin_jobs_session
```

✅ **Done when:** All commands complete without errors

---

### STEP 5: Upload Files (3 minutes)

**On your laptop (new PowerShell window):**

```powershell
# Navigate to project
cd "C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs"

# Upload main script (replace IP)
scp -i "ai-job-applier-key.pem" linkedin_job_applier.py ubuntu@54.123.45.67:~/ai-job-applier/

# Upload profile
scp -i "ai-job-applier-key.pem" AI_Employee_Vault\profile.yaml ubuntu@54.123.45.67:~/ai-job-applier/AI_Employee_Vault/

# Upload resume (optional)
scp -i "ai-job-applier-key.pem" AI_Employee_Vault\resume.pdf ubuntu@54.123.45.67:~/ai-job-applier/AI_Employee_Vault/
```

✅ **Done when:** All files uploaded (no errors)

---

### STEP 6: Test Deployment (2 minutes)

**Back in SSH session:**

```bash
# Activate environment
cd ~/ai-job-applier
source venv/bin/activate

# Test run
python linkedin_job_applier.py --max-jobs 5

# Check logs
cat AI_Employee_Vault/Logs/job_applier_*.log

# Check applications
ls AI_Employee_Vault/Jobs/Applied/
```

✅ **Done when:** You see job search results in logs

---

### STEP 7: Setup Auto-Run (3 minutes)

**In SSH session:**

```bash
# Create runner script
cat > run_job_applier.sh << 'EOF'
#!/bin/bash
cd /home/ubuntu/ai-job-applier
source venv/bin/activate
python linkedin_job_applier.py --max-jobs 20 >> /home/ubuntu/ai-job-applier/cron.log 2>&1
EOF

chmod +x run_job_applier.sh

# Add to crontab
crontab -e

# Add this line at the end:
0 */4 * * * /home/ubuntu/ai-job-applier/run_job_applier.sh

# Save: Ctrl+O, Enter
# Exit: Ctrl+X

# Verify
crontab -l
```

✅ **Done when:** Crontab shows your scheduled job

---

## ✅ DEPLOYMENT COMPLETE!

### What You Have Now:

✅ EC2 instance running 24/7  
✅ Job auto-applier installed  
✅ Auto-runs every 4 hours  
✅ Logs all applications  
✅ Free for 12 months  

---

## 📊 MONITORING

### Check Status (Anytime)

**Via SSH:**
```bash
# Is instance running?
ps aux | grep python

# View recent logs
tail -f ~/ai-job-applier/cron.log

# Check applications today
ls ~/ai-job-applier/AI_Employee_Vault/Jobs/Applied/ | wc -l
```

**Via AWS Console:**
```
EC2 → Instances → ai-job-applier
Status: "running"
CPU: Should be low (< 10%)
```

---

## 🔧 TROUBLESHOOTING

### SSH Connection Failed

```
Error: Permission denied (publickey)
Fix: Check key file permissions
icacls ai-job-applier-key.pem /grant %USERNAME%:F

Error: Connection timed out
Fix: Check security group allows SSH (port 22)
```

### Python Not Found

```bash
sudo apt install -y python3 python3-pip
```

### Playwright Installation Failed

```bash
sudo apt install -y libgbm1 libnss3 libatk1.0-0
playwright install chromium
```

### Cron Job Not Running

```bash
# Check cron service
sudo service cron status

# View logs
grep CRON /var/log/syslog

# Test manually
./run_job_applier.sh
```

---

## 💰 COST TRACKING

### Free Tier Limits (12 Months)

| Resource | Limit | Your Usage |
|----------|-------|------------|
| EC2 t2.micro | 750 hrs/month | ~720 hrs (24/7) ✓ |
| Storage | 30 GB | ~1 GB ✓ |
| Data Transfer | 1 GB/month | ~0.1 GB ✓ |

### Setup Billing Alert

```
1. AWS Console → Billing → Budgets
2. Create Budget
3. Type: Cost
4. Limit: $1 USD
5. Email: your-email@gmail.com
6. Create
```

You'll get email if costs exceed $1 (they won't with free tier).

---

## 📱 NEXT: WHATSAPP NOTIFICATIONS

After EC2 deployment is working, setup WhatsApp:

1. Go to: `WHATSAPP_CLOUD_SETUP.md`
2. Create Meta Developer account
3. Get API credentials
4. Configure on EC2
5. Receive job alerts on WhatsApp!

---

## 🎯 QUICK REFERENCE

### Important Commands

```bash
# Connect to EC2
ssh -i "key.pem" ubuntu@YOUR_IP

# Check if running
ps aux | grep python

# View logs
tail -f cron.log

# Check applications
ls AI_Employee_Vault/Jobs/Applied/

# Restart cron
sudo service cron restart

# Check disk space
df -h

# Check memory
free -h
```

### Important Files

```
~/ai-job-applier/
├── linkedin_job_applier.py      # Main script
├── run_job_applier.sh           # Cron runner
├── cron.log                     # Cron logs
├── AI_Employee_Vault/
│   ├── profile.yaml             # Your settings
│   ├── Jobs/Applied/            # Applied jobs
│   ├── Logs/                    # App logs
│   └── .linkedin_jobs_session/  # Browser session
```

### Important URLs

```
AWS Console: https://console.aws.amazon.com/
EC2 Dashboard: https://console.aws.amazon.com/ec2/
Billing: https://console.aws.amazon.com/billing/
```

---

## 📞 SUPPORT

**Documentation:**
- Full Guide: `AWS_EC2_DEPLOYMENT.md`
- Phase 2 Overview: `PHASE_2_COMPLETE.md`
- Job Applier Guide: `JOB_AUTO_APPLIER_GUIDE.md`

**AWS Resources:**
- EC2 Docs: https://docs.aws.amazon.com/ec2/
- Free Tier: https://aws.amazon.com/free/
- Support: https://console.aws.amazon.com/support/

---

**🎉 CONGRATULATIONS! YOUR AI JOB AUTO-APPLIER IS NOW RUNNING 24/7 ON AWS!** 🚀
