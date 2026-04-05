@echo off
REM ================================================================
REM QUICK TEST - LinkedIn Job Applier
REM ================================================================
REM This will:
REM 1. Open browser
REM 2. Navigate to LinkedIn Jobs
REM 3. Wait for you to login (if needed)
REM 4. Search for 1 keyword
REM 5. Show results
REM ================================================================

echo ================================================================
echo  LINKEDIN JOB APPLIER - QUICK TEST
echo ================================================================
echo.
echo This test will:
echo   1. Open Chromium browser
echo   2. Go to LinkedIn Jobs
echo   3. Wait for you to login (if not already)
echo   4. Search for "Frontend Developer Internship" in Karachi
echo   5. Show how many jobs found
echo.
echo IMPORTANT:
echo   - A browser window will open
echo   - If you see login page, LOGIN to LinkedIn
echo   - The script will continue automatically after login
echo.
pause

python -c "
from playwright.sync_api import sync_playwright
import time

print('\n[1/5] Launching browser...')
playwright = sync_playwright().start()
context = playwright.chromium.launch_persistent_context(
    user_data_dir='AI_Employee_Vault/.linkedin_jobs_session',
    headless=False,
    args=['--disable-blink-features=AutomationControlled'],
    viewport={'width': 1366, 'height': 768},
)

page = context.pages[0]
print('[2/5] Going to LinkedIn Jobs...')
page.goto('https://www.linkedin.com/jobs/', wait_until='domcontentloaded')
time.sleep(5)

print('[3/5] Checking login status...')
if 'login' in page.url.lower():
    print('    NOT LOGGED IN - Waiting 60 seconds for login...')
    for i in range(60, 0, -10):
        time.sleep(10)
        if 'jobs' in page.url.lower():
            print('    Login detected!')
            break
        print(f'    {i}s remaining...')

print('[4/5] Searching for jobs...')
search_url = 'https://www.linkedin.com/jobs/search?keywords=Frontend%20Developer%20Internship&location=Karachi%2C%20Pakistan&f_TPR=r86400&sortBy=DD'
page.goto(search_url, wait_until='domcontentloaded')
time.sleep(5)

print('[5/5] Counting jobs...')
try:
    job_cards = page.locator('div.job-card-container--clickable')
    count = job_cards.count()
    print(f'\n    FOUND {count} JOBS!')
    print(f'\n    Current URL: {page.url}')
    print(f'\n    Test complete!')
except Exception as e:
    print(f'    Error: {e}')

print('\nClosing in 10 seconds...')
time.sleep(10)
context.close()
playwright.stop()
print('Done!')
"

echo.
echo ================================================================
echo  TEST COMPLETE
echo ================================================================
echo.
echo If you saw "FOUND X JOBS" - the automation is working!
echo.
pause
