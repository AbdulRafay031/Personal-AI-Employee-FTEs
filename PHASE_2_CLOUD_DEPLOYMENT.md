# ☁️ PHASE 2: CLOUD DEPLOYMENT GUIDE

## 🎯 What Phase 2 Does

| Feature | Phase 1 (Local) | Phase 2 (Cloud) |
|---------|----------------|-----------------|
| **Runtime** | Laptop must be ON | ✅ 24/7 (even when laptop OFF) |
| **Location** | Your laptop | AWS/Google Cloud Server |
| **Cost** | Rs. 0 | Rs. 0 (Free Tier 12 months) |
| **Notifications** | Check logs manually | ✅ WhatsApp alerts |
| **Approval** | Automatic | ✅ Remote approval option |
| **Sync** | Local only | ✅ Cloud-Local sync |

---

## 📋 Cloud Deployment Options

### Option 1: AWS EC2 (Recommended)

**Free Tier:** 750 hours/month for 12 months  
**Specs:** t2.micro or t3.micro (1 vCPU, 1GB RAM)  
**OS:** Ubuntu 22.04  
**Cost:** Rs. 0 (Free Tier)

### Option 2: Google Cloud Compute Engine

**Free Tier:** e2-micro instance (2 vCPU, 1GB RAM)  
**OS:** Ubuntu 22.04  
**Cost:** Rs. 0 (Free Tier)

### Option 3: Oracle Cloud Free Tier

**Free Tier:** Always Free (4 ARM cores, 24GB RAM)  
**OS:** Ubuntu 22.04  
**Cost:** Rs. 0 (Always Free)

### Option 4: VPS (Paid Alternative)

**Providers:** DigitalOcean, Linode, Vultr  
**Cost:** $5-10/month (Rs. 400-800)  
**Specs:** 1 vCPU, 1GB RAM, 25GB SSD

---

## 🛠️ What We'll Deploy

```
┌─────────────────────────────────────────────────┐
│  CLOUD SERVER (AWS/Google/Oracle)               │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  Job Auto-Applier (Main Script)         │   │
│  │  - Runs every 4 hours via cron          │   │
│  │  - Searches LinkedIn jobs               │   │
│  │  - Applies to relevant positions        │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  WhatsApp Notification Bot              │   │
│  │  - Sends new job alerts                 │   │
│  │  - Daily summary reports                │   │
│  │  - Approval requests                    │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  Cloud-Local Sync                       │   │
│  │  - Sync applications to your laptop     │   │
│  │  - Upload new resumes/profile updates   │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  Obsidian Vault (Subset)                │   │
│  │  - Jobs/Applied/                        │   │
│  │  - Logs/                                │   │
│  │  - profile.yaml                         │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────┐
│  YOUR LAPTOP (Local)                            │
│                                                 │
│  - Full Obsidian Vault                          │
│  - Dashboard monitoring                         │
│  - Receive WhatsApp notifications               │
│  - Review applications                          │
└─────────────────────────────────────────────────┘
```

---

## 📦 Deployment Steps

### Step 1: Create Cloud Account

