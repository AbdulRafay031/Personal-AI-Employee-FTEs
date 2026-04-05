# 🚀 AWS EC2 Deployment Guide - Mumbai Region

**Target:** AI Employee Platinum Tier  
**Region:** Asia Pacific (Mumbai) - `ap-south-1`  
**Instance:** t2.micro (Free Tier Eligible)  
**OS:** Ubuntu 22.04 LTS  
**Estimated Time:** 30-45 minutes

---

## 📋 Deployment Checklist

- [ ] AWS Account created
- [ ] EC2 Instance launched in Mumbai
- [ ] SSH Key downloaded
- [ ] Instance running and accessible
- [ ] Cloud deployment script executed
- [ ] Git vault sync configured
- [ ] Services running and healthy
- [ ] Local machine synced with cloud

---

## Step 1: Create AWS Account (if not done)

**URL:** https://portal.aws.amazon.com/billing/signup

1. Enter email → Continue
2. Create password → Continue
3. Fill contact info
4. Add payment method (credit/debit card for verification)
5. Complete identity verification
6. Select "Basic (Free)" support plan
7. Wait for activation email (5-15 minutes)

---

## Step 2: Launch EC2 Instance in Mumbai

**URL:** https://console.aws.amazon.com/ec2/

### 2.1 Launch Instance

1. Click **"Launch instance"** (orange button)
2. Configure:
   - **Name:** `ai-employee-cloud`
   - **AMI:** Ubuntu Server 22.04 LTS (HVM), SSD Volume Type
   - **Instance type:** t2.micro (Free Tier)
   - **Region:** Asia Pacific (Mumbai) - Select from top-right dropdown

### 2.2 Create Key Pair

1. Click **"Create new key pair"**
2. Name: `ai-employee-key`
3. Type: RSA
4. Click **"Create key pair"**
5. **⚠️ IMPORTANT:** Save `ai-employee-key.pem` to your Downloads folder
6. **You cannot download this file again!**

### 2.3 Configure Network

1. Under "Network settings", click **"Edit"**
2. Check **"Allow SSH traffic from"**
3. Select **"Anywhere"** (0.0.0.0/0)
4. Check **"Allow HTTP traffic from the internet"**
5. Check **"Allow HTTPS traffic from the internet"**

### 2.4 Storage

- Keep default: 8 GiB gp2 (sufficient for free tier)

### 2.5 Launch

1. Click **"Launch instance"**
2. Wait 2-5 minutes for instance to start
3. Copy the **Public IPv4 address** (e.g., `13.235.xx.xx`)

---

## Step 3: Prepare Key and Connect via SSH

### 3.1 Move Key to .ssh Folder (Windows)

Open **PowerShell** and run:

```powershell
# Create .ssh folder if it doesn't exist
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.ssh"

# Move key to .ssh folder
Move-Item "$env:USERPROFILE\Downloads\ai-employee-key.pem" "$env:USERPROFILE\.ssh\ai-employee-key.pem"

# Set correct permissions (CRITICAL - SSH will refuse to work without this)
icacls "$env:USERPROFILE\.ssh\ai-employee-key.pem" /reset
icacls "$env:USERPROFILE\.ssh\ai-employee-key.pem" /inheritance:r
icacls "$env:USERPROFILE\.ssh\ai-employee-key.pem" /grant:r "$env:USERNAME:R"
```

### 3.2 Connect via SSH

Replace `YOUR_PUBLIC_IP` with your EC2 instance's public IP:

```powershell
ssh -i "$env:USERPROFILE\.ssh\ai-employee-key.pem" ubuntu@YOUR_PUBLIC_IP
```

**First time connection:**
- Type `yes` when asked about fingerprint
- You should see: `Welcome to Ubuntu 22.04.x LTS`

---

## Step 4: Deploy AI Employee to Cloud

Once connected via SSH, run these commands on the remote server:

### 4.1 Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 4.2 Install Git and Clone Repository

