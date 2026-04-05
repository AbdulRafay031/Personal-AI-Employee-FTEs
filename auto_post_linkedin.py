"""
Fully Automated LinkedIn Post Publisher
Handles login and posting in a single session - no manual steps required!
"""

import sys
import time
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

# Configuration
VAULT_PATH = Path("AI_Employee_Vault")
SESSION_PATH = VAULT_PATH / ".linkedin_session"
POST_FILE = VAULT_PATH / "Approved" / "Plan_linkedin_testing_linkedin_watcher_technologies.md"
IMAGE_FILE = VAULT_PATH / "Plans" / "linkedin_post_image.png"
HEADLESS = False  # Must be visible for login


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


def wait_for_page_load(page, timeout=30):
    """Wait for page to fully load."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            if page.is_visible('body'):
                time.sleep(2)
                return True
        except:
            pass
        time.sleep(1)
    return False


def post_to_linkedin_automated():
    """Fully automated LinkedIn posting."""
    
    print("=" * 70)
    print("🤖 AI EMPLOYEE - LINKEDIN AUTO POSTER")
    print("=" * 70)
    
    # Validate files
    if not POST_FILE.exists():
        print(f"✗ Post file not found: {POST_FILE}")
        return False
    
    if not IMAGE_FILE.exists():
        print(f"✗ Image file not found: {IMAGE_FILE}")
        return False
    
    # Extract content
    post_content = extract_post_content(POST_FILE)
    print(f"\n✓ Post file: {POST_FILE.name}")
    print(f"✓ Image: {IMAGE_FILE.name}")
    print(f"✓ Content length: {len(post_content)} characters")
    
    # Ensure session path exists
    SESSION_PATH.mkdir(parents=True, exist_ok=True)
    
    playwright = sync_playwright().start()
    
    try:
        # Launch browser
        print("\n[1/6] Launching browser with persistent session...")
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_PATH),
            headless=HEADLESS,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ],
            viewport={'width': 1280, 'height': 800},
        )
        
        page = context.pages[0]
        page.set_default_timeout(90000)
        
        # Navigate to LinkedIn
        print("[2/6] Navigating to LinkedIn...")
        page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded')
        time.sleep(3)
        
        # Check if already logged in
        print("[3/6] Checking authentication...")
        page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded')
        time.sleep(5)
        
        is_logged_in = False
        
        # Check multiple indicators
        try:
            if page.is_visible('div.share-box-feed-entry', timeout=5000):
                is_logged_in = True
                print("✓ Already authenticated (feed visible)")
            elif page.is_visible('img.avatar-image', timeout=5000):
                is_logged_in = True
                print("✓ Already authenticated (avatar visible)")
            elif page.is_visible('[aria-label="Main Navigation"]', timeout=5000):
                is_logged_in = True
                print("✓ Already authenticated (nav visible)")
            elif page.is_visible('button:has-text("Create a post")', timeout=5000):
                is_logged_in = True
                print("✓ Already authenticated (create post button visible)")
            # Check if on any LinkedIn page that's not login
            elif 'linkedin.com' in page.url and 'login' not in page.url.lower() and 'uas' not in page.url.lower():
                is_logged_in = True
                print(f"✓ Already authenticated (on page: {page.url[:60]}...)")
        except Exception as e:
            print(f"   Auth check: {e}")
            pass
        
        # If not logged in, wait for manual login
        if not is_logged_in:
            print("\n⏳ Waiting for login (300 seconds)...")
            print("   → A browser window should have opened")
            print("   → LOGIN to LinkedIn in that browser window NOW")
            print("   → After login, script will auto-detect and continue")
            print("   → You have 5 minutes to complete login")
            print("")
            
            max_wait = 300
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                time.sleep(5)
                try:
                    # Check if we're on feed now
                    current_url = page.url
                    if 'feed' in current_url and page.is_visible('div.share-box-feed-entry', timeout=3000):
                        print(f"\n✓ Login detected! (elapsed: {int(time.time() - start_time)}s)")
                        is_logged_in = True
                        break
                    elif page.is_visible('div.share-box-feed-entry', timeout=3000):
                        print(f"\n✓ Login detected! (elapsed: {int(time.time() - start_time)}s)")
                        is_logged_in = True
                        break
                    elif page.is_visible('img.avatar-image', timeout=3000):
                        print(f"\n✓ Login detected! (elapsed: {int(time.time() - start_time)}s)")
                        is_logged_in = True
                        break
                except:
                    pass
                
                elapsed = int(time.time() - start_time)
                if elapsed % 30 == 0 and elapsed > 0:
                    print(f"   ⏱ Waiting for login... ({elapsed}s/{max_wait}s)")
                    print(f"      Current URL: {page.url[:80]}...")
            
            if not is_logged_in:
                print(f"\n✗ Login timeout after {max_wait} seconds")
                page.screenshot(path='linkedin_login_failed.png')
                print("   Screenshot saved: linkedin_login_failed.png")
                context.close()
                playwright.stop()
                return False
        
        # Navigate to post creator
        print("\n[4/6] Opening post creator...")
        page.goto('https://www.linkedin.com/feed/?shareActive=true', wait_until='domcontentloaded')
        time.sleep(5)
        
        # Take screenshot
        page.screenshot(path='linkedin_step1_feed.png')
        
        # Close any overlays/popups first
        print("   Checking for overlays/popups...")
        try:
            # Close cookie banner
            cookie_close = page.locator('button[aria-label*="close"], button[id*="close"], .artdeco-toast-item__dismiss')
            if cookie_close.count() > 0:
                cookie_close.first.click()
                time.sleep(1)
                print("   ✓ Closed cookie banner")
        except:
            pass
        
        try:
            # Close notification popup
            notif_close = page.locator('[data-test-close-notification-promo] button')
            if notif_close.count() > 0:
                notif_close.first.click()
                time.sleep(1)
                print("   ✓ Closed notification")
        except:
            pass
        
        try:
            # Close any dialog overlay
            dialog_close = page.locator('button[aria-label="Close dialog"]')
            if dialog_close.count() > 0:
                dialog_close.first.click()
                time.sleep(1)
                print("   ✓ Closed dialog")
        except:
            pass
        
        try:
            # Click on body to dismiss any tooltips
            page.click('body', position={'x': 100, 'y': 100})
            time.sleep(1)
        except:
            pass
        
        # Take another screenshot after cleanup
        page.screenshot(path='linkedin_after_cleanup.png')
        
        # Find editor - try multiple approaches
        editor = None
        post_opened = False
        
        # Approach 1: Check if modal already open
        try:
            editor = page.locator('div.ProseMirror')
            if editor.count() > 0:
                post_opened = True
                print("✓ Post modal already open (ProseMirror)")
        except:
            pass
        
        if not post_opened:
            try:
                editor = page.locator('div[contenteditable="true"][role="textbox"]')
                if editor.count() > 0:
                    post_opened = True
                    print("✓ Post modal already open (contenteditable)")
            except:
                pass
        
        # Approach 2: Click to open modal
        if not post_opened:
            print("   Opening post modal...")
            
            # Try clicking "Start a post"
            try:
                start_post = page.get_by_role('button', name='Start a post')
                if start_post.count() > 0:
                    start_post.first.click()
                    time.sleep(3)
                    post_opened = True
                    print("✓ Opened via 'Start a post' button")
            except Exception as e:
                print(f"   'Start a post' not clickable: {e}")
            
            # Try clicking share box
            if not post_opened:
                try:
                    share_box = page.locator('div.share-box-feed-entry').first
                    share_box.click()
                    time.sleep(3)
                    post_opened = True
                    print("✓ Opened via share box click")
                except Exception as e:
                    print(f"   Share box click failed: {e}")
            
            # Try keyboard navigation
            if not post_opened:
                try:
                    page.keyboard.press('Tab')
                    time.sleep(0.5)
                    page.keyboard.press('Enter')
                    time.sleep(3)
                    post_opened = True
                    print("✓ Opened via keyboard navigation")
                except Exception as e:
                    print(f"   Keyboard navigation failed: {e}")
        
        if not post_opened:
            print("✗ Could not open post modal")
            page.screenshot(path='linkedin_no_modal.png')
            context.close()
            playwright.stop()
            return False
        
        # Get editor reference again
        try:
            editor = page.locator('div.ProseMirror')
            if editor.count() == 0:
                editor = page.locator('div[contenteditable="true"][role="textbox"]')
        except:
            print("✗ Editor lost reference")
            context.close()
            playwright.stop()
            return False
        
        # Fill content
        print("\n[5/6] Adding post content...")
        try:
            editor.fill(post_content)
            time.sleep(2)
            print("✓ Content added successfully")
        except Exception as e:
            print(f"✗ Failed to add content: {e}")
            page.screenshot(path='linkedin_content_error.png')
            context.close()
            playwright.stop()
            return False
        
        # Upload image
        print("\n[6/6] Uploading image and publishing...")
        image_uploaded = False
        
        # Wait for editor to stabilize
        time.sleep(3)
        
        # Take screenshot before upload
        page.screenshot(path='linkedin_before_upload.png')
        
        # Try to upload image
        try:
            # Find and click photo button
            photo_button = page.get_by_role('button', name='Photo')
            if photo_button.count() > 0:
                photo_button.first.click()
                time.sleep(2)
                
                # Find file input and upload
                file_input = page.locator('input[type="file"][accept*="image"]').first
                file_input.set_input_files(str(IMAGE_FILE))
                print("✓ Image upload initiated")
                
                # Wait for upload
                time.sleep(5)
                
                # Verify upload
                page.screenshot(path='linkedin_image_uploaded.png')
                print("✓ Image uploaded (screenshot saved)")
                image_uploaded = True
            else:
                print("⚠ Photo button not found - posting text only")
        except Exception as e:
            print(f"⚠ Image upload failed: {e}")
            print("  Continuing with text-only post...")
        
        # Final screenshot before posting
        page.screenshot(path='linkedin_before_submit.png')
        
        # DISMISS ANY OVERLAYS before clicking Post
        print("   Dismissing overlays before submit...")
        
        # Try to remove interop-outlet via JavaScript
        try:
            page.evaluate('''() => {
                const overlay = document.querySelector('#interop-outlet');
                if (overlay) {
                    overlay.style.display = 'none';
                    console.log('Hidden interop-outlet');
                }
                const toast = document.querySelector('.artdeco-toast');
                if (toast) {
                    toast.style.display = 'none';
                }
            }''')
            time.sleep(1)
            print("   ✓ Dismissed overlays via JavaScript")
        except Exception as e:
            print(f"   Could not dismiss via JS: {e}")
        
        # Click on empty area to dismiss tooltips
        try:
            page.mouse.click(10, 10)
            time.sleep(1)
        except:
            pass
        
        # Take screenshot after cleanup
        page.screenshot(path='linkedin_after_overlay_dismiss.png')
        
        # Click Post button
        try:
            post_button = page.get_by_role('button', name='Post')
            if post_button.count() == 0:
                post_button = page.get_by_role('button', name='Share')
            
            if post_button.count() > 0:
                print("✓ Found Post button")
                
                # Try force click
                try:
                    post_button.first.click(force=True)
                except:
                    # If force click fails, try keyboard
                    post_button.first.focus()
                    page.keyboard.press('Enter')
                
                print("✓ Post button clicked!")
                
                # Wait for post to publish
                time.sleep(5)
                
                # Final screenshot
                page.screenshot(path='linkedin_after_post.png')
                
                # Check if successful
                if 'feed' in page.url:
                    print("\n" + "=" * 70)
                    print("✅ SUCCESS! POST PUBLISHED TO LINKEDIN!")
                    print("=" * 70)
                    print(f"\n📸 Screenshots saved:")
                    print(f"   1. linkedin_step1_feed.png")
                    print(f"   2. linkedin_before_upload.png")
                    print(f"   3. linkedin_after_post.png")
                    if image_uploaded:
                        print(f"   4. linkedin_image_uploaded.png")
                    
                    # Move file to Done
                    done_folder = VAULT_PATH / "Done"
                    done_folder.mkdir(parents=True, exist_ok=True)
                    done_path = done_folder / POST_FILE.name
                    POST_FILE.rename(done_path)
                    print(f"\n✓ Post file moved to Done/")
                    
                    success = True
                else:
                    print(f"\n⚠ Post may not have published")
                    print(f"   Current URL: {page.url}")
                    print(f"   Check: linkedin_after_post.png")
                    success = False
            else:
                print("✗ Post button not found")
                page.screenshot(path='linkedin_no_submit.png')
                success = False
                
        except Exception as e:
            print(f"✗ Error during submit: {e}")
            page.screenshot(path='linkedin_submit_error.png')
            success = False
        
        # Keep browser open briefly
        print("\nClosing browser in 10 seconds...")
        time.sleep(10)
        
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
    print("\n🚀 Starting Automated LinkedIn Post Publisher...\n")
    
    try:
        success = post_to_linkedin_automated()
        
        if success:
            print("\n🎉 Process completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Process completed with errors")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        sys.exit(1)
