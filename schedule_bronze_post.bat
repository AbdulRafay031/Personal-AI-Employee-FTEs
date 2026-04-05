@echo off
REM Scheduled Task: Bronze Tier LinkedIn Post
REM This will run the Bronze Tier post publisher in 2 hours

echo ============================================================
echo BRONZE TIER POST - SCHEDULED FOR 2 HOURS FROM NOW
echo ============================================================
echo.
echo Current time: %TIME%
echo Scheduled run time: 2 hours from now
echo.
echo The script will:
echo   1. Wait for 2 hours (7200 seconds)
echo   2. Auto-publish the Bronze Tier completion post
echo   3. Move the file to Done/
echo   4. Close automatically
echo.
echo You can close this window - it will run in background.
echo ============================================================
echo.

REM Wait for 2 hours (7200 seconds) using timeout
REM timeout /t 7200 /nobreak
REM Note: timeout may not work in background, using Python instead

python -c "import time; print('Waiting 2 hours (7200 seconds)...'); time.sleep(7200); print('Wait complete!')"

REM Run the Bronze Tier post publisher
echo.
echo Running Bronze Tier post publisher...
python auto_post_linkedin_bronze.py

echo.
echo ============================================================
echo SCHEDULED TASK COMPLETE
echo ============================================================
pause