```bash
# Install git
sudo apt install -y git

# Clone your repository (replace with your actual repo URL)
git clone https://github.com/YOUR_USERNAME/Personal-AI-Employee-FTEs.git
cd Personal-AI-Employee-FTEs
```

### 4.3 Run Deployment Script

```bash
# Make script executable
chmod +x deploy_platinum_cloud.sh

# Run deployment (requires sudo)
sudo bash deploy_platinum_cloud.sh
```

### 4.4 Follow Interactive Prompts

The script will ask you:

1. **GitHub repository URL:** Enter your repo URL
2. **Git remote URL for vault sync:** Enter your vault sync repo URL (or press Enter to skip)
3. **Expose Odoo port (8069) to your IP?:** Type `y` and enter your local IP
4. **View Platinum tier setup instructions?:** Type `n` (you already have the docs)

---

## Step 5: Configure Credentials

After deployment completes:

```bash
# Edit .env file with your credentials
nano .env

# Add your actual credentials:
# OPENROUTER_API_KEY=your_key_here
# GMAIL_CLIENT_ID=your_client_id
# GMAIL_CLIENT_SECRET=your_client_secret
# etc.

# Save and exit: Ctrl+X, Y, Enter
```

---

## Step 6: Authenticate Services

### 6.1 Gmail Authentication

```bash
# Run Gmail watcher auth
python3 watchers/gmail_watcher.py --auth

# Follow the browser URL instructions
# Authorize the application
# Save the credentials file when prompted
```

### 6.2 WhatsApp Authentication

```bash
# Run WhatsApp watcher auth
python3 watchers/whatsapp_watcher.py --auth

# Scan QR code with your WhatsApp mobile app
# Session will be saved locally
```

---

## Step 7: Verify Deployment

### 7.1 Check Services

```bash
# Check all services
sudo systemctl status ai-employee-*

# You should see:
# ● ai-employee-gmail.service - AI Employee - Gmail Watcher
# ● ai-employee-whatsapp.service - AI Employee - WhatsApp Watcher
# ● ai-employee-orchestrator.service - AI Employee - Orchestrator
# ● ai-employee-health.service - AI Employee - Health Monitor
```

### 7.2 Check Logs

```bash
# View orchestrator logs
sudo journalctl -u ai-employee-orchestrator -f --no-pager

# View health monitor logs
sudo journalctl -u ai-employee-health -f --no-pager
```

### 7.3 Check Vault

```bash
# Check vault structure
ls -la ~/ai-employee/vault/

# Check for new tasks
ls -la ~/ai-employee/vault/Needs_Action/
```

---

## Step 8: Setup Git Vault Sync (Cloud → Local)

### 8.1 On Cloud VM

```bash
cd ~/ai-employee/vault

# Initialize git (if not done by script)
git init

# Add remote (create a private GitHub repo first)
git remote add origin https://github.com/YOUR_USERNAME/vault-sync.git

# Initial commit
git add -A
git commit -m "Initial cloud vault setup"
git push -u origin main

# Setup automated sync (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * cd ~/ai-employee/vault && git pull origin main && git add -A && git commit -m 'Auto-sync (cloud)' && git push origin main") | crontab -
```

### 8.2 On Local Machine (Windows)

Open **PowerShell** on your local machine:

```powershell
# Navigate to vault
cd "C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs\AI_Employee_Vault"

# Initialize git
git init

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/vault-sync.git

# Pull from cloud
git pull origin main --allow-unrelated-histories

# Setup automated sync
schtasks /create /tn "AI-Employee-Vault-Sync" /tr "git -C \"C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs\AI_Employee_Vault\" pull origin main && git -C \"C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs\AI_Employee_Vault\" add -A && git -C \"C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs\AI_Employee_Vault\" commit -m \"Auto-sync (local)\" && git -C \"C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs\AI_Employee_Vault\" push origin main" /sc minute /mo 5
```

---

## Step 9: Test Cloud Deployment

