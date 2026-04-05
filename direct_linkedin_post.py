"""
Direct LinkedIn Poster - Maximum Compatibility
Uses simplest possible approach to avoid LinkedIn detection.
"""

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

VAULT_PATH = Path("AI_Employee_Vault")
SESSION_PATH = VAULT_PATH / ".linkedin_session"
POST_FILE = VAULT_PATH / "Approved" / "Plan_linkedin_testing_linkedin_watcher_technologies.md"
IMAGE_FILE = VAULT_PATH / "Plans" / "linkedin_post_image.png"


def extract_content(file_path):
    content = file_path.read_text(encoding='utf-8')
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            content = parts[2]
    if '## Suggested Actions' in content:
        content = content.split('## Suggested Actions')[0]
    if '## Notes' in content:
        content = content.split('## Notes')[0]
    return content.strip().rstrip('-').strip()


def post():
    print("=" * 70)
    print("LINKEDIN POST - DIRECT METHOD")
    print("=" * 70)
    
    if not POST_FILE.exists():
        print("✗ Post file not found")
        return False
    
    content = extract_content(POST_FILE)
    print(f"✓ Content: {len(content)} chars")
    
    SESSION_PATH.mkdir(parents=True, exist_ok=True)
    playwright = sync_playwright().start()
    
    try:
        # Launch with larger viewport
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_PATH),
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1920, 'height': 1080},
        )
        
        page = context.pages[0]
        page.set_default_timeout(60000)
        
        # Go to LinkedIn
        print("\n[1/4] Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded')
        time.sleep(5)
        
        # Wait for login if needed
        if 'login' in page.url:
            print("[2/4] Please login... (90 seconds)")
            for i in range(90, 0, -10):
                time.sleep(10)
                if 'feed' in page.url:
                    break
                print(f"   {i}s remaining")
        
        print("\n[2/4] Opening post creator...")
        
        # CLICK the "Start a post" box directly
        page.click('text=Start a post', timeout=10000)
        print("✓ Clicked 'Start a post'")
        time.sleep(3)
        
        # Take screenshot
        page.screenshot(path='debug_modal_open.png')
        
        print("\n[3/4] Adding content...")
        
        # Click in the editor area first to focus it
        page.click('text=What do you want to talk about?', timeout=5000)
        time.sleep(1)
        
        # Use keyboard to paste content (more reliable than fill)
        page.keyboard.press('Control+a')  # Select all (clear any existing)
        time.sleep(0.5)
        
        # Type content in chunks to avoid detection
        lines = content.split('\n')
        for i, line in enumerate(lines[:20]):  # First 20 lines to test
            page.keyboard.type(line + '\n')
            time.sleep(0.1)
        
        print("✓ Content added via keyboard")
        time.sleep(2)
        
        # Upload image
        if IMAGE_FILE.exists():
            print("\n[4/4] Uploading image...")
            try:
                # Click Photo button
                page.click('button:has-text("Photo")', timeout=5000)
                time.sleep(2)
                
                # Upload file
                file_input = page.locator('input[type="file"]').first
                file_input.set_input_files(str(IMAGE_FILE))
                time.sleep(5)
                print("✓ Image uploaded")
            except Exception as e:
                print(f"⚠ Image upload: {str(e)[:50]}")
        
        # Screenshot before post
        page.screenshot(path='debug_ready_to_post.png')
        
        print("\n" + "=" * 70)
        print("✅ POST IS READY!")
        print("=" * 70)
        print("\n👉 PLEASE CLICK THE 'POST' BUTTON MANUALLY")
        print("   (The browser window is in front of you)")
        print("\n   Waiting 90 seconds...")
        
        # Wait for user to click Post
        for i in range(90, 0, -10):
            time.sleep(10)
            # Check if modal closed (post published)
            try:
                modal = page.locator('div[role="dialog"]').first
                if modal.count() == 0:
                    print("\n✓ Modal closed - post published!")
                    break
            except:
                pass
            if i % 30 == 0:
                print(f"   {i}s remaining...")
        
        # Check result
        time.sleep(2)
        page.screenshot(path='debug_after_post.png')
        
        if 'feed' in page.url:
            # Move to Done
            done_folder = VAULT_PATH / "Done"
            done_folder.mkdir(parents=True, exist_ok=True)
            POST_FILE.rename(done_folder / POST_FILE.name)
            print("\n✅ SUCCESS! Post published!")
            print("✓ File moved to Done/")
            success = True
        else:
            print("\n⚠ Check if post was published manually")
            success = False
        
        print("\nClosing in 10s...")
        time.sleep(10)
        
        context.close()
        playwright.stop()
        
        return success
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        try:
            page.screenshot(path='debug_error.png')
            print("   Screenshot: debug_error.png")
        except:
            pass
        context.close()
        playwright.stop()
        return False


if __name__ == '__main__':
    try:
        if post():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCancelled")
        sys.exit(1)
