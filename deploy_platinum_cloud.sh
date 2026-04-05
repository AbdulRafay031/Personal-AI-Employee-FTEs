#!/bin/bash
# =====================================================
# Platinum Tier AI Employee - Cloud Deployment Script
# =====================================================
# This script deploys the AI Employee to a cloud VM (Ubuntu/Debian)
# 
# Usage: bash deploy_platinum_cloud.sh
# 
# Prerequisites:
# - Ubuntu 22.04+ or Debian 12+
# - Root or sudo access
# - Internet connection
# =====================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AI_EMPLOYEE_DIR="/home/$SUDO_USER/ai-employee"
VAULT_PATH="$AI_EMPLOYEE_DIR/vault"
LOG_PATH="$AI_EMPLOYEE_DIR/logs"
CONFIG_PATH="$AI_EMPLOYEE_DIR/config"
SESSION_PATH="$AI_EMPLOYEE_DIR/sessions"

echo -e "${BLUE}"
echo "============================================================"
echo "  AI Employee - Platinum Tier Cloud Deployment"
echo "============================================================"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}[ERROR] Please run as root or with sudo${NC}"
    exit 1
fi

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: System Update
echo ""
print_status "Step 1/10: Updating system packages..."
apt update && apt upgrade -y
print_status "System updated successfully"

# Step 2: Install Dependencies
echo ""
print_status "Step 2/10: Installing dependencies..."

# Python 3.13
add-apt-repository -y ppa:deadsnakes/ppa
apt install -y python3.13 python3.13-venv python3.13-dev python3-pip

# Node.js 24
curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
apt install -y nodejs

# Other dependencies
apt install -y git curl wget nginx certbot python3-certbot-nginx \
               postgresql docker.io docker-compose ufw

# Playwright
pip3 install playwright
python3.13 -m playwright install --with-deps chromium

print_status "Dependencies installed successfully"

# Step 3: Create Directory Structure
echo ""
print_status "Step 3/10: Creating directory structure..."

mkdir -p "$AI_EMPLOYEE_DIR"
mkdir -p "$VAULT_PATH"/{Inbox,Needs_Action,In_Progress,Pending_Approval,Approved,Rejected,Done,Plans,Accounting,Briefings,Logs,Jobs,Invoices,Updates,Signals}
mkdir -p "$LOG_PATH"
mkdir -p "$CONFIG_PATH"
mkdir -p "$SESSION_PATH"

# Set permissions
chown -R $SUDO_USER:$SUDO_USER "$AI_EMPLOYEE_DIR"
chmod -R 755 "$AI_EMPLOYEE_DIR"

print_status "Directory structure created"

# Step 4: Clone Repository
echo ""
print_status "Step 4/10: Cloning AI Employee repository..."

cd "$AI_EMPLOYEE_DIR"

# Ask for repository URL
read -p "Enter your GitHub repository URL: " REPO_URL
if [ -z "$REPO_URL" ]; then
    print_warning "No repository URL provided. Skipping clone."
else
    git clone "$REPO_URL" .
    print_status "Repository cloned successfully"
fi

# Step 5: Install Python Dependencies
echo ""
print_status "Step 5/10: Installing Python dependencies..."

cd "$AI_EMPLOYEE_DIR"
pip3 install -r requirements.txt

# Install additional Platinum tier dependencies
pip3 install psutil google-api-python-client google-auth-httplib2 google-auth-oauthlib

print_status "Python dependencies installed"

# Step 6: Configure Environment
echo ""
print_status "Step 6/10: Configuring environment..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning ".env file created from template. Please edit it with your credentials."
        print_warning "DO NOT commit .env to Git!"
    else
        print_warning ".env.example not found. Creating basic .env file."
        cat > .env << 'EOF'
# AI Employee Configuration
# IMPORTANT: Never commit this file to Git!

# OpenRouter (or your LLM provider)
OPENROUTER_API_KEY=your_api_key_here

# Gmail API
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REDIRECT_URI=http://localhost

# WhatsApp (if using Cloud API)
WHATSAPP_CLOUD_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Odoo (if deployed)
ODOO_API_PASSWORD=your_odoo_password

# Vault Path
VAULT_PATH=/home/$(whoami)/ai-employee/vault
EOF
    fi
fi

# Add .env to .gitignore
if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo "*.key" >> .gitignore
    echo "*.pem" >> .gitignore
    echo "credentials/" >> .gitignore
    echo "secrets/" >> .gitignore
    echo ".whatsapp_session/" >> .gitignore
    echo ".linkedin_session/" >> .gitignore
    print_status ".gitignore updated"
fi

# Step 7: Initialize Git Vault Sync
echo ""
print_status "Step 7/10: Initializing Git vault sync..."

cd "$VAULT_PATH"
git init
git config user.email "ai-employee-cloud@local"
git config user.name "AI Employee (Cloud)"

# Create initial commit
git add -A
git commit -m "Initial vault setup (cloud)"

# Ask for remote URL
read -p "Enter Git remote URL for vault sync (or press Enter to skip): " GIT_REMOTE
if [ ! -z "$GIT_REMOTE" ]; then
    git remote add origin "$GIT_REMOTE"
    git push -u origin main
    print_status "Git remote configured: $GIT_REMOTE"
else
    print_warning "Git remote not configured. Vault sync will not work."
fi

