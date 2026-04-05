# AWS EC2 DEPLOYMENT GUIDE
## AI Job Auto-Applier - Phase 2

---

## 📋 STEP 1: Create AWS Account (10 minutes)

### 1.1 Go to AWS Sign Up

**URL:** https://aws.amazon.com/

1. Click **"Create an AWS Account"** (top right)
2. Enter your email address
3. Click **"Continue"**

### 1.2 Account Information

```
AWS Account Name: Your name or company (e.g., "Abdul Rafay" or "My Job Applier")
Contact Information:
  - Full Name: Abdul Rafay
  - Phone Number: +92 316 1163799
  - Address: Karachi, Pakistan
```

### 1.3 Payment Information

**Important:** AWS won't charge you for Free Tier usage, but requires a card for verification.

```
Card Type: Visa / Mastercard / Debit Card
Card Number: [Your card]
Expiration: [Your card expiry]
Security Code: [CVV on back]
Billing Address: Same as above
```

**Note:** 
- AWS will charge $1 USD temporarily for verification (refunded)
- Free Tier usage: $0 for 12 months
- You won't be charged unless you exceed free tier limits

### 1.4 Identity Verification

1. **Enter your phone number**
2. **Receive SMS code**
3. **Enter the code** to verify

### 1.5 Select Support Plan

```
✓ Basic Support (FREE)
  - Access to AWS Free Tier
  - Customer Service
  - AWS Documentation
  - Health Status
```

**Click: "Complete Sign Up"**

### 1.6 Wait for Activation

- AWS will send confirmation email
- Account activation: 5-15 minutes
- You'll receive: "Your AWS Account is Ready"

---

## 📋 STEP 2: Launch EC2 Instance (15 minutes)

### 2.1 Go to EC2 Console

**URL:** https://console.aws.amazon.com/ec2/

Or:
1. Login to AWS Console: https://console.aws.amazon.com/
2. Search for "EC2" in top search bar
3. Click "EC2" under Services

### 2.2 Launch Instance

1. Click **"Launch instance"** button (orange)

### 2.3 Configure Instance

**Step 1: Name and tags**
```
Name: ai-job-applier
Add optional tags: (skip for now)
```

**Step 2: Application and OS Images (AMI)**
```
✓ Quick Start
✓ Amazon Linux 2023 AMI  (OR)
✓ Ubuntu Server 22.04 LTS  ← RECOMMENDED

Select: Ubuntu Server 22.04 LTS
```

**Step 3: Instance type**
```
Instance type: t2.micro  ← FREE TIER ELIGIBLE
Additional info: Burstable performance, 1 vCPU, 1 GiB memory
```

**Step 4: Key pair (login credentials)**
```
Key pair settings:
  ✓ Key pair type: RSA
  ✓ Private key format: .pem
  
Click: "Create new key pair"
Key pair name: ai-job-applier-key
Download: Save "ai-job-applier-key.pem" to your computer

⚠️ IMPORTANT: 
- Save this file safely!
- You cannot download it again!
- If lost, you must create new instance!
```

**Step 5: Network settings (Security group)**
```
Firewall (security group):
  ✓ Create security group
  ✓ Allow SSH traffic from: Anywhere (0.0.0.0/0)
  
Uncheck:
  ☐ Allow HTTP traffic from the internet
  ☐ Allow HTTPS traffic from the internet
```

**Step 6: Configure storage**
```
Root volume size: 8 GiB  ← Default (sufficient)
Volume type: gp2 (General Purpose SSD)
```

**Step 7: Advanced settings**
```
(Skip defaults - no changes needed)
```

**Step 8: Summary**
```
Review on the right panel:
  ✓ Name: ai-job-applier
  ✓ OS: Ubuntu 22.04
  ✓ Instance type: t2.micro
  ✓ Storage: 8 GiB
  ✓ Key pair: ai-job-applier-key
```

### 2.4 Launch Instance

1. Click **"Launch instance"** (orange button, right side)
2. Wait for "Success" message
3. Click **"Launch Instances"** (blue link)

### 2.5 Wait for Instance to Start

1. You'll see: "Instance state: pending"
2. Wait 2-5 minutes
3. Status changes to: "Instance state: running"
4. Note the **Public IP address** (e.g., 54.123.45.67)

