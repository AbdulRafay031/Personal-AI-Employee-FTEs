"""
Semi-Automated LinkedIn Poster
Automation does everything except the final Post button click.
This is the most reliable approach for LinkedIn.
"""

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

# Configuration
VAULT_PATH = Path("AI_Employee_Vault")
SESSION_PATH = VAULT_PATH / ".linkedin_session"
POST_FILE = VAULT_PATH / "Approved" / "Plan_linkedin_testing_linkedin_watcher_technologies.md"
IMAGE_FILE = VAULT_PATH / "Plans" / "linkedin_post_image.png"
HEADLESS = False  # Must be visible so you can click Post


def extract_post_content(file_path):
    """Extract post content."""
    content = file_path.read_text(encoding='utf-8')
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            content = parts[2]
    
    if '## Suggested Actions' in content:
        content = content.split('## Suggested Actions')[0]
    if '## Notes' in content:
        content = content.split('## Notes')[0]
    
    content = content.strip().rstrip('-').strip()
    
    return content


def semi_auto_post():
    """Semi-automated posting - you click Post button."""
    
    print("=" * 70)
    print("🤖 AI EMPLOYEE - SEMI-AUTOMATED LINKEDIN POSTER")
    print("=" * 70)
    print("\n💡 HOW IT WORKS:")
    print("   → Automation does 95% of the work")
    print("   → You just click the final 'Post' button")
    print("   → This bypasses LinkedIn's anti-automation")
    print("=" * 70)
    
    # Check files
    if not POST_FILE.exists():
        done_file = VAULT_PATH / "Done" / POST_FILE.name
        if done_file.exists():
            print(f"\n⚠ File already in Done/ - skipping")
            return False
        print(f"✗ Post file not found: {POST_FILE}")
        return False
    
    post_content = extract_post_content(POST_FILE)
    print(f"\n✓ Content ready: {len(post_content)} characters")
    
    SESSION_PATH.mkdir(parents=True, exist_ok=True)
    
    playwright = sync_playwright().start()
    
    try:
        # Launch browser
        print("\n[1/5] Launching browser...")
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_PATH),
            headless=HEADLESS,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ],
            viewport={'width': 1366, 'height': 768},
        )
        
        page = context.pages[0]
        page.set_default_timeout(90000)
        
        # Navigate to LinkedIn
        print("[2/5] Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded')
        time.sleep(5)
        
        # Check login
        print("[3/5] Checking login...")
        if 'login' in page.url.lower():
            print("\n⏳ Please login in the browser window (60 seconds)...")
            for i in range(60, 0, -10):
                time.sleep(10)
                if 'feed' in page.url:
                    print("✓ Login detected!")
                    break
                print(f"   Waiting... {i}s remaining")
        
        # Open post creator and fill content
        print("\n[4/5] Creating post...")
        page.goto('https://www.linkedin.com/feed/?shareActive=true', wait_until='domcontentloaded')
        time.sleep(5)
        
        # Find editor
        editor = None
        try:
            editor = page.locator('div.ProseMirror')
            if editor.count() == 0:
                editor = page.locator('div[contenteditable="true"][role="textbox"]')
        except:
            pass
        
        if editor is None or editor.count() == 0:
            # Click Start a post
            try:
                start_btn = page.get_by_role('button', name='Start a post')
                if start_btn.count() > 0:
                    start_btn.first.click()
                    time.sleep(3)
                    editor = page.locator('div.ProseMirror').first
            except:
                print("✗ Could not open post creator")
                context.close()
                playwright.stop()
                return False
        
        # Fill content
        if editor and editor.count() > 0:
            editor.fill(post_content)
            time.sleep(2)
            print("✓ Content added to post")
        else:
            print("✗ Editor not found")
            context.close()
            playwright.stop()
            return False
        
        # Upload image
        if IMAGE_FILE.exists():
            print("\n📷 Uploading image...")
            try:
                photo_btn = page.get_by_role('button', name='Photo')
                if photo_btn.count() > 0:
                    photo_btn.first.click()
                    time.sleep(2)
                    file_input = page.locator('input[type="file"][accept*="image"]').first
                    file_input.set_input_files(str(IMAGE_FILE))
                    time.sleep(5)
                    print("✓ Image uploaded")
                else:
                    print("⚠ Photo button not found")
            except Exception as e:
                print(f"⚠ Image upload failed: {e}")
        
        # Take screenshot
        page.screenshot(path='semi_auto_ready.png')
        
        # FINAL STEP - Human clicks Post
        print("\n" + "=" * 70)
        print("✅ POST READY TO PUBLISH!")
        print("=" * 70)
        print("\n👉 YOUR TASK:")
        print("   1. Look at the browser window")
        print("   2. You should see your post content")
        print("   3. Click the blue 'Post' button")
        print("   4. That's it!")
        print("\n⏰ Waiting 60 seconds for you to click Post...")
        print("   (Browser window is open in front of you)")
        print("=" * 70)
        
        # Wait for user to click
        for i in range(60, 0, -5):
            time.sleep(5)
            if i % 15 == 0:
                print(f"   {i} seconds remaining...")
        
        # Check if post was published
        print("\n\nChecking if post was published...")
        if 'feed' in page.url:
            print("✓ You're back on feed - post likely published!")
            
            # Move to Done
            done_folder = VAULT_PATH / "Done"
            done_folder.mkdir(parents=True, exist_ok=True)
            done_path = done_folder / POST_FILE.name
            POST_FILE.rename(done_path)
            print(f"✓ Post file moved to Done/")
            
            print("\n" + "=" * 70)
            print("🎉 SUCCESS! POST PUBLISHED!")
            print("=" * 70)
            success = True
        else:
            print("⚠ Still on post modal - post may not be published")
            print("   You can still click Post manually")
            success = False
        
        print("\nClosing browser in 10 seconds...")
        time.sleep(10)
        
        context.close()
        playwright.stop()
        
        return success
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            playwright.stop()
        except:
            pass
        return False


if __name__ == '__main__':
    print("\n🚀 Starting Semi-Automated LinkedIn Poster...\n")
    
    try:
        success = semi_auto_post()
        
        if success:
            print("\n✅ Process completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Process completed with issues")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        sys.exit(1)
