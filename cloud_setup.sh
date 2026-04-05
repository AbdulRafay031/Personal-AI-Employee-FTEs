#!/bin/bash
# ============================================================================
# CLOUD SERVER SETUP SCRIPT
# For: AI Job Auto-Applier Phase 2
# Run on: AWS EC2 / Google Cloud / Oracle Cloud
# ============================================================================

echo "============================================================================"
echo "  AI JOB AUTO-APPLIER - CLOUD SERVER SETUP"
echo "============================================================================"
echo ""
echo "This script will:"
echo "  1. Update system packages"
echo "  2. Install Python 3"
echo "  3. Install Playwright & dependencies"
echo "  4. Setup virtual environment"
echo "  5. Install job applier"
echo "  6. Setup cron job (auto-run)"
echo "  7. Setup logging"
echo ""
echo "Starting setup..."
echo ""

# Step 1: Update system
echo "[1/7] Updating system packages..."
sudo apt update && sudo apt upgrade -y
echo "✓ System updated"
echo ""

# Step 2: Install Python
echo "[2/7] Installing Python 3..."
sudo apt install -y python3 python3-pip python3-venv
python3 --version
echo "✓ Python installed"
echo ""

# Step 3: Install Playwright dependencies
echo "[3/7] Installing Playwright dependencies..."
sudo apt install -y chromium-browser
echo "✓ Chromium installed"
echo ""

# Step 4: Create application directory
echo "[4/7] Setting up application directory..."
mkdir -p ~/ai-job-applier
cd ~/ai-job-applier

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install playwright pyyaml
playwright install chromium

echo "✓ Playwright installed"
echo ""

# Step 5: Create directory structure
echo "[5/7] Creating directory structure..."
mkdir -p AI_Employee_Vault/Jobs/Applied
mkdir -p AI_Employee_Vault/Jobs/Saved
mkdir -p AI_Employee_Vault/Logs
mkdir -p AI_Employee_Vault/.linkedin_jobs_session

echo "✓ Directory structure created"
echo ""

# Step 6: Create sample profile
echo "[6/7] Creating sample profile..."
cat > AI_Employee_Vault/profile.yaml << 'EOF'
# AI Job Applier Profile
full_name: "Your Name"
email: "your.email@gmail.com"
phone: "+92 300 1234567"

titles:
  - "Frontend Developer"
  - "AI Developer"
  - "MERN Stack Developer"

locations:
  - "Karachi, Pakistan"
  - "Remote"

search_keywords:
  - "Frontend Developer Internship"
  - "AI Developer"
  - "MERN Stack"

exclude_unpaid: true
max_applications_per_day: 20
EOF

echo "✓ Profile created (edit AI_Employee_Vault/profile.yaml)"
echo ""

# Step 7: Setup cron job
echo "[7/7] Setting up cron job..."

# Create cron script
cat > run_job_applier.sh << 'EOF'
#!/bin/bash
cd /home/ubuntu/ai-job-applier
source venv/bin/activate
python linkedin_job_applier.py --max-jobs 20 >> /home/ubuntu/ai-job-applier/cron.log 2>&1
EOF

chmod +x run_job_applier.sh

# Add to crontab (runs every 4 hours)
(crontab -l 2>/dev/null; echo "0 */4 * * * /home/ubuntu/ai-job-applier/run_job_applier.sh") | crontab -

echo "✓ Cron job setup (runs every 4 hours)"
echo ""

# Final setup
echo "============================================================================"
echo "  SETUP COMPLETE!"
echo "============================================================================"
echo ""
echo "Next steps:"
echo "  1. Upload linkedin_job_applier.py to ~/ai-job-applier/"
echo "  2. Edit AI_Employee_Vault/profile.yaml with your details"
echo "  3. Test run: python linkedin_job_applier.py --max-jobs 5"
echo "  4. Check cron: crontab -l"
echo "  5. View logs: tail -f cron.log"
echo ""
echo "Directory: ~/ai-job-applier"
echo "Logs: ~/ai-job-applier/cron.log"
echo "Applications: ~/ai-job-applier/AI_Employee_Vault/Jobs/Applied/"
echo ""
echo "============================================================================"
