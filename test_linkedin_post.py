"""
Test LinkedIn Post - Single Session Approach
This script logs in and posts in the same browser session to avoid session loss.
"""

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

# Configuration
VAULT_PATH = Path("AI_Employee_Vault")
SESSION_PATH = VAULT_PATH / ".linkedin_session"
HEADLESS = False  # Keep visible so you can see what's happening

# Post content
POST_CONTENT = """🎉 Exciting update about Testing AI Employee LinkedIn Automation

We've been working hard on Testing AI Employee LinkedIn Automation and wanted to share our progress.

Key highlights:
✅ Milestone 1
✅ Milestone 2
✅ Milestone 3

Thank you to everyone who made this possible!

#TestingAIEmployeeLinkedInAutomation #Business #Professional"""

HASHTAGS = ["#TestingAIEmployeeLinkedInAutomation", "#Business", "#Professional"]


def test_linkedin_post():
    """Test LinkedIn posting in a single session."""
    
    print("=" * 60)
    print("LinkedIn Post Test - Single Session")
    print("=" * 60)
    
    # Ensure session path exists
    SESSION_PATH.mkdir(parents=True, exist_ok=True)
    
    playwright = sync_playwright().start()
    
    # Launch with persistent context
    print("\n[1/5] Launching browser with persistent context...")
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=str(SESSION_PATH),
        headless=HEADLESS,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage',
        ],
        viewport={'width': 1280, 'height': 720},
    )
    
    page = context.pages[0]
    page.set_default_timeout(60000)
    
    print("[2/5] Navigating to LinkedIn...")
    page.goto('https://www.linkedin.com/login', wait_until='networkidle')
    time.sleep(3)
    
    # Check if already logged in
    print("[3/5] Checking login status...")
    page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
    time.sleep(5)
    
    # Check URL to see if we're on feed or login page
    current_url = page.url
    print(f"     Current URL: {current_url}")
    
    # Also check page content
    page_title = page.title()
    print(f"     Page Title: {page_title}")
    
    # Check if we're actually on the feed page (not just redirected)
    is_logged_in = False
    try:
        # Look for feed-specific elements
        if page.is_visible('div.share-box-feed-entry', timeout=5000):
            is_logged_in = True
            print("     Found feed elements - logged in!")
        elif page.is_visible('div.ProseMirror', timeout=5000):
            is_logged_in = True
            print("     Found editor - logged in!")
        elif 'login' in current_url.lower():
            is_logged_in = False
    except:
        pass
    
    if not is_logged_in:
        print("\n⚠️  NOT LOGGED IN - Please log in manually in the browser window")
        print("   After logging in, wait for the script to continue...")
        
        # Wait for user to log in
        max_wait = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            time.sleep(5)
            current_url = page.url
            
            # Check for actual feed elements, not just URL
            try:
                if page.is_visible('div.share-box-feed-entry', timeout=3000):
                    print("✓ Login detected (feed elements visible)!")
                    is_logged_in = True
                    break
                elif page.is_visible('div.ProseMirror', timeout=3000):
                    print("✓ Login detected (editor visible)!")
                    is_logged_in = True
                    break
            except:
                pass
                
            # Check if still on login page
            if 'login' in current_url.lower() and page.is_visible('#login-form', timeout=3000):
                print(f"   Waiting for login... ({int(time.time() - start_time)}s elapsed)")
        else:
            print("✗ Login timeout!")
            page.screenshot(path='linkedin_login_timeout.png')
            context.close()
            playwright.stop()
            return False
    
    if is_logged_in:
        print("✓ Logged in successfully!")
    
    # Now try to post
    print("\n[4/5] Creating post...")
    page.goto('https://www.linkedin.com/feed/?shareActive=true', wait_until='networkidle')
    time.sleep(5)
    
    # Take screenshot before attempting to post
    page.screenshot(path='linkedin_before_post.png')
    print("     Screenshot saved: linkedin_before_post.png")
    
    # Try to find and fill the editor
    editor_found = False
    
    # Try ProseMirror
    try:
        editor = page.locator('div.ProseMirror')
        if editor.count() > 0:
            print("     Found ProseMirror editor")
            editor.fill(POST_CONTENT)
            editor_found = True
    except Exception as e:
        print(f"     ProseMirror not found: {e}")
    
    # Try contenteditable
    if not editor_found:
        try:
            textarea = page.locator('div[contenteditable="true"][role="textbox"]')
            if textarea.count() > 0:
                print("     Found contenteditable textarea")
                textarea.fill(POST_CONTENT)
                editor_found = True
        except Exception as e:
            print(f"     Contenteditable not found: {e}")
    
    if not editor_found:
        print("✗ Could not find editor - taking screenshot...")
        page.screenshot(path='linkedin_no_editor.png')
        print("     Screenshot saved: linkedin_no_editor.png")
        
        # Try clicking "Start a post"
        print("     Trying to click 'Start a post' button...")
        try:
            start_post = page.get_by_role('button', name='Start a post')
            if start_post.count() > 0:
                start_post.first.click()
                time.sleep(3)
                
                # Try editor again
                editor = page.locator('div.ProseMirror')
                if editor.count() > 0:
                    print("     Found editor after clicking Start a post")
                    editor.fill(POST_CONTENT)
                    editor_found = True
        except Exception as e:
            print(f"     Start a post click failed: {e}")
    
    if not editor_found:
        print("\n✗ FAILED: Could not find editor to fill content")
        context.close()
        playwright.stop()
        return False
    
    time.sleep(2)
    
    # Add hashtags (if not already in content)
    if HASHTAGS:
        try:
            editor = page.locator('div.ProseMirror').first
            editor.press('end')
            editor.type(' ' + ' '.join(HASHTAGS))
            print("     Hashtags added")
        except Exception as e:
            print(f"     Could not add hashtags: {e}")
    
    time.sleep(2)
    
    # Click Post button
    print("\n[5/5] Publishing post...")
    page.screenshot(path='linkedin_ready_to_post.png')
    
    try:
        # Find Post button
        post_button = page.get_by_role('button', name='Post')
        if post_button.count() == 0:
            post_button = page.get_by_role('button', name='Share')
        
        if post_button.count() > 0:
            print("     Found Post button, clicking...")
            post_button.first.click()
            time.sleep(5)
            
            # Check if post was successful
            page.screenshot(path='linkedin_after_post.png')
            print("     Screenshot saved: linkedin_after_post.png")
            
            # Check for success indicators
            current_url = page.url
            if 'feed' in current_url.lower():
                print("\n✓ SUCCESS! Post published!")
                print(f"     Current URL: {current_url}")
            else:
                print(f"\n? Post button clicked, check screenshot. URL: {current_url}")
        else:
            print("✗ Post button not found")
            page.screenshot(path='linkedin_no_post_button.png')
            
    except Exception as e:
        print(f"✗ Error clicking Post button: {e}")
        page.screenshot(path='linkedin_post_error.png')
    
    print("\n" + "=" * 60)
    print("Test complete! Check screenshots for results.")
    print("=" * 60)
    
    # Keep browser open for inspection
    print("\nKeeping browser open for 30 seconds for manual inspection...")
    time.sleep(30)
    
    context.close()
    playwright.stop()
    
    return True


if __name__ == '__main__':
    try:
        success = test_linkedin_post()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
