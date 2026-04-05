@echo off
REM ============================================================================
REM AWS EC2 DEPLOYMENT HELPER - AI JOB AUTO-APPLIER
REM ============================================================================
REM This script helps you deploy to AWS EC2
REM ============================================================================

echo.
echo ============================================================================
echo  AWS EC2 DEPLOYMENT - AI JOB AUTO-APPLIER
echo ============================================================================
echo.
echo This guide will help you deploy to AWS EC2
echo.
echo STEPS:
echo   1. Create AWS Account (if you don't have)
echo   2. Launch EC2 Instance
echo   3. Connect via SSH
echo   4. Run setup commands
echo   5. Upload files
echo   6. Test deployment
echo.
echo ============================================================================
echo.
pause

REM Open AWS Console in browser
echo Opening AWS Console...
start https://console.aws.amazon.com/ec2/

echo.
echo ============================================================================
echo  STEP 1: CREATE AWS ACCOUNT (If you don't have one)
echo ============================================================================
echo.
echo 1. If you don't have AWS account:
echo    - Go to: https://portal.aws.amazon.com/billing/signup
echo    - Enter email, create password
echo    - Add payment method (for verification only)
echo    - Verify phone number
echo    - Wait for activation email (5-15 minutes)
echo.
echo 2. If you already have AWS account:
echo    - Login to: https://console.aws.amazon.com/
echo.
pause

echo.
echo ============================================================================
echo  STEP 2: LAUNCH EC2 INSTANCE
echo ============================================================================
echo.
echo In AWS Console, follow these steps:
echo.
echo 1. Click "Launch instance" (orange button)
echo.
echo 2. Configure:
echo    Name: ai-job-applier
echo    AMI: Ubuntu Server 22.04 LTS
echo    Instance type: t2.micro (Free Tier)
echo.
echo 3. Key pair:
echo    Click "Create new key pair"
echo    Name: ai-job-applier-key
echo    Download and SAVE the .pem file!
echo.
echo 4. Network settings:
echo    Allow SSH from anywhere (checked)
echo.
echo 5. Storage: 8 GiB (default)
echo.
echo 6. Click "Launch instance"
echo.
echo 7. Wait for "running" status (2-5 minutes)
echo.
echo 8. Note the "Public IP" address
echo.
pause

echo.
echo ============================================================================
echo  STEP 3: CONNECT VIA SSH
echo ============================================================================
echo.
echo 1. Find your downloaded key file:
echo    ai-job-applier-key.pem
echo.
echo 2. Open PowerShell in that folder
echo.
echo 3. Set permissions:
echo    icacls ai-job-applier-key.pem /inheritance:r
echo    icacls ai-job-applier-key.pem /grant %USERNAME%:F
echo.
echo 4. Connect:
echo    ssh -i "ai-job-applier-key.pem" ubuntu@YOUR_EC2_IP
echo.
echo    (Replace YOUR_EC2_IP with the Public IP from AWS Console)
echo.
echo 5. Type "yes" when asked about fingerprint
echo.
echo 6. You should see: ubuntu@ip-xxx-xxx-xxx-xxx:~$
echo.
pause

echo.
echo ============================================================================
echo  STEP 4: RUN SETUP COMMANDS (Copy-Paste to SSH)
echo ============================================================================
echo.
echo Once connected via SSH, run these commands:
echo.
echo --- COPY FROM HERE ---
echo.
echo # Update system
echo sudo apt update && sudo apt upgrade -y
echo.
echo # Install Python
echo sudo apt install -y python3 python3-pip python3-venv
echo.
echo # Install Chromium
echo sudo apt install -y chromium-browser
echo.
echo # Create directory
echo mkdir -p ~/ai-job-applier
echo cd ~/ai-job-applier
echo.
echo # Setup Python environment
echo python3 -m venv venv
echo source venv/bin/activate
echo pip install --upgrade pip
echo.
echo # Install Playwright
echo pip install playwright pyyaml
echo playwright install chromium
echo playwright install-deps chromium
echo.
echo # Create directories
echo mkdir -p AI_Employee_Vault/Jobs/Applied
echo mkdir -p AI_Employee_Vault/Jobs/Saved
echo mkdir -p AI_Employee_Vault/Logs
echo mkdir -p AI_Employee_Vault/.linkedin_jobs_session
echo.
echo --- TO HERE ---
echo.
pause

echo.
echo ============================================================================
echo  STEP 5: UPLOAD FILES
echo ============================================================================
echo.
echo On your laptop (new PowerShell window):
echo.
echo cd "C:\Users\Noman Traders\Documents\GitHub\Personal-AI-Employee-FTEs"
echo.
echo # Upload main script
echo scp -i "ai-job-applier-key.pem" linkedin_job_applier.py ubuntu@YOUR_EC2_IP:~/ai-job-applier/
echo.
echo # Upload profile
echo scp -i "ai-job-applier-key.pem" AI_Employee_Vault\profile.yaml ubuntu@YOUR_EC2_IP:~/ai-job-applier/AI_Employee_Vault/
echo.
echo # Upload resume (if you have)
echo scp -i "ai-job-applier-key.pem" AI_Employee_Vault\resume.pdf ubuntu@YOUR_EC2_IP:~/ai-job-applier/AI_Employee_Vault/
echo.
pause

echo.
echo ============================================================================
echo  STEP 6: TEST DEPLOYMENT
echo ============================================================================
echo.
echo Back in SSH session:
echo.
echo --- COPY FROM HERE ---
echo.
echo # Activate environment
echo cd ~/ai-job-applier
echo source venv/bin/activate
echo.
echo # Test run (5 jobs max)
echo python linkedin_job_applier.py --max-jobs 5
echo.
echo # Check logs
echo cat AI_Employee_Vault/Logs/job_applier_*.log
echo.
echo # Check applications
echo ls AI_Employee_Vault/Jobs/Applied/
echo.
echo --- TO HERE ---
echo.
pause

echo.
echo ============================================================================
echo  STEP 7: SETUP CRON JOB (Auto-Run Every 4 Hours)
echo ============================================================================
echo.
echo In SSH session:
echo.
echo --- COPY FROM HERE ---
echo.
echo # Create runner script
echo cat ^> run_job_applier.sh ^< 'EOF'
echo #!/bin/bash
echo cd /home/ubuntu/ai-job-applier
echo source venv/bin/activate
echo python linkedin_job_applier.py --max-jobs 20 ^>^> /home/ubuntu/ai-job-applier/cron.log 2^>^&1
echo EOF
echo.
echo chmod +x run_job_applier.sh
echo.
echo # Add to crontab
echo crontab -e
echo.
echo # Add this line:
echo 0 */4 * * * /home/ubuntu/ai-job-applier/run_job_applier.sh
echo.
echo # Save (Ctrl+O, Enter) and Exit (Ctrl+X)
echo.
echo # Verify
echo crontab -l
echo.
echo --- TO HERE ---
echo.
pause

echo.
echo ============================================================================
echo  DEPLOYMENT COMPLETE!
echo ============================================================================
echo.
echo Your AI Job Auto-Applier is now running on AWS EC2!
echo.
echo NEXT:
echo   - Monitor: AWS Console → EC2 → Instances
echo   - Logs: tail -f ~/ai-job-applier/cron.log (in SSH)
echo   - Applications: ls ~/ai-job-applier/AI_Employee_Vault/Jobs/Applied/
echo.
echo FOR WHATSAPP NOTIFICATIONS:
echo   - See: whatsapp_cloud_setup.md
echo.
echo ============================================================================
echo.
pause
