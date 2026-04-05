"""
Scheduled LinkedIn Post Publisher - Bronze Tier Completion
Run this script 2 hours after the first post to publish the Bronze Tier announcement.

Usage:
    python auto_post_linkedin_bronze.py
"""

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

# Configuration
VAULT_PATH = Path("AI_Employee_Vault")
SESSION_PATH = VAULT_PATH / ".linkedin_session"
POST_FILE = VAULT_PATH / "Plans" / "Plan_linkedin_bronze_tier_completion.md"
# Note: Image is optional - will post text-only if not found
IMAGE_FILE = VAULT_PATH / "Plans" / "bronze_tier_completion.png"
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


def post_to_linkedin_bronze():
    """Publish Bronze Tier completion post."""
    
    print("=" * 70)
    print("🥉 BRONZE TIER COMPLETION - LINKEDIN POST")
    print("=" * 70)
    
    # Validate files
    if not POST_FILE.exists():
        print(f"✗ Post file not found: {POST_FILE}")
        return False
    
    # Extract content
    post_content = extract_post_content(POST_FILE)
    print(f"\n✓ Post file: {POST_FILE.name}")
    print(f"✓ Content length: {len(post_content)} characters")
    
    has_image = IMAGE_FILE.exists()
    if has_image:
        print(f"✓ Image: {IMAGE_FILE.name}")
    else:
        print(f"ℹ No image found - will post text-only")
    
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
            ],
            viewport={'width': 1280, 'height': 800},
        )
        
        page = context.pages[0]
        page.set_default_timeout(90000)
        
        # Navigate to LinkedIn
        print("[2/6] Navigating to LinkedIn...")
        page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded')
        time.sleep(5)
        
        # Check authentication
        print("[3/6] Checking authentication...")
        is_logged_in = False
        
        try:
            if page.is_visible('div.share-box-feed-entry', timeout=5000):
                is_logged_in = True
            elif 'linkedin.com' in page.url and 'login' not in page.url.lower():
                is_logged_in = True
            
            if is_logged_in:
                print("✓ Already authenticated")
            else:
                print("✗ Not logged in - please login manually")
                context.close()
                playwright.stop()
                return False
        except:
            print("✗ Authentication check failed")
            context.close()
            playwright.stop()
            return False
        
        # Navigate to post creator
        print("\n[4/6] Opening post creator...")
        page.goto('https://www.linkedin.com/feed/?shareActive=true', wait_until='domcontentloaded')
        time.sleep(5)
        
        # Close overlays
        try:
            page.evaluate('''() => {
                const overlay = document.querySelector('#interop-outlet');
                if (overlay) overlay.style.display = 'none';
            }''')
            page.mouse.click(10, 10)
            time.sleep(1)
        except:
            pass
        
        # Find editor
        editor = None
        try:
            editor = page.locator('div.ProseMirror')
            if editor.count() == 0:
                editor = page.locator('div[contenteditable="true"][role="textbox"]')
        except:
            pass
        
        if editor is None or editor.count() == 0:
            # Try to open modal
            try:
                start_post = page.get_by_role('button', name='Start a post')
                if start_post.count() > 0:
                    start_post.first.click()
                    time.sleep(3)
                    editor = page.locator('div.ProseMirror').first
            except:
                print("✗ Could not open post creator")
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
            context.close()
            playwright.stop()
            return False
        
        # Upload image if exists
        if has_image:
            print("\n[6/6] Uploading image and publishing...")
            try:
                photo_button = page.get_by_role('button', name='Photo')
                if photo_button.count() > 0:
                    photo_button.first.click()
                    time.sleep(2)
                    file_input = page.locator('input[type="file"][accept*="image"]').first
                    file_input.set_input_files(str(IMAGE_FILE))
                    time.sleep(5)
                    print("✓ Image uploaded")
            except:
                print("⚠ Image upload skipped")
        else:
            print("\n[6/6] Publishing post...")
        
        # Dismiss overlays
        try:
            page.evaluate('''() => {
                const overlay = document.querySelector('#interop-outlet');
                if (overlay) overlay.style.display = 'none';
            }''')
            page.mouse.click(10, 10)
            time.sleep(1)
        except:
            pass
        
        # Click Post button
        try:
            post_button = page.get_by_role('button', name='Post')
            if post_button.count() == 0:
                post_button = page.get_by_role('button', name='Share')
            
            if post_button.count() > 0:
                print("✓ Found Post button")
                post_button.first.click(force=True)
                print("✓ Post button clicked!")
                
                time.sleep(5)
                page.screenshot(path='linkedin_bronze_post.png')
                
                if 'feed' in page.url:
                    print("\n" + "=" * 70)
                    print("✅ SUCCESS! BRONZE TIER POST PUBLISHED!")
                    print("=" * 70)
                    
                    # Move to Done
                    done_folder = VAULT_PATH / "Done"
                    done_folder.mkdir(parents=True, exist_ok=True)
                    done_path = done_folder / POST_FILE.name
                    POST_FILE.rename(done_path)
                    print(f"\n✓ Post file moved to Done/")
                    
                    success = True
                else:
                    print(f"\n⚠ Check screenshot: linkedin_bronze_post.png")
                    success = False
            else:
                print("✗ Post button not found")
                success = False
                
        except Exception as e:
            print(f"✗ Error during submit: {e}")
            success = False
        
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
    print("\n🚀 Starting Bronze Tier LinkedIn Post Publisher...\n")
    
    try:
        success = post_to_linkedin_bronze()
        
        if success:
            print("\n🎉 Bronze Tier post published successfully!")
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
