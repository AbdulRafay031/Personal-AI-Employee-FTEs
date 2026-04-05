@echo off
REM ===========================================
REM AI Employee Starter Script
REM For: Rafay (rafay16031@gmail.com)
REM ===========================================

echo.
echo ========================================
echo   AI Employee - Starting Services
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo.
    echo Please create .env file first:
    echo 1. Copy .env.example to .env
    echo 2. Fill in your API keys and settings
    echo.
    pause
    exit /b 1
)

REM Check if vault exists
if not exist "AI_Employee_Vault" (
    echo [ERROR] AI_Employee_Vault folder not found!
    echo.
    echo Please run Bronze Tier setup first.
    echo.
    pause
    exit /b 1
)

echo [OK] Configuration found
echo.

REM Create session folders if they don't exist
if not exist "AI_Employee_Vault\.whatsapp_session" mkdir "AI_Employee_Vault\.whatsapp_session"
if not exist "AI_Employee_Vault\.linkedin_session" mkdir "AI_Employee_Vault\.linkedin_session"

echo [OK] Session folders ready
echo.

REM Start WhatsApp Watcher
echo [1/3] Starting WhatsApp Watcher...
echo      - Monitoring WhatsApp Web for messages
echo      - Session: AI_Employee_Vault\.whatsapp_session
echo.
start "AI Employee - WhatsApp Watcher" python watchers/whatsapp_watcher.py AI_Employee_Vault --session-path AI_Employee_Vault\.whatsapp_session
timeout /t 3 /nobreak > nul

REM Start Orchestrator
echo [2/3] Starting Orchestrator...
echo      - Processing tasks from Needs_Action
echo      - Interval: 60 seconds
echo.
start "AI Employee - Orchestrator" python orchestrator.py AI_Employee_Vault --interval 60
timeout /t 3 /nobreak > nul

REM Start Approval Processor
echo [3/3] Starting Approval Processor...
echo      - Executing approved actions
echo      - Checking every 15 minutes
echo.
start "AI Employee - Approval Processor" python skills/approval_workflow.py AI_Employee_Vault --execute-approved
timeout /t 2 /nobreak > nul

echo.
echo ========================================
echo   All Services Started!
echo ========================================
echo.
echo Running Services:
echo   1. WhatsApp Watcher (monitoring messages)
echo   2. Orchestrator (processing tasks)
echo   3. Approval Processor (executing approved actions)
echo.
echo What to do next:
echo   1. Check AI_Employee_Vault/Dashboard.md for status
echo   2. Check AI_Employee_Vault/Pending_Approval\ for items needing your decision
echo   3. Send yourself a WhatsApp message with "test" to verify
echo.
echo To Stop:
echo   Close all three terminal windows
echo   OR press Ctrl+C in each window
echo.
echo ========================================
echo.

REM Open vault in Explorer
explorer AI_Employee_Vault

REM Show dashboard
if exist "AI_Employee_Vault\Dashboard.md" (
    echo Opening Dashboard...
    start AI_Employee_Vault\Dashboard.md
)

pause
