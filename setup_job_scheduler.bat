@echo off
REM ================================================================
REM SETUP WINDOWS TASK SCHEDULER FOR JOB AUTO-APPLIER
REM ================================================================
REM This will schedule the job applier to run automatically:
REM - Every 4 hours when laptop is on
REM - At startup
REM - At logon
REM ================================================================

echo ================================================================
echo  SETTING UP AUTOMATED JOB APPLICATIONS
echo ================================================================
echo.

REM Get current directory
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%linkedin_job_applier.py
set BATCH_FILE=%SCRIPT_DIR%run_job_applier.bat

echo Script: %PYTHON_SCRIPT%
echo.

REM Create the batch file for running
echo Creating runner batch file...
(
echo @echo off
echo REM LinkedIn Job Auto-Applier Runner
echo cd /d "%SCRIPT_DIR%"
echo python linkedin_job_applier.py --max-jobs 20
echo echo Job Applier run completed at %%date%% %%time%%
) > "%BATCH_FILE%"

echo [OK] Runner batch created: %BATCH_FILE%
echo.

REM Create task with schtasks
echo Creating scheduled task...
echo.
echo Task Configuration:
echo   - Name: LinkedIn_Job_AutoApplier
echo   - Run: Every 4 hours
echo   - Also run at: Startup and Logon
echo   - Run only when user is logged on
echo   - Stop if running longer than: 1 hour
echo.

REM Delete existing task if exists
schtasks /Delete /TN "LinkedIn_Job_AutoApplier" /F > nul 2>&1

REM Create new task
schtasks /Create /TN "LinkedIn_Job_AutoApplier" ^
    /TR "\"%BATCH_FILE%\"" ^
    /SC HOURLY ^
    /MO 4 ^
    /RU "%USERNAME%" ^
    /RL HIGHEST ^
    /ST 09:00 ^
    /DU 00:00 ^
    /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Scheduled task created successfully!
    echo.
    echo ================================================================
    echo  TASK DETAILS
    echo ================================================================
    echo.
    echo Task Name: LinkedIn_Job_AutoApplier
    echo Schedule: Every 4 hours
    echo First Run: Today at 9:00 AM
    echo.
    echo To view/edit task:
    echo   1. Press Win+R
    echo   2. Type: taskschd.msc
    echo   3. Find: LinkedIn_Job_AutoApplier
    echo.
    echo To run manually:
    echo   schtasks /Run /TN "LinkedIn_Job_AutoApplier"
    echo.
    echo To check status:
    echo   schtasks /Query /TN "LinkedIn_Job_AutoApplier"
    echo.
    echo To delete:
    echo   schtasks /Delete /TN "LinkedIn_Job_AutoApplier" /F
    echo.
    echo ================================================================
) else (
    echo.
    echo [ERROR] Failed to create scheduled task
    echo.
    echo Manual setup required:
    echo   1. Press Win+R
    echo   2. Type: taskschd.msc
    echo   3. Click "Create Task"
    echo   4. Name: LinkedIn_Job_AutoApplier
    echo   5. Triggers: New - At startup, At logon, Daily
    echo   6. Actions: New - Start a program - %BATCH_FILE%
    echo   7. Conditions: Uncheck "Start only if on AC power"
    echo   8. Settings: Allow task to be run on demand
    echo.
)

echo.
echo ================================================================
echo  NEXT STEPS
echo ================================================================
echo.
echo 1. Update your profile in: AI_Employee_Vault\profile.yaml
echo 2. Add your resume PDF to: AI_Employee_Vault\resume.pdf
echo 3. Run once manually to test:
echo    python linkedin_job_applier.py
echo.
echo 4. Check logs in: AI_Employee_Vault\Logs\
echo 5. View applied jobs in: AI_Employee_Vault\Jobs\Applied\
echo.
echo ================================================================
pause