**⚠️ IMPORTANT:** 
- Public IP changes if you stop/start instance
- For permanent IP, use Elastic IP (free when instance running)
- For now, use the Public IP shown

---

## 📋 STEP 3: Connect to EC2 via SSH (5 minutes)

### 3.1 Prepare SSH Key

**Windows:**
```
1. Find your downloaded key: ai-job-applier-key.pem
2. Right-click → Properties → Security
3. Click "Advanced"
4. Change owner to your username
5. Uncheck "Include inheritable permissions"
6. Click "Add" → Enter your username → OK
7. Check "Full control" → OK → Apply
```

**Or via PowerShell (easier):**
```powershell
# Navigate to Downloads folder
cd C:\Users\YourUsername\Downloads

# Set correct permissions
icacls ai-job-applier-key.pem /inheritance:r
icacls ai-job-applier-key.pem /grant YourUsername:F
```

### 3.2 Connect via SSH

**Option A: Using PowerShell (Recommended)**

```powershell
# Navigate to key location
cd C:\Users\YourUsername\Downloads

# Connect to EC2
ssh -i "ai-job-applier-key.pem" ubuntu@YOUR_PUBLIC_IP

# Example:
ssh -i "ai-job-applier-key.pem" ubuntu@54.123.45.67
```

**First time connection:**
```
The authenticity of host '54.123.45.67' can't be established.
ECDSA key fingerprint is SHA256:xxxxxxxxxxxxx.
Are you sure you want to continue connecting (yes/no/[fingerprint])?

Type: yes
```

**If connection successful:**
```
Welcome to Ubuntu 22.04 LTS (GNU/Linux ...)
ubuntu@ip-172-31-xx-xx:~$
```

**Option B: Using EC2 Instance Connect (Browser)**

1. Go to EC2 Console
2. Select your instance: "ai-job-applier"
3. Click **"Connect"** (top)
4. Select **"EC2 Instance Connect"** tab
5. Click **"Connect"** button
6. Browser opens SSH terminal

---

## 📋 STEP 4: Run Cloud Setup Script (10 minutes)

### 4.1 Update System

Once connected via SSH:

```bash
# Update package list
sudo apt update

# Upgrade packages
sudo apt upgrade -y
```

### 4.2 Install Python & Dependencies

```bash
# Install Python 3
sudo apt install -y python3 python3-pip python3-venv

# Install Chromium (for Playwright)
sudo apt install -y chromium-browser

# Install Node.js (for some dependencies)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 4.3 Create Application Directory

```bash
# Create directory
mkdir -p ~/ai-job-applier
cd ~/ai-job-applier

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 4.4 Install Job Applier

```bash
# Install Playwright
pip install playwright pyyaml

# Install Chromium browser for Playwright
playwright install chromium

# Install Playwright system dependencies
playwright install-deps chromium
```

### 4.5 Create Directory Structure

```bash
# Create folders
mkdir -p AI_Employee_Vault/Jobs/Applied
mkdir -p AI_Employee_Vault/Jobs/Saved
mkdir -p AI_Employee_Vault/Logs
mkdir -p AI_Employee_Vault/.linkedin_jobs_session
```

### 4.6 Create Profile Configuration

```bash
# Create profile file
cat > AI_Employee_Vault/profile.yaml << 'EOF'
# AI Job Applier Profile
full_name: "Abdul Rafay"
email: "rafay16031@gmail.com"
phone: "+92 316 1163799"
location: "Karachi, Pakistan"

titles:
  - "Frontend Developer"
  - "AI Developer"
  - "MERN Stack Developer"
  - "Agentic AI Engineer"

locations:
  - "Karachi, Pakistan"
  - "UAE (Remote)"
  - "USA (Remote)"
  - "UK (Remote)"
  - "Remote"

search_keywords:
  - "Frontend Developer Internship"
  - "AI Developer Internship"
  - "MERN Stack Developer"
  - "Agentic AI"
  - "LLM Developer"

exclude_unpaid: true
max_applications_per_day: 20
delay_between_applications: 120
EOF
```

---

## 📋 STEP 5: Upload Job Applier Script (5 minutes)

### Option A: Using SCP (from your laptop)

**Open new PowerShell window on your laptop:**