**AWS Free Tier:**
1. Go to: https://aws.amazon.com/free/
2. Click "Create an AWS Account"
3. Enter email, password, account name
4. Add credit/debit card (for verification, won't charge)
5. Verify phone number
6. Wait for account activation (5-10 minutes)

**Google Cloud Free Tier:**
1. Go to: https://cloud.google.com/free
2. Click "Get started for free"
3. Sign in with Google account
4. Fill in profile
5. Add payment method (verification only)
6. Activate free trial

**Oracle Cloud Free Tier:**
1. Go to: https://www.oracle.com/cloud/free/
2. Click "Start for free"
3. Fill in registration
4. Verify email and phone
5. Add payment method
6. Wait for approval

---

### Step 2: Create Cloud Server

**AWS EC2:**
```bash
# 1. Go to EC2 Console
# 2. Click "Launch Instance"
# 3. Configure:
Name: ai-job-applier
AMI: Ubuntu Server 22.04 LTS
Instance Type: t2.micro (Free Tier eligible)
Key Pair: Create new (download .pem file)
Security Group: Allow SSH (port 22)
Storage: 8GB GP2
# 4. Click "Launch Instance"
# 5. Wait for instance to be "running"
# 6. Note Public IP address
```

**Google Cloud:**
```bash
# 1. Go to Compute Engine
# 2. Click "Create Instance"
# 3. Configure:
Name: ai-job-applier
Region: us-central1 (Iowa) - Free Tier
Zone: us-central1-a
Machine Type: e2-micro
Boot Disk: Ubuntu 22.04 LTS, 10GB
Firewall: Allow HTTP, HTTPS
# 4. Click "Create"
# 5. Note External IP address
```

---

### Step 3: Connect to Server

**Windows (PowerShell):**
```powershell
# For AWS
cd C:\path\to\key.pem
ssh -i "key.pem" ubuntu@YOUR_EC2_IP

# For Google Cloud
ssh ubuntu@YOUR_GCP_IP
```

**First Time Setup:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install -y python3 python3-pip python3-venv

# Install Playwright dependencies
sudo apt install -y chromium-browser

# Install Node.js (for some dependencies)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create directory
mkdir ~/ai-job-applier
cd ~/ai-job-applier
```

---

### Step 4: Deploy Application

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install playwright pyyaml
playwright install chromium

# Upload your files (from your laptop)
# Use SCP or SFTP:
scp -i key.pem linkedin_job_applier.py ubuntu@YOUR_IP:~/ai-job-applier/
scp -i key.pem profile.yaml ubuntu@YOUR_IP:~/ai-job-applier/

# Or use Git:
git clone https://github.com/your-username/Personal-AI-Employee-FTEs.git
cd Personal-AI-Employee-FTEs
```

---

### Step 5: Setup Cron Job (Auto-Run)

```bash
# Edit crontab
crontab -e

# Add this line (runs every 4 hours):
0 */4 * * * cd /home/ubuntu/ai-job-applier && /home/ubuntu/ai-job-applier/venv/bin/python linkedin_job_applier.py --max-jobs 20 >> /home/ubuntu/ai-job-applier/cron.log 2>&1

# Save and exit
```

---

### Step 6: Setup WhatsApp Notifications

See: `WHATSAPP_CLOUD_SETUP.md` (next section)

---

## 🔧 Configuration

### Update Profile for Cloud

Edit `profile.yaml`:
```yaml
# Add cloud settings
cloud_deployment:
  enabled: true
  timezone: "Asia/Karachi"
  whatsapp_notifications: true
  whatsapp_number: "+923161163799"
  
# Application limits for cloud
max_applications_per_day: 20
delay_between_applications: 120

# Notification settings
notify_on_new_job: true
notify_on_application: true
daily_summary: true
daily_summary_time: "20:00"
```

---

## 📊 Monitoring

### Check Cloud Server Status

**AWS:**
```bash
# EC2 Console → Instances
# Check: Status = "running"
# Check: CPU Utilization
```

**Google Cloud:**
```bash
# Compute Engine → VM instances
# Check: Status = "Running"
# Check: CPU, Memory
```

### Check Application Logs

**SSH into server:**
```bash
ssh -i key.pem ubuntu@YOUR_IP

# View recent logs
tail -f ~/ai-job-applier/cron.log

# View today's job log
cat ~/ai-job-applier/AI_Employee_Vault/Logs/job_applier_*.log
```

### Check Applications

**Via SSH:**
```bash
# List applied jobs
ls -la ~/ai-job-applier/AI_Employee_Vault/Jobs/Applied/

# Count today's applications
ls ~/ai-job-applier/AI_Employee_Vault/Jobs/Applied/ | wc -l
```

**Via WhatsApp:**
- Receive instant notifications
- Daily summary at 8:00 PM
- On-demand status requests

---

## 🔄 Cloud-Local Sync

### Option 1: Git Sync

**On Cloud Server:**
```bash
# Setup git repo
git init
git remote add origin https://github.com/your-username/job-applier-cloud.git

# Auto-commit daily
0 23 * * * cd /home/ubuntu/ai-job-applier && git add -A && git commit -m "Daily sync" && git push origin main
```

**On Your Laptop:**
```bash
# Pull updates
git pull origin main

# View applied jobs
cd AI_Employee_Vault/Jobs/Applied/
```

### Option 2: rsync Sync

**On Your Laptop (PowerShell):**
```powershell
# Sync from cloud to local
rsync -avz -e "ssh -i key.pem" ubuntu@YOUR_IP:~/ai-job-applier/AI_Employee_Vault/Jobs/Applied/ ./AI_Employee_Vault/Jobs/Applied/

# Sync profile updates to cloud
rsync -avz -e "ssh -i key.pem" ./AI_Employee_Vault/profile.yaml ubuntu@YOUR_IP:~/ai-job-applier/
```

### Option 3: Google Drive Sync

**Setup on Cloud:**
```bash
# Install rclone
curl https://rclone.org/install.sh | sudo bash

# Configure Google Drive
rclone config
# Follow prompts to setup Google Drive

# Sync command
rclone sync /home/ubuntu/ai-job-applier/AI_Employee_Vault/Jobs/Applied gdrive:AI-Employee-Backup/Jobs/Applied
```

---

## 💰 Cost Breakdown

### AWS Free Tier (12 Months)

| Resource | Usage | Cost |
|----------|-------|------|
| EC2 t2.micro | 750 hrs/month | $0 |
| S3 Storage | 5GB | $0 |
| Data Transfer | 1GB/month | $0 |
| **TOTAL** | | **$0/month** |

### After Free Tier (Month 13+)

| Resource | Usage | Cost |
|----------|-------|------|
| EC2 t2.micro | 750 hrs/month | ~$8-10 |
| S3 Storage | 5GB | ~$0.10 |
| **TOTAL** | | **~$10/month (Rs. 800)** |

### Google Cloud Free Tier

| Resource | Usage | Cost |
|----------|-------|------|
| e2-micro | 750 hrs/month | $0 |
| Storage | 30GB | $0 |
| **TOTAL** | | **$0/month (Always Free)** |

---

## ⚠️ Important Notes

### Security

1. **Use SSH Keys** - Never use password authentication
2. **Setup Firewall** - Only allow port 22 (SSH)
3. **Regular Updates** - Run `sudo apt update` weekly
4. **Monitor Usage** - Check AWS/GCP console monthly
5. **Backup Data** - Sync applications to multiple locations

### Cost Control

1. **Set Budget Alerts** - AWS Budgets / GCP Budgets
2. **Monitor Usage** - Check daily for first week
3. **Stop Instance** - When not needed (can restart later)
4. **Use Free Tier** - Stay within free limits
5. **Delete if Unused** - Avoid surprise charges

### Performance

1. **Instance Type** - t2.micro is sufficient for job applying
2. **Memory** - 1GB RAM is enough
3. **Storage** - 8-10GB is plenty
4. **Bandwidth** - Minimal usage (text-based)
5. **CPU** - Low usage (runs 4x/day for short periods)

---

## 🎯 Next Steps

After cloud deployment:

1. ✅ **Test Cloud Running**
   - Manually trigger first run
   - Check logs
   - Verify applications submitted

2. ✅ **Setup WhatsApp Notifications**
   - Configure WhatsApp Cloud API
   - Test message sending
   - Setup daily summaries

3. ✅ **Configure Sync**
   - Choose sync method (Git/rsync/Drive)
   - Test sync from cloud to local
   - Verify files sync correctly

4. ✅ **Monitor First Week**
   - Check logs daily
   - Review applications
   - Adjust settings if needed

---

## 📞 Support

**Common Issues:**

1. **Can't connect via SSH**
   - Check security group allows port 22
   - Verify key file permissions: `chmod 400 key.pem`
   - Use correct username (ubuntu for Ubuntu)

2. **Python not found**
   - Install: `sudo apt install python3 python3-pip`
   - Check: `python3 --version`

3. **Playwright fails**
   - Install dependencies: `playwright install chromium`
   - May need: `sudo apt install chromium-browser`

4. **Cron job not running**
   - Check cron log: `grep CRON /var/log/syslog`
   - Verify crontab: `crontab -l`
   - Test manually first

---

**Ready to deploy? Let me know which cloud provider you choose and I'll create the deployment scripts!** 🚀
