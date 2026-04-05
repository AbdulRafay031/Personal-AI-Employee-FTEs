@echo off
REM ================================================================
REM LINKEDIN POST - ONE CLICK PUBLISHER
REM ================================================================
REM This will:
REM 1. Copy post content to clipboard
REM 2. Open LinkedIn in your browser
REM 3. Open image folder
REM 4. You just paste and click Post
REM ================================================================

echo ================================================================
echo  LINKEDIN POST PUBLISHER
echo ================================================================
echo.
echo  Preparing your post...
echo.

REM Copy content to clipboard using PowerShell
powershell -command "Get-Content 'AI_Employee_Vault\Plans\linkedin_post_clipboard.txt' | Set-Clipboard"

echo  [OK] Post content copied to clipboard!
echo.

REM Open LinkedIn
start https://www.linkedin.com/feed/
echo  [OK] LinkedIn opened in browser!
echo.

REM Open image folder
explorer /select,"AI_Employee_Vault\Plans\linkedin_post_image.png"
echo  [OK] Image folder opened!
echo.
echo ================================================================
echo  NEXT STEPS:
echo ================================================================
echo.
echo  1. In LinkedIn, click 'Start a post'
echo  2. Press Ctrl+V to paste the content
echo  3. Click the Photo icon and select: linkedin_post_image.png
echo  4. Click the blue 'Post' button
echo.
echo  After posting, run this to mark complete:
echo    move AI_Employee_Vault\Approved\Plan_linkedin_*.md AI_Employee_Vault\Done\
echo.
echo ================================================================
pause
