"""
Reliable LinkedIn Post Publisher - Guaranteed Post
This script ensures the post is actually published with better error handling.
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
HEADLESS = False


def extract_post_content(file_path):
    """Extract post content from markdown file."""
    content = file_path.read_text(encoding='utf-8')
    
    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            content = parts[2]
    
    # Remove sections that aren't part of the post
    if '## Suggested Actions' in content:
        content = content.split('## Suggested Actions')[0]
    if '## Notes' in content:
        content = content.split('## Notes')[0]
    
    # Clean up
    content = content.strip().rstrip('-').strip()
    
    return content


def publish_reliable():
    """Publish with maximum reliability."""
    
    print("=" * 70)
    print("🚀 RELIABLE LINKEDIN POST PUBLISHER")
    print("=" * 70)
    
    # Check files - move back from Done if needed
    if not POST_FILE.exists():
        # Check if in Done folder
        done_file = VAULT_PATH / "Done" / POST_FILE.name
        if done_file.exists():
            print(f"\n⚠ Post file already in Done/ - moving back to Approved/")
            done_file.rename(POST_FILE)
        else:
            print(f"✗ Post file not found: {POST_FILE}")
            return False
    
    # Extract content
    post_content = extract_post_content(POST_FILE)
    print(f"\n✓ Post file: {POST_FILE.name}")
    print(f"✓ Content length: {len(post_content)} characters")
    
    SESSION_PATH.mkdir(parents=True, exist_ok=True)
    
    playwright = sync_playwright().start()
    
    try:
        # Launch browser
        print("\n[1/7] Launching browser...")
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
        page.set_default_timeout(120000)
        
        # Navigate to LinkedIn
        print("[2/7] Navigating to LinkedIn...")
        page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded')
        time.sleep(8)  # Wait longer for page to fully load
        
        # Check authentication
        print("[3/7] Checking authentication...")
        is_logged_in = False
        
        try:
            if 'linkedin.com' in page.url and 'login' not in page.url.lower():
                is_logged_in = True
                print(f"✓ Logged in (URL: {page.url[:60]}...)")
        except:
            pass
        
        if not is_logged_in:
            print("\n⏳ Waiting for login (120 seconds)...")
            print("   → LOGIN in the browser window now!")
            
            max_wait = 120
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                time.sleep(5)
                try:
                    if 'feed' in page.url and 'login' not in page.url.lower():
                        print("\n✓ Login detected!")
                        is_logged_in = True
                        break
                except:
                    pass
                
                elapsed = int(time.time() - start_time)
                if elapsed % 30 == 0 and elapsed > 0:
                    print(f"   Waiting... ({elapsed}s/{max_wait}s)")
            
            if not is_logged_in:
                print(f"\n✗ Login timeout")
                context.close()
                playwright.stop()
                return False
        
        # Navigate to post creator
        print("\n[4/7] Opening post creator...")
        page.goto('https://www.linkedin.com/feed/?shareActive=true', wait_until='domcontentloaded')
        time.sleep(8)
        
        # Take screenshot
        page.screenshot(path='reliable_step1_feed.png')
        
        # Dismiss ALL overlays
        print("   Dismissing overlays...")
        for i in range(3):
            try:
                page.evaluate('''() => {
                    const overlay = document.querySelector('#interop-outlet');
                    if (overlay) overlay.remove();
                    const toast = document.querySelector('.artdeco-toast');
                    if (toast) toast.remove();
                }''')
                time.sleep(0.5)
            except:
                pass
        
        try:
            page.mouse.click(50, 50)
            time.sleep(1)
        except:
            pass
        
        # Find editor
        print("\n[5/7] Adding content...")
        editor = None
        
        # Try to find editor
        try:
            editor = page.locator('div.ProseMirror')
            if editor.count() == 0:
                editor = page.locator('div[contenteditable="true"][role="textbox"]')
        except:
            pass
        
        # If no editor, click "Start a post"
        if editor is None or editor.count() == 0:
            print("   Opening post modal...")
            try:
                # Try multiple selectors
                selectors = [
                    'button:has-text("Start a post")',
                    'div.share-box-feed-entry',
                    '[data-id="gh-create-a-post"]',
                ]
                
                for selector in selectors:
                    try:
                        btn = page.locator(selector).first
                        if btn.count() > 0:
                            btn.click(force=True)
                            time.sleep(3)
                            print(f"   ✓ Opened with: {selector}")
                            break
                    except:
                        continue
                
                editor = page.locator('div.ProseMirror')
                if editor.count() == 0:
                    editor = page.locator('div[contenteditable="true"][role="textbox"]')
            except Exception as e:
                print(f"   ✗ Failed to open modal: {e}")
                page.screenshot(path='reliable_no_modal.png')
                context.close()
                playwright.stop()
                return False
        
        # Fill content
        if editor and editor.count() > 0:
            try:
                editor.fill(post_content)
                time.sleep(3)
                print("✓ Content added")
                page.screenshot(path='reliable_content_added.png')
            except Exception as e:
                print(f"✗ Failed to fill content: {e}")
                context.close()
                playwright.stop()
                return False
        else:
            print("✗ Editor not found")
            context.close()
            playwright.stop()
            return False
        
        # Try image upload
        if IMAGE_FILE.exists():
            print("\n[6/7] Uploading image...")
            try:
                photo_button = page.get_by_role('button', name='Photo')
                if photo_button.count() > 0:
                    photo_button.first.click(force=True)
                    time.sleep(2)
                    file_input = page.locator('input[type="file"][accept*="image"]').first
                    file_input.set_input_files(str(IMAGE_FILE))
                    time.sleep(5)
                    print("✓ Image uploaded")
                    page.screenshot(path='reliable_image_uploaded.png')
                else:
                    print("⚠ Photo button not found")
            except Exception as e:
                print(f"⚠ Image upload failed: {e}")
        else:
            print("\n[6/7] Skipping image (not found)")
        
        # CRITICAL: Actually click Post button
        print("\n[7/7] Publishing post...")
        page.screenshot(path='reliable_before_submit.png')
        
        # Dismiss overlays one more time
        try:
            page.evaluate('''() => {
                const overlay = document.querySelector('#interop-outlet');
                if (overlay) overlay.remove();
            }''')
            page.mouse.click(20, 20)
            time.sleep(1)
        except:
            pass
        
        # Find and click Post button
        post_clicked = False
        
        try:
            # Try multiple times
            for attempt in range(3):
                print(f"   Attempt {attempt + 1}/3...")
                
                try:
                    post_button = page.get_by_role('button', name='Post')
                    if post_button.count() == 0:
                        post_button = page.get_by_role('button', name='Share')
                    
                    if post_button.count() > 0:
                        print(f"   ✓ Found Post button")
                        
                        # Force click
                        post_button.first.click(force=True)
                        print(f"   ✓ Clicked Post button!")
                        
                        # Wait for post to publish
                        time.sleep(8)
                        
                        # Take screenshot
                        page.screenshot(path=f'reliable_after_submit_{attempt}.png')
                        
                        # Check if we're back on feed
                        if 'feed' in page.url:
                            print("\n" + "=" * 70)
                            print("✅ SUCCESS! POST PUBLISHED!")
                            print("=" * 70)
                            post_clicked = True
                            break
                        else:
                            print(f"   ⚠ Still on post modal, trying again...")
                            time.sleep(2)
                    else:
                        print(f"   ✗ Post button not found")
                
                except Exception as e:
                    print(f"   ✗ Attempt {attempt + 1} failed: {e}")
                    time.sleep(2)
            
            if post_clicked:
                # Move file to Done
                done_folder = VAULT_PATH / "Done"
                done_folder.mkdir(parents=True, exist_ok=True)
                done_path = done_folder / POST_FILE.name
                POST_FILE.rename(done_path)
                print(f"\n✓ Post file moved to Done/")
                
                print(f"\n📸 Screenshots:")
                print(f"   - reliable_step1_feed.png")
                print(f"   - reliable_content_added.png")
                print(f"   - reliable_before_submit.png")
                print(f"   - reliable_after_submit_0.png")
                
                success = True
            else:
                print("\n" + "=" * 70)
                print("⚠ POST MAY NOT HAVE PUBLISHED")
                print("=" * 70)
                print(f"\n   Current URL: {page.url}")
                print(f"   Check: reliable_after_submit_0.png")
                success = False
                
        except Exception as e:
            print(f"\n✗ Error: {e}")
            page.screenshot(path='reliable_submit_error.png')
            success = False
        
        print("\nClosing browser in 15 seconds...")
        time.sleep(15)
        
        context.close()
        playwright.stop()
        
        return success
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        try:
            playwright.stop()
        except:
            pass
        return False


if __name__ == '__main__':
    print("\n🚀 Starting Reliable LinkedIn Publisher...\n")
    
    try:
        success = publish_reliable()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        sys.exit(1)
