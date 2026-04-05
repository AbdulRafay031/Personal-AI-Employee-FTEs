@echo off
REM ===========================================
REM AI Employee - Setup Verification Script
REM For: Rafay (rafay16031@gmail.com)
REM ===========================================

echo.
echo ========================================
echo   AI Employee - Setup Verification
echo ========================================
echo.

REM Check Python
echo [1/8] Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python not found!
    echo       Please install Python 3.10+ from https://python.org/
    pause
    exit /b 1
)
python --version
echo [OK] Python found
echo.

REM Check pip
echo [2/8] Checking pip...
pip --version > nul 2>&1
if errorlevel 1 (
    echo [FAIL] pip not found!
    echo       Please reinstall Python
    pause
    exit /b 1
)
echo [OK] pip found
echo.

REM Check required packages
echo [3/8] Checking required packages...

set PACKAGES=playwright openai python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib

for %%p in (%PACKAGES%) do (
    pip show %%p > nul 2>&1
    if errorlevel 1 (
        echo [MISSING] %%p not installed
    ) else (
        echo [OK] %%p installed
    )
)
echo.

REM Check Playwright browsers
echo [4/8] Checking Playwright browsers...
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')" > nul 2>&1
if errorlevel 1 (
    echo [FAIL] Playwright not working!
    echo       Run: pip install playwright
    echo       Run: playwright install chromium
    pause
    exit /b 1
)
echo [OK] Playwright working
echo.

REM Check vault structure
echo [5/8] Checking vault structure...
if exist "AI_Employee_Vault" (
    echo [OK] AI_Employee_Vault exists
) else (
    echo [WARN] AI_Employee_Vault not found - will be created on first run
)

if exist "AI_Employee_Vault\Needs_Action" (
    echo [OK] Needs_Action folder exists
) else (
    echo [INFO] Creating Needs_Action folder...
    mkdir "AI_Employee_Vault\Needs_Action"
)

if exist "AI_Employee_Vault\Pending_Approval" (
    echo [OK] Pending_Approval folder exists
) else (
    echo [INFO] Creating Pending_Approval folder...
    mkdir "AI_Employee_Vault\Pending_Approval"
)

if exist "AI_Employee_Vault\Approved" (
    echo [OK] Approved folder exists
) else (
    echo [INFO] Creating Approved folder...
    mkdir "AI_Employee_Vault\Approved"
)

if exist "AI_Employee_Vault\Done" (
    echo [OK] Done folder exists
) else (
    echo [INFO] Creating Done folder...
    mkdir "AI_Employee_Vault\Done"
)
echo.

REM Check .env file
echo [6/8] Checking .env file...
if exist ".env" (
    echo [OK] .env file found
    echo [INFO] Make sure you've filled in:
    echo        - OPENROUTER_API_KEY
    echo        - GMAIL_APP_PASSWORD
    echo        - YOUR_WHATSAPP_NUMBER
) else (
    echo [WARN] .env file not found!
    echo [INFO] Copy .env.example to .env and fill in your details
    echo [INFO] Command: copy .env.example .env
)
echo.

REM Check skills
echo [7/8] Checking skills...
if exist ".qwen\skills" (
    echo [OK] Skills directory exists
    dir /b .qwen\skills | findstr /C:"whatsapp" > nul 2>&1 && echo [OK] WhatsApp Watcher skill found
    dir /b .qwen\skills | findstr /C:"linkedin" > nul 2>&1 && echo [OK] LinkedIn Poster skill found
    dir /b .qwen\skills | findstr /C:"email" > nul 2>&1 && echo [OK] Email MCP skill found
    dir /b .qwen\skills | findstr /C:"plan" > nul 2>&1 && echo [OK] Plan Generator skill found
    dir /b .qwen\skills | findstr /C:"hitl" > nul 2>&1 && echo [OK] HITL Approval skill found
    dir /b .qwen\skills | findstr /C:"scheduler" > nul 2>&1 && echo [OK] Scheduler skill found
) else (
    echo [WARN] .qwen\skills folder not found
)
echo.

REM Check watcher scripts
echo [8/8] Checking watcher scripts...
if exist "watchers\whatsapp_watcher.py" (
    echo [OK] WhatsApp Watcher script found
) else (
    echo [FAIL] WhatsApp Watcher script not found!
)

if exist "watchers\gmail_watcher.py" (
    echo [OK] Gmail Watcher script found
) else (
    echo [WARN] Gmail Watcher script not found
)

if exist "watchers\filesystem_watcher.py" (
    echo [OK] File System Watcher script found
) else (
    echo [WARN] File System Watcher script not found
)

if exist "orchestrator.py" (
    echo [OK] Orchestrator script found
) else (
    echo [FAIL] Orchestrator script not found!
)
echo.

echo ========================================
echo   Setup Verification Complete!
echo ========================================
echo.
echo Next Steps:
echo   1. If any [FAIL], install missing components
echo   2. Copy .env.example to .env and fill in details
echo   3. Run: start_ai_employee.bat
echo.
echo For detailed setup instructions, see:
echo   WORKFLOW_GUIDE.md
echo   SILVER_TIER_SETUP.md
echo.
pause