```powershell
# Navigate to your project folder
cd "C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs"

# Upload main script
scp -i "ai-job-applier-key.pem" linkedin_job_applier.py ubuntu@YOUR_EC2_IP:~/ai-job-applier/

# Upload profile (if you edited it locally)
scp -i "ai-job-applier-key.pem" AI_Employee_Vault/profile.yaml ubuntu@YOUR_EC2_IP:~/ai-job-applier/AI_Employee_Vault/

# Upload resume (if you have it)
scp -i "ai-job-applier-key.pem" AI_Employee_Vault/resume.pdf ubuntu@YOUR_EC2_IP:~/ai-job-applier/AI_Employee_Vault/
```

### Option B: Copy-Paste via SSH

**In your SSH session:**

```bash
# Create the file
nano linkedin_job_applier.py

# Paste the entire content of linkedin_job_applier.py
# (Copy from your local file and paste into nano)

# Save: Ctrl+O, Enter
# Exit: Ctrl+X
```

### Option C: Git Clone (if using GitHub)

```bash
# Install git
sudo apt install -y git

# Clone your repository
cd ~/ai-job-applier
git clone https://github.com/your-username/Personal-AI-Employee-FTEs.git .
```

---

## 📋 STEP 6: Test the Deployment (10 minutes)

### 6.1 Verify Files

```bash
# List files
ls -la ~/ai-job-applier/

# Should see:
# - linkedin_job_applier.py
# - AI_Employee_Vault/
# - venv/
```

### 6.2 Test Run (Manual)

```bash
# Activate virtual environment
cd ~/ai-job-applier
source venv/bin/activate

# Run once manually (5 jobs max)
python linkedin_job_applier.py --max-jobs 5
```