# Step 8: Configure Firewall
echo ""
print_status "Step 8/10: Configuring firewall..."

ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Ask if Odoo should be exposed
read -p "Expose Odoo port (8069) to your IP? (y/n): " EXPOSE_ODOO
if [ "$EXPOSE_ODOO" = "y" ]; then
    read -p "Enter your IP address: " YOUR_IP
    ufw allow from "$YOUR_IP" to any port 8069
    print_status "Odoo port exposed to $YOUR_IP"
fi

ufw --force enable
print_status "Firewall configured"

# Step 9: Setup Systemd Services
echo ""
print_status "Step 9/10: Creating systemd services..."

# Gmail Watcher Service
cat > /etc/systemd/system/ai-employee-gmail.service << EOF
[Unit]
Description=AI Employee - Gmail Watcher
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$AI_EMPLOYEE_DIR
EnvironmentFile=$AI_EMPLOYEE_DIR/.env
ExecStart=/usr/bin/python3.13 watchers/gmail_watcher.py --vault-path $VAULT_PATH
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# WhatsApp Watcher Service
cat > /etc/systemd/system/ai-employee-whatsapp.service << EOF
[Unit]
Description=AI Employee - WhatsApp Watcher
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$AI_EMPLOYEE_DIR
EnvironmentFile=$AI_EMPLOYEE_DIR/.env
ExecStart=/usr/bin/python3.13 watchers/whatsapp_watcher.py --vault-path $VAULT_PATH
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

# Orchestrator Service
cat > /etc/systemd/system/ai-employee-orchestrator.service << EOF
[Unit]
Description=AI Employee - Orchestrator
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$AI_EMPLOYEE_DIR
EnvironmentFile=$AI_EMPLOYEE_DIR/.env
ExecStart=/usr/bin/python3.13 orchestrator.py --vault-path $VAULT_PATH
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
EOF

# Health Monitor Service
cat > /etc/systemd/system/ai-employee-health.service << EOF
[Unit]
Description=AI Employee - Health Monitor
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$AI_EMPLOYEE_DIR
EnvironmentFile=$AI_EMPLOYEE_DIR/.env
ExecStart=/usr/bin/python3.13 health_monitor.py --vault-path $VAULT_PATH
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload and enable services
systemctl daemon-reload
systemctl enable ai-employee-gmail
systemctl enable ai-employee-whatsapp
systemctl enable ai-employee-orchestrator
systemctl enable ai-employee-health

print_status "Systemd services created and enabled"

# Step 10: Start Services
echo ""
print_status "Step 10/10: Starting AI Employee services..."

systemctl start ai-employee-gmail
systemctl start ai-employee-whatsapp
systemctl start ai-employee-orchestrator
systemctl start ai-employee-health

print_status "All services started"

# Setup cron for vault sync
print_status "Setting up automated vault sync (cron job)..."

(crontab -l 2>/dev/null; echo "*/5 * * * * cd $VAULT_PATH && git pull origin main && git add -A && git commit -m 'Auto-sync (cloud)' && git push origin main") | crontab -

print_status "Vault sync cron job added (every 5 minutes)"

# Setup cron for CEO briefing (Monday 7 AM)
print_status "Setting up weekly CEO briefing..."

(crontab -l 2>/dev/null; echo "0 7 * * 1 cd $AI_EMPLOYEE_DIR && python3.13 ceo_briefing_generator.py --vault-path $VAULT_PATH") | crontab -

print_status "CEO briefing cron job added (Mondays at 7 AM)"

# Final Status
echo ""
echo -e "${GREEN}"
echo "============================================================"
echo "  AI Employee Cloud Deployment Complete!"
echo "============================================================"
echo -e "${NC}"
echo ""
echo "Services Running:"
systemctl status ai-employee-gmail --no-pager -l | head -5
systemctl status ai-employee-whatsapp --no-pager -l | head -5
systemctl status ai-employee-orchestrator --no-pager -l | head -5
systemctl status ai-employee-health --no-pager -l | head -5
echo ""
echo "Vault Location: $VAULT_PATH"
echo "Logs Location: $LOG_PATH"
echo "Config Location: $CONFIG_PATH"
echo ""
echo "Useful Commands:"
echo "  Check status:    systemctl status ai-employee-*"
echo "  View logs:       journalctl -u ai-employee-orchestrator -f"
echo "  Restart all:     systemctl restart ai-employee-*"
echo "  Stop all:        systemctl stop ai-employee-*"
echo "  Vault sync:      cd $VAULT_PATH && git status"
echo ""
echo "Next Steps:"
echo "  1. Edit .env file with your credentials"
echo "  2. Authenticate Gmail: python3.13 watchers/gmail_watcher.py --auth"
echo "  3. Authenticate WhatsApp: python3.13 watchers/whatsapp_watcher.py --auth"
echo "  4. Configure local machine and setup Git sync"
echo "  5. Test end-to-end flow (see PLATINUM_TIER_IMPLEMENTATION.md)"
echo ""
echo "============================================================"
echo ""

# Offer to open setup instructions
read -p "View Platinum tier setup instructions? (y/n): " VIEW_INSTRUCTIONS
if [ "$VIEW_INSTRUCTIONS" = "y" ]; then
    if [ -f "PLATINUM_TIER_IMPLEMENTATION.md" ]; then
        less PLATINUM_TIER_IMPLEMENTATION.md
    else
        print_warning "PLATINUM_TIER_IMPLEMENTATION.md not found in current directory."
        print_warning "Please check the repository documentation."
    fi
fi

echo ""
echo "Deployment complete! Your AI Employee is now running in the cloud."
echo "Monitor the services regularly and check the vault for new tasks."
