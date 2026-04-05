@echo off
REM =====================================================
REM Platinum Tier AI Employee - Master Startup Script
REM =====================================================
REM This script starts all AI Employee components for Platinum tier operation.
REM 
REM Usage: START_PLATINUM_AI_EMPLOYEE.bat
REM 
REM Components Started:
REM 1. Gmail Watcher
REM 2. WhatsApp Watcher
REM 3. Filesystem Watcher
REM 4. Finance Watcher
REM 5. Orchestrator (with Ralph Wiggum loop)
REM 6. Health Monitor
REM 7. Audit Logger
REM 8. CEO Briefing Generator (scheduled)
REM =====================================================

echo.
echo ============================================================
echo   AI Employee - Platinum Tier Startup
echo ============================================================
echo.

REM Set working directory
set WORK_DIR=%~dp0
cd /d "%WORK_DIR%"

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.13 or higher.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found. Some features may not work.
    echo Please copy .env.example to .env and fill in your credentials.
    echo.
    pause
)

REM Create vault structure if it doesn't exist
if not exist "AI_Employee_Vault" (
    echo [INFO] Creating AI Employee vault structure...
    mkdir AI_Employee_Vault
    mkdir AI_Employee_Vault\Inbox
    mkdir AI_Employee_Vault\Needs_Action
    mkdir AI_Employee_Vault\In_Progress
    mkdir AI_Employee_Vault\Pending_Approval
    mkdir AI_Employee_Vault\Approved
    mkdir AI_Employee_Vault\Rejected
    mkdir AI_Employee_Vault\Done
    mkdir AI_Employee_Vault\Plans
    mkdir AI_Employee_Vault\Accounting
    mkdir AI_Employee_Vault\Briefings
    mkdir AI_Employee_Vault\Logs
    mkdir AI_Employee_Vault\Jobs
    mkdir AI_Employee_Vault\Invoices
    mkdir AI_Employee_Vault\Updates
    mkdir AI_Employee_Vault\Signals
    echo [INFO] Vault structure created.
    echo.
)

echo [INFO] Starting AI Employee components...
echo.

REM Start Gmail Watcher
echo [1/7] Starting Gmail Watcher...
start "AI Employee - Gmail Watcher" cmd /k "python watchers\gmail_watcher.py --vault-path AI_Employee_Vault"
timeout /t 2 >nul

REM Start WhatsApp Watcher
echo [2/7] Starting WhatsApp Watcher...
start "AI Employee - WhatsApp Watcher" cmd /k "python watchers\whatsapp_watcher.py --vault-path AI_Employee_Vault"
timeout /t 2 >nul

REM Start Filesystem Watcher
echo [3/7] Starting Filesystem Watcher...
start "AI Employee - Filesystem Watcher" cmd /k "python watchers\filesystem_watcher.py --vault-path AI_Employee_Vault"
timeout /t 2 >nul

REM Start Finance Watcher
echo [4/7] Starting Finance Watcher...
start "AI Employee - Finance Watcher" cmd /k "python watchers\finance_watcher.py --vault-path AI_Employee_Vault --mode csv"
timeout /t 2 >nul

REM Start Orchestrator
echo [5/7] Starting Orchestrator...
start "AI Employee - Orchestrator" cmd /k "python orchestrator.py --vault-path AI_Employee_Vault"
timeout /t 2 >nul

REM Start Health Monitor
echo [6/7] Starting Health Monitor...
start "AI Employee - Health Monitor" cmd /k "python health_monitor.py --vault-path AI_Employee_Vault"
timeout /t 2 >nul

REM Start Audit Logger (background logging)
echo [7/7] Initializing Audit Logger...
start "AI Employee - Audit Logger" cmd /k "python audit_logger.py --vault-path AI_Employee_Vault"
timeout /t 2 >nul

echo.
echo ============================================================
echo   All components started successfully!
echo ============================================================
echo.
echo   Monitoring Windows:
echo   - AI Employee - Gmail Watcher
echo   - AI Employee - WhatsApp Watcher
echo   - AI Employee - Filesystem Watcher
echo   - AI Employee - Finance Watcher
echo   - AI Employee - Orchestrator
echo   - AI Employee - Health Monitor
echo   - AI Employee - Audit Logger
echo.
echo   To stop all components, close each window or press Ctrl+C
echo   in each window.
echo.
echo   Vault Location: %WORK_DIR%AI_Employee_Vault
echo   Dashboard: %WORK_DIR%AI_Employee_Vault\Dashboard.md
echo.
echo ============================================================
echo.

REM Wait for user to press any key
echo Press any key to continue (this will NOT stop the components)...
pause >nul

REM Optional: Open vault in Obsidian
echo.
set /p OPEN_OBSIDIAN="Open vault in Obsidian? (y/n): "
if /i "%OPEN_OBSIDIAN%"=="y" (
    echo Opening Obsidian vault...
    start "" "obsidian://open?vault=AI_Employee_Vault"
)

echo.
echo AI Employee is now running in Platinum tier mode!
echo Check Dashboard.md for real-time status.
echo.
pause