**What to expect:**
1. Browser launches (you won't see it - headless mode)
2. Navigates to LinkedIn
3. Searches for jobs
4. May ask you to login first time

**If you see login required:**
- The script will wait
- You need to login via browser (not possible on headless server)
- Solution: Run once with display, or use saved session

### 6.3 Check Logs

```bash
# View logs
cat AI_Employee_Vault/Logs/job_applier_*.log

# Or tail (live view)
tail -f AI_Employee_Vault/Logs/job_applier_*.log
```

### 6.4 Check Applications

```bash
# List applied jobs
ls -la AI_Employee_Vault/Jobs/Applied/

# Count applications
ls AI_Employee_Vault/Jobs/Applied/ | wc -l
```

---

## 📋 STEP 7: Setup Cron Job (Auto-Run) (5 minutes)

### 7.1 Create Runner Script

```bash
# Create runner script
cat > run_job_applier.sh << 'EOF'
#!/bin/bash
cd /home/ubuntu/ai-job-applier
source venv/bin/activate
python linkedin_job_applier.py --max-jobs 20 >> /home/ubuntu/ai-job-applier/cron.log 2>&1
EOF

# Make executable
chmod +x run_job_applier.sh
```

### 7.2 Setup Cron Job

```bash
# Edit crontab
crontab -e

# If asked for editor, choose nano (easier)

# Add this line at the end:
0 */4 * * * /home/ubuntu/ai-job-applier/run_job_applier.sh

# Save: Ctrl+O, Enter
# Exit: Ctrl+X
```

### 7.3 Verify Cron

```bash
# List cron jobs
crontab -l

# Should show:
# 0 */4 * * * /home/ubuntu/ai-job-applier/run_job_applier.sh
```

### 7.4 Test Cron

```bash
# Run manually to test
./run_job_applier.sh

# Check log
tail cron.log
```

---

## 📋 STEP 8: Setup Elastic IP (Optional but Recommended) (5 minutes)

**Why:** Public IP changes when you stop/start instance. Elastic IP stays permanent.

### 8.1 Allocate Elastic IP

1. Go to EC2 Console
2. Under "Network & Security" → **"Elastic IPs"**
3. Click **"Allocate Elastic IP address"**
4. Settings:
   - Border: Amazon's pool of IPv4 addresses
   - Customer owned IP pool: (leave default)
5. Click **"Allocate"**

### 8.2 Associate Elastic IP

1. Select your new Elastic IP
2. Click **"Actions"** → **"Associate Elastic IP address"**
3. Settings:
   - Resource type: Instance
   - Instance: Select "ai-job-applier"
   - Private IP: (auto-selected)
4. Click **"Associate"**

### 8.3 Note Your Elastic IP

```
Elastic IP: xx.xxx.xxx.xxx  ← This is now your permanent IP!
```

**Update your SSH commands:**
```powershell
# Use Elastic IP from now on
ssh -i "ai-job-applier-key.pem" ubuntu@YOUR_ELASTIC_IP
```

---

## 📋 STEP 9: Setup CloudWatch Alarms (Free) (5 minutes)

### 9.1 Create CPU Alarm

1. Go to EC2 Console
2. Select your instance
3. Click **"Manage CloudWatch alarms"**
4. Click **"Create alarm"**
5. Settings:
   - Metric: CPU Utilization
   - Threshold: > 80%
   - Period: 5 minutes
   - Datapoints: 1 out of 1
6. Notification:
   - SNS topic: Create new
   - Email: your-email@gmail.com
7. Click **"Create alarm"**

### 9.2 Create Status Check Alarm

1. Click **"Create alarm"** again
2. Settings:
   - Metric: Status Check Failed
   - Threshold: > 0
   - Period: 1 minute
3. Notification: Same email
4. Click **"Create alarm"**

---

## 📋 STEP 10: Verify Everything (5 minutes)

### Checklist

```bash
# 1. Check instance is running
# AWS Console → EC2 → Instances → State: "running"

# 2. Check SSH connection
ssh -i "key.pem" ubuntu@YOUR_IP
# Should connect successfully

# 3. Check Python is installed
python3 --version
# Should show: Python 3.10.x

# 4. Check Playwright is installed
source venv/bin/activate
playwright --version
# Should show version

# 5. Check cron job
crontab -l
# Should show your scheduled job

# 6. Check directory structure
ls -la ~/ai-job-applier/
# Should see all files

# 7. Check logs
tail -f ~/ai-job-applier/cron.log
# Should show recent activity

# 8. Check applications
ls ~/ai-job-applier/AI_Employee_Vault/Jobs/Applied/
# Should show applied jobs (if any)
```

---

## ✅ DEPLOYMENT COMPLETE!

### What You Have Now:

✅ **EC2 Instance Running 24/7**
✅ **Job Auto-Applier Installed**
✅ **Cron Job (runs every 4 hours)**
✅ **Logs & Monitoring**
✅ **Elastic IP (permanent address)**
✅ **CloudWatch Alarms**

### Next Steps:

1. **Test First Run:**
   ```bash
   cd ~/ai-job-applier
   source venv/bin/activate
   python linkedin_job_applier.py --max-jobs 10
   ```

2. **Monitor Logs:**
   ```bash
   tail -f cron.log
   ```

3. **Check Applications:**
   ```bash
   ls -la AI_Employee_Vault/Jobs/Applied/
   ```

4. **Setup WhatsApp (Next Section)**

---

##  Troubleshooting

### Can't Connect via SSH

```bash
# Check security group
# EC2 → Security Groups → Inbound rules → Allow SSH (port 22)

# Check key permissions (Windows PowerShell)
icacls ai-job-applier-key.pem /grant YourUsername:F

# Try verbose SSH
ssh -vvv -i "key.pem" ubuntu@YOUR_IP
```

### Python Not Found

```bash
# Install Python
sudo apt update
sudo apt install -y python3 python3-pip
```

### Playwright Installation Fails

```bash
# Install dependencies
sudo apt install -y libgbm1 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2

# Reinstall Chromium
playwright install chromium
```

### Cron Job Not Running

```bash
# Check cron service
sudo service cron status

# View cron logs
grep CRON /var/log/syslog

# Test manually
./run_job_applier.sh
```

---

## 📞 Support

**AWS Free Tier Limits:**
- 750 hours/month of t2.micro
- 12 months free
- Monitor usage: AWS Console → Billing → Bills

**Cost Control:**
- Setup billing alarm: $1 limit
- Monitor daily: AWS Console → Billing

**Need Help?**
- AWS Documentation: https://docs.aws.amazon.com/ec2/
- AWS Free Tier: https://aws.amazon.com/free/

---

**DEPLOYMENT COMPLETE! READY FOR WHATSAPP SETUP!** 
