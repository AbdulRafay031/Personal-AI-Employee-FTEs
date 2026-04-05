# Platinum Tier Implementation Guide

**Estimated Time:** 60+ hours  
**Prerequisites:** All Gold tier requirements complete

This guide walks you through implementing the Platinum tier: Always-On Cloud + Local Executive architecture for your AI Employee.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites Checklist](#prerequisites-checklist)
3. [Step 1: Cloud VM Deployment](#step-1-cloud-vm-deployment)
4. [Step 2: Cloud/Local Split Architecture](#step-2-cloudlocal-split-architecture)
5. [Step 3: Vault Sync System](#step-3-vault-sync-system)
6. [Step 4: Claim-by-Move Rule Implementation](#step-4-claim-by-move-rule-implementation)
7. [Step 5: Odoo Community Deployment](#step-5-odoo-community-deployment)
8. [Step 6: Health Monitoring & Auto-Restart](#step-6-health-monitoring--auto-restart)
9. [Step 7: Security Hardening](#step-7-security-hardening)
10. [Step 8: Audit Logging & Compliance](#step-8-audit-logging--compliance)
11. [Step 9: End-to-End Testing](#step-9-end-to-end-testing)
12. [Step 10: Production Deployment](#step-10-production-deployment)
13. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The Platinum tier implements a **Cloud/Local split architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                        CLOUD VM (24/7)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Domain Ownership:                                    │  │
│  │  - Email triage & draft replies                      │  │
│  │  - Social post drafts & scheduling                   │  │
│  │  - LinkedIn job monitoring                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕ Git Sync                         │
└─────────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────────┐
│                    LOCAL MACHINE                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Domain Ownership:                                    │  │
│  │  - Approvals (HITL)                                  │  │
│  │  - WhatsApp session                                  │  │
│  │  - Payments/banking                                  │  │
│  │  - Final "send/post" actions                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Principles:

1. **Cloud drafts, Local approves**: Cloud can create draft emails/posts but cannot send them
2. **Secrets never sync**: Credentials, sessions, tokens stay local
3. **Single-writer rule**: Only Local writes to `Dashboard.md`
4. **Claim-by-move**: First agent to claim a task owns it
5. **Git-based sync**: Vault syncs via Git (Phase 1)

---

## Prerequisites Checklist

Before starting Platinum tier implementation:

- [ ] Bronze tier complete (watchers, vault, basic orchestration)
- [ ] Silver tier complete (HITL, MCP servers, LinkedIn automation)
- [ ] Gold tier complete (Ralph Wiggum loop, CEO briefings, finance watcher)
- [ ] Cloud VM provisioned (AWS EC2, Oracle Cloud, or GCP)
- [ ] Domain name configured (optional, for HTTPS)
- [ ] Git repository created for vault sync
- [ ] Odoo Community edition downloaded (for accounting integration)

---

## Step 1: Cloud VM Deployment

### 1.1 Choose Your Cloud Provider

**Recommended Options:**

| Provider | Free Tier | Specs | Best For |
|----------|-----------|-------|----------|
| Oracle Cloud | Always Free | 4 ARM cores, 24GB RAM | Best free tier |
| AWS EC2 | 12 months free | 1 vCPU, 1GB RAM (t2.micro) | AWS ecosystem |
| GCP | 12 months free | 1 vCPU, 0.6GB RAM (e2-micro) | Google integration |
| Azure | 12 months free | 1 vCPU, 1GB RAM (B1s) | Microsoft ecosystem |

### 1.2 Deploy Cloud VM

**Quick Start (AWS EC2):**

```bash
# Use the provided deployment script
DEPLOY_TO_AWS.bat

# Or manually via AWS CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=AI-Employee-Cloud}]'
```

**Quick Start (Oracle Cloud):**

```bash
# Use Oracle Cloud web console or CLI
# Select "Always Free" ARM instance
# Ubuntu 22.04 LTS recommended
```

### 1.3 Initial Server Setup

SSH into your VM and run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.13 python3-pip git curl wget

# Install Node.js (for MCP servers)
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt install -y nodejs

# Install Playwright
pip3 install playwright
python3 -m playwright install --with-deps chromium

# Create directory structure
mkdir -p ~/ai-employee/{vault,logs,config,sessions}
```

### 1.4 Deploy Cloud Setup Script

Copy and run the cloud setup script:

```bash
# From your local machine
scp cloud_setup.sh ubuntu@YOUR_VM_IP:~/
ssh ubuntu@YOUR_VM_IP "bash ~/cloud_setup.sh"
```

---

## Step 2: Cloud/Local Split Architecture

### 2.1 Initialize Cloud Instance

On the cloud VM:

```bash
# Clone your repository
cd ~/ai-employee
git clone https://github.com/YOUR_USERNAME/Personal-AI-Employee-FTEs.git

# Initialize cloud instance
python3 cloud_local_split.py \
  --vault-path ~/ai-employee/vault \
  --instance-type cloud \
  --agent-id cloud-agent-001 \
  --init-git
```

### 2.2 Initialize Local Instance

On your local machine:

```bash
# Initialize local instance
python cloud_local_split.py ^
  --vault-path C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs\AI_Employee_Vault ^
  --instance-type local ^
  --agent-id local-agent-001 ^
  --git-remote https://github.com/YOUR_USERNAME/vault-sync.git
```

### 2.3 Configure Domain Ownership

Edit `cloud_local_split.py` to customize domain ownership:

```python
# Cloud domains (draft-only)
self.cloud_domains = ["email", "social_media", "linkedin", "twitter"]

# Local domains (execution)
self.local_domains = ["whatsapp", "payments", "banking", "approvals", "final_send"]
```

### 2.4 Test Cloud/Local Communication

**Test 1: Cloud creates draft**

```bash
# On cloud VM
python3 cloud_local_split.py \
  --vault-path ~/ai-employee/vault \
  --instance-type cloud \
  --agent-id cloud-agent-001 \
  --create-draft \
  --action-type draft_email \
  --action-data '{"to":"client@example.com","subject":"Test","body":"Draft test"}'
```

**Test 2: Local sees draft**

```bash
# On local machine
python cloud_local_split.py ^
  --vault-path AI_Employee_Vault ^
  --instance-type local ^
  --agent-id local-agent-001 ^
  --sync
```

You should see the draft in `Pending_Approval/` folder.

---

## Step 3: Vault Sync System

### 3.1 Create Git Repository for Vault Sync

**Option A: GitHub Private Repository (Recommended)**

```bash
# Create a new private repository on GitHub
# Then initialize vault sync

cd AI_Employee_Vault
git init
git remote add origin https://github.com/YOUR_USERNAME/vault-sync.git

# Create .gitignore (CRITICAL - secrets never sync)
cat > .gitignore << 'EOF'
# Secrets - NEVER sync these
.env
*.key
*.pem
credentials/
secrets/

# Session files
.whatsapp_session/
.linkedin_session/
.linkedin_jobs_session/

# OS files
.DS_Store
Thumbs.db

# Python cache
__pycache__/
*.pyc
EOF

git add .
git commit -m "Initial vault setup (local)"
git push -u origin main
```

### 3.2 Configure Cloud Git Sync

On cloud VM:

```bash
cd ~/ai-employee/vault
git init
git remote add origin https://github.com/YOUR_USERNAME/vault-sync.git

# Configure Git
git config user.email "ai-employee-cloud@local"
git config user.name "AI Employee (Cloud)"

# Pull from remote
git pull origin main

# Set up automated sync
crontab -e

# Add this line (sync every 5 minutes)
*/5 * * * * cd ~/ai-employee/vault && git pull origin main && git add -A && git commit -m "Auto-sync (cloud)" && git push origin main
```

### 3.3 Configure Local Git Sync

On Windows (using Task Scheduler):

```bash
# Create scheduled task (runs every 5 minutes)
schtasks /create /tn "AI-Employee-Vault-Sync" /tr "git -C \"C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs\AI_Employee_Vault\" pull origin main && git -C \"C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs\AI_Employee_Vault\" add -A && git -C \"C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs\AI_Employee_Vault\" commit -m \"Auto-sync (local)\" && git -C \"C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs\AI_Employee_Vault\" push origin main" /sc minute /mo 5
```

### 3.4 Sync Rules

**What Syncs:**
- ✅ Markdown files (`.md`)
- ✅ Task files (`Needs_Action/`, `Done/`, `Plans/`)
- ✅ Approval files (`Pending_Approval/`, `Approved/`)
- ✅ Briefings and accounting logs
- ✅ Updates and signals

**What NEVER Syncs:**
- ❌ `.env` files
- ❌ Credentials and tokens
- ❌ Session files (`.whatsapp_session/`, etc.)
- ❌ Banking information
- ❌ Payment tokens

---

## Step 4: Claim-by-Move Rule Implementation

### 4.1 How Claim-by-Move Works

The claim-by-move rule prevents duplicate work in multi-agent scenarios:

1. Task file appears in `Needs_Action/`
2. First agent to move it to `In_Progress/<agent_id>/` owns it
3. Other agents must ignore claimed tasks
4. Agent can release task back to `Needs_Action/` if unable to complete

### 4.2 Implementation

Already implemented in `cloud_local_split.py`:

```python
from cloud_local_split import ClaimByMoveRule

# Initialize
claim_rule = ClaimByMoveRule(
    vault_path="/path/to/vault",
    agent_id="cloud-agent-001"
)

# Get available tasks
available = claim_rule.get_available_tasks()

# Claim a task
for task_file in available:
    if claim_rule.claim_task(task_file):
        print(f"Successfully claimed {task_file.name}")
        # Process task...
        break
```

### 4.3 Testing Claim-by-Move

**Test 1: Single agent claims task**

```bash
# Create test task
cat > AI_Employee_Vault/Needs_Action/TEST_task_001.md << 'EOF'
---
type: test
created: 2026-04-04T10:00:00Z
---

# Test Task

This is a test task for claim-by-move.
EOF

# Claim task
python cloud_local_split.py \
  --vault-path AI_Employee_Vault \
  --instance-type local \
  --agent-id local-agent-001 \
  --claim-task TEST_task_001.md

# Verify task moved to In_Progress/local-agent-001/
ls AI_Employee_Vault/In_Progress/local-agent-001/
```

**Test 2: Second agent cannot claim same task**

```bash
# Try to claim with different agent (should fail)
python cloud_local_split.py \
  --vault-path AI_Employee_Vault \
  --instance-type cloud \
  --agent-id cloud-agent-001 \
  --claim-task TEST_task_001.md

# Should output: "Task already claimed by local-agent-001"
```

---

## Step 5: Odoo Community Deployment

### 5.1 Deploy Odoo on Cloud VM

**Option A: Docker Deployment (Recommended)**

```bash
# On cloud VM
sudo apt install -y docker.io docker-compose

# Create docker-compose.yml
cat > ~/odoo/docker-compose.yml << 'EOF'
version: '3.8'

services:
  web:
    image: odoo:17.0
    depends_on:
      - db
    ports:
      - "8069:8069"
      - "8072:8072"
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons:/mnt/extra-addons

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data

volumes:
  odoo-web-data:
  odoo-db-data:
EOF

# Start Odoo
cd ~/odoo
docker-compose up -d

# Access at: http://YOUR_VM_IP:8069
```

**Option B: Direct Installation**

```bash
# Install Odoo 17
sudo apt install -y odoo

# Start and enable
sudo systemctl start odoo
sudo systemctl enable odoo

# Access at: http://YOUR_VM_IP:8069
```

### 5.2 Configure Odoo

1. **Initial Setup:**
   - Navigate to `http://YOUR_VM_IP:8069`
   - Create database: `ai_employee`
   - Set master password (save in `.env`!)
   - Install modules: Accounting, Invoicing, CRM

2. **Create API User:**
   - Settings → Users & Companies → Users
   - Create user: `api_user`
   - Set strong password
   - Grant accounting permissions

3. **Configure Accounting:**
   - Set up chart of accounts
   - Configure tax rules
   - Set up bank accounts (placeholder for testing)

### 5.3 Create Odoo MCP Server

```bash
# Install Odoo MCP server
pip3 install odoo-mcp

# Or use existing implementation
# https://github.com/AlanOgic/mcp-odoo-adv

# Configure MCP server
cat > ~/ai-employee/config/odoo_mcp_config.json << 'EOF'
{
  "odoo_url": "http://localhost:8069",
  "odoo_db": "ai_employee",
  "odoo_user": "api_user",
  "odoo_password": "${ODOO_API_PASSWORD}"
}
EOF

# Start Odoo MCP server
python3 -m odoo_mcp \
  --config ~/ai-employee/config/odoo_mcp_config.json \
  --port 8810
```

### 5.4 Integrate Odoo MCP with AI Employee

Add to your orchestrator:

```python
from odoo_mcp_client import OdooMCPClient

class Orchestrator:
    def __init__(self):
        self.odoo_client = OdooMCPClient(
            url="http://localhost:8810",
            db="ai_employee",
            user="api_user",
            password=os.getenv("ODOO_API_PASSWORD")
        )
    
    def create_invoice(self, client_email, amount, description):
        """Create invoice in Odoo (draft-only, requires approval)"""
        invoice = self.odoo_client.create_invoice(
            partner_email=client_email,
            amount=amount,
            description=description,
            status="draft"  # Draft-only!
        )
        
        # Create approval request
        self.approval_workflow.create_request(
            action_type="invoice_create",
            data=invoice,
            requires_approval=True
        )
```

---

## Step 6: Health Monitoring & Auto-Restart

### 6.1 Deploy Health Monitor

Already implemented in `health_monitor.py`. Deploy it:

**On Cloud VM:**

```bash
# Start health monitor
python3 health_monitor.py \
  --vault-path ~/ai-employee/vault \
  --start-all

# Or run as systemd service
sudo cat > /etc/systemd/system/ai-employee-health.service << 'EOF'
[Unit]
Description=AI Employee Health Monitor
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-employee
ExecStart=/usr/bin/python3 health_monitor.py --vault-path ~/ai-employee/vault
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start ai-employee-health
sudo systemctl enable ai-employee-health
```

**On Local (Windows):**

```bash
# Start health monitor
python health_monitor.py ^
  --vault-path AI_Employee_Vault ^
  --start-all

# Or run as Windows service (use NSSM)
nssm install AI-Employee-Health "python" "health_monitor.py --vault-path AI_Employee_Vault"
nssm start AI-Employee-Health
```

### 6.2 Configure Health Checks

Edit `health_monitor.py` to customize thresholds:

```python
config = {
    "disk_warning_threshold": 80,      # Warn at 80% disk usage
    "disk_critical_threshold": 95,     # Critical at 95%
    "memory_warning_threshold": 85,    # Warn at 85% memory
    "max_process_restarts": 5,         # Max restart attempts
    "check_interval": 60               # Check every 60 seconds
}
```

### 6.3 Monitor Health Dashboard

Health dashboard auto-generates at `System_Health.md`:

```markdown
# System Health Dashboard

## Overall Status: HEALTHY

## System Resources
| Metric | Value | Status |
|--------|-------|--------|
| Disk Usage | 45.2% | ✅ |
| Disk Free | 125.3 GB | ✅ |
| Memory Usage | 62.1% | ✅ |
| CPU Usage | 15.3% | ✅ |

## Processes
| Process | Status | PID | Uptime |
|---------|--------|-----|--------|
| gmail_watcher | ✅ running | 12345 | 2 days |
| whatsapp_watcher | ✅ running | 12346 | 2 days |
| orchestrator | ✅ running | 12347 | 2 days |
```

---

## Step 7: Security Hardening

### 7.1 Credential Management

**NEVER store credentials in code or vault:**

```bash
# Use environment variables
export GMAIL_CLIENT_ID="your_client_id"
export GMAIL_CLIENT_SECRET="your_client_secret"
export ODOO_API_PASSWORD="your_odoo_password"

# Or use .env file (NEVER commit!)
cat > .env << 'EOF'
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
ODOO_API_PASSWORD=your_odoo_password
WHATSAPP_SESSION_PATH=/secure/path/session
EOF

# Add to .gitignore
echo ".env" >> .gitignore
```

### 7.2 Firewall Configuration

**Cloud VM:**

```bash
# Configure UFW firewall
sudo apt install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS (if using reverse proxy)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Odoo (restrict to your IP)
sudo ufw allow from YOUR_IP to any port 8069

# Enable firewall
sudo ufw enable
```

### 7.3 HTTPS Setup (Optional but Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (requires domain name)
sudo certbot certonly --standalone -d your-domain.com

# Configure Nginx reverse proxy
sudo cat > /etc/nginx/sites-available/odoo << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### 7.4 Regular Security Audits

```bash
# Check for outdated packages
pip3 list --outdated
npm outdated

# Update regularly
sudo apt update && sudo apt upgrade -y
pip3 install --upgrade -r requirements.txt
npm update
```

---

## Step 8: Audit Logging & Compliance

### 8.1 Audit Logger Deployment

Already implemented in `audit_logger.py`. Usage:

```python
from audit_logger import AuditLogger

logger = AuditLogger(vault_path="/path/to/vault")

# Log an action
logger.log_action(
    action_type="email_send",
    actor="claude_code",
    target="client@example.com",
    parameters={"subject": "Invoice #123"},
    approval_status="approved",
    approved_by="human",
    result="success"
)
```

### 8.2 Generate Compliance Reports

```bash
# Generate weekly compliance report
python audit_logger.py \
  --vault-path AI_Employee_Vault \
  --compliance-report \
  --days 90

# Output: Logs/compliance_report_20260404.md
```

### 8.3 Search Audit Logs

```bash
# Search for failed actions
python audit_logger.py \
  --vault-path AI_Employee_Vault \
  --search "failed" \
  --result failed \
  --days 30

# Search by actor
python audit_logger.py \
  --vault-path AI_Employee_Vault \
  --search "gmail_watcher" \
  --actor gmail_watcher
```

### 8.4 Automatic Log Cleanup

```bash
# Clean up logs older than 90 days
python audit_logger.py \
  --vault-path AI_Employee_Vault \
  --cleanup
```

---

## Step 9: End-to-End Testing

### 9.1 Platinum Demo Test Plan

**Test Scenario: Email arrives while Local is offline**

1. **Setup:**
   - Stop local AI Employee
   - Ensure cloud instance is running
   - Have test email account ready

2. **Execute:**
   ```bash
   # Send test email to monitored Gmail account
   # Wait 2-3 minutes for Gmail watcher to detect
   ```

3. **Verify Cloud Actions:**
   ```bash
   # Check cloud vault
   ls ~/ai-employee/vault/Needs_Action/
   # Should see: EMAIL_<id>.md

   # Check cloud created draft reply
   ls ~/ai-employee/vault/Pending_Approval/
   # Should see: DRAFT_draft_email_<timestamp>.md
   ```

4. **Bring Local Online:**
   ```bash
   # Start local AI Employee
   python start_ai_employee.bat

   # Wait for sync
   # Check local vault
   dir AI_Employee_Vault\Pending_Approval\
   # Should see cloud's draft
   ```

5. **User Approves:**
   ```bash
   # Move file from Pending_Approval to Approved
   move AI_Employee_Vault\Pending_Approval\DRAFT_* AI_Employee_Vault\Approved\

   # Wait for execution
   # Check Logs/ for email_send entry
   ```

6. **Verify Completion:**
   ```bash
   # Check Dashboard.md
   # Should show: "Email sent to <recipient>"

   # Check audit log
   python audit_logger.py --vault-path AI_Employee_Vault --search "email_send"
   ```

### 9.2 Test Automation

Run automated tests:

```bash
# Run Platinum tier test suite
python test_platinum_tier.py --vault-path AI_Employee_Vault

# Expected output:
# ✅ Cloud/Local split: PASS
# ✅ Vault sync: PASS
# ✅ Claim-by-move: PASS
# ✅ Draft creation: PASS
# ✅ Approval workflow: PASS
# ✅ Audit logging: PASS
```

---

## Step 10: Production Deployment

### 10.1 Cloud VM Production Checklist

- [ ] All watchers running (Gmail, WhatsApp, Finance, Filesystem)
- [ ] Orchestrator running with Ralph Wiggum loop
- [ ] Health monitor active with auto-restart
- [ ] Git sync configured (every 5 minutes)
- [ ] Odoo MCP server running
- [ ] Firewall configured
- [ ] HTTPS enabled (if using domain)
- [ ] Monitoring alerts configured (WhatsApp/email notifications)
- [ ] Backup strategy implemented
- [ ] Documentation updated

### 10.2 Local Machine Production Checklist

- [ ] All local watchers running
- [ ] HITL approval workflow active
- [ ] WhatsApp session authenticated
- [ ] Payment credentials configured (securely)
- [ ] Git sync configured
- [ ] Health monitor running
- [ ] Audit logging active
- [ ] Daily dashboard review habit established

### 10.3 Monitoring & Maintenance

**Daily:**
- Review Dashboard.md (2 minutes)
- Check Pending_Approval folder
- Verify health status in System_Health.md

**Weekly:**
- Review CEO Briefing (auto-generated Mondays)
- Check audit logs for anomalies
- Review and process pending approvals

**Monthly:**
- Generate compliance report
- Review and rotate credentials if needed
- Update all dependencies
- Review cloud VM costs

**Quarterly:**
- Full security audit
- Penetration testing (optional)
- Review and update Company_Handbook.md
- Backup and disaster recovery test

---

## Troubleshooting

### Cloud/Local Sync Issues

**Problem:** Vault not syncing between cloud and local

**Solution:**
```bash
# Check git status on both ends
git status
git log -n 5

# Force sync
git fetch origin
git reset --hard origin/main

# Check for conflicts
git diff HEAD origin/main

# Verify .gitignore is correct
cat .gitignore
```

### Claim-by-Move Not Working

**Problem:** Multiple agents claiming same task

**Solution:**
```bash
# Check task file for claim marker
cat Needs_Action/TASK_FILE.md
# Should see: claimed_by: <agent_id>

# Reset claim
python cloud_local_split.py --release-task TASK_FILE.md
```

### Health Monitor Not Restarting Processes

**Problem:** Crashed processes not restarting

**Solution:**
```bash
# Check health monitor logs
cat /tmp/ai_employee_health_monitor.log

# Manually restart process
python health_monitor.py --vault-path AI_Employee_Vault --start-all

# Check max restart limit not exceeded
cat System_Health.md
```

### Odoo MCP Connection Failed

**Problem:** Cannot connect to Odoo MCP server

**Solution:**
```bash
# Check Odoo is running
curl http://localhost:8069

# Check MCP server
curl http://localhost:8810/health

# Check credentials
cat config/odoo_mcp_config.json

# Restart MCP server
pkill -f odoo_mcp
python3 -m odoo_mcp --config config/odoo_mcp_config.json
```

---

## Next Steps

After completing Platinum tier:

1. **A2A Upgrade (Phase 2):** Replace file handoffs with direct Agent-to-Agent messages
2. **Multi-Cloud Deployment:** Deploy across multiple cloud providers for redundancy
3. **Advanced Analytics:** Integrate with BI tools for deeper insights
4. **Custom Skills:** Develop domain-specific agent skills
5. **Team Collaboration:** Multi-user support with role-based access

---

## Resources

- **Main Blueprint:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Ralph Wiggum Pattern:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
- **Odoo MCP Server:** https://github.com/AlanOgic/mcp-odoo-adv
- **Agent Skills Documentation:** https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

---

*Platinum Tier Implementation Guide v0.1*  
*Last Updated: 2026-04-04*