### 9.1 Send Test Email

Send an email to your monitored Gmail account and wait 2-3 minutes.

### 9.2 Check Cloud Vault

```bash
# On cloud VM
ls -la ~/ai-employee/vault/Needs_Action/
cat ~/ai-employee/vault/Needs_Action/EMAIL_*.md
```

### 9.3 Check Local Vault

After 5 minutes (sync interval):

```powershell
# On local machine
dir "C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs\AI_Employee_Vault\Needs_Action\"
```

You should see the same email action file synced from cloud!

---

## 🔧 Useful Commands

### Service Management

```bash
# Check status
sudo systemctl status ai-employee-gmail
sudo systemctl status ai-employee-whatsapp
sudo systemctl status ai-employee-orchestrator
sudo systemctl status ai-employee-health

# Restart all
sudo systemctl restart ai-employee-*

# Stop all
sudo systemctl stop ai-employee-*

# Start all
sudo systemctl start ai-employee-*

# View logs
sudo journalctl -u ai-employee-orchestrator -n 100 --no-pager
```

### Vault Sync

```bash
# Manual sync
cd ~/ai-employee/vault
git pull origin main
git add -A
git commit -m "Manual sync"
git push origin main

# Check sync status
git status
git log -n 5
```

### Monitoring

```bash
# Check system resources
htop

# Check disk usage
df -h

# Check vault size
du -sh ~/ai-employee/vault/

# View health dashboard
cat ~/ai-employee/vault/System_Health.md
```

---

## 🚨 Troubleshooting

### SSH Connection Refused

```powershell
# Check security group allows SSH
# Go to EC2 Console → Security Groups → Inbound Rules
# Ensure port 22 is open to 0.0.0.0/0

# Check instance is running
# EC2 Console → Instances → Instance State should be "running"
```

### Services Not Starting

```bash
# Check logs for errors
sudo journalctl -u ai-employee-orchestrator -n 50 --no-pager

# Check .env file exists
cat ~/ai-employee/Personal-AI-Employee-FTEs/.env

# Restart specific service
sudo systemctl restart ai-employee-orchestrator
```

### Git Sync Not Working

```bash
# Check git status
cd ~/ai-employee/vault
git status
git remote -v

# Test push/pull
git pull origin main
git push origin main

# Check cron job
crontab -l
```

---

## ✅ Deployment Complete Checklist

- [ ] AWS EC2 instance running in Mumbai
- [ ] SSH access working
- [ ] Deployment script executed successfully
- [ ] All 4 services running (gmail, whatsapp, orchestrator, health)
- [ ] Credentials configured in .env
- [ ] Gmail authentication complete
- [ ] WhatsApp authentication complete (if needed)
- [ ] Git vault sync configured (cloud → local)
- [ ] Automated sync cron jobs running
- [ ] Test email detected and action file created
- [ ] Action file synced to local machine
- [ ] Health dashboard generated

---

## 📊 Next Steps After Deployment

1. **Monitor for 24 hours** - Ensure services stay running
2. **Check CEO Briefing** - Will auto-generate next Monday at 7 AM
3. **Review audit logs** - Check `Logs/` folder for activity
4. **Configure Odoo** (optional) - Deploy Odoo for accounting integration
5. **Setup domain + HTTPS** (optional) - For secure Odoo access

---

## 🎯 You're Now Running Platinum Tier!

**Cloud (24/7):**
- ✅ Gmail monitoring
- ✅ Email draft creation
- ✅ Social media monitoring
- ✅ Job application monitoring

**Local (When Online):**
- ✅ WhatsApp monitoring
- ✅ Payment processing
- ✅ HITL approvals
- ✅ Final send/post actions

**Synced via Git:**
- ✅ Task files
- ✅ Approval requests
- ✅ Accounting logs
- ✅ CEO briefings
- ✅ Health status

---

*Ready to deploy! Follow the steps above to get your AI Employee running in the cloud.*
