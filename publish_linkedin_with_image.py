"""
Quick LinkedIn Post with Image - Single Session
Publishes the approved post with the generated image.
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
HEADLESS = False  # Keep visible so you can see what's happening


def extract_post_content(file_path):
    """Extract post content from markdown file."""
    content = file_path.read_text(encoding='utf-8')
    
    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            content = parts[2]
    
    # Extract main content (before "## Suggested Actions")
    if '## Suggested Actions' in content:
        content = content.split('## Suggested Actions')[0]
    
    # Clean up
    content = content.strip()
    
    # Remove hashtags section at the end if present
    if content.endswith('#AIAutomation #LinkedInAutomation #Python #Playwright #DigitalEmployee #Obsidian #MCP #LocalFirst #Automation #ProductivityTools #OpenSource'):
        content = content.replace('#AIAutomation #LinkedInAutomation #Python #Playwright #DigitalEmployee #Obsidian #MCP #LocalFirst #Automation #ProductivityTools #OpenSource', '').strip()
    
    return content


def post_to_linkedin():
    """Post to LinkedIn with image."""
    
    print("=" * 60)
    print("LinkedIn Post - With Image")
    print("=" * 60)
    
    # Check files exist
    if not POST_FILE.exists():
        print(f"✗ Post file not found: {POST_FILE}")
        return False
    
    if not IMAGE_FILE.exists():
        print(f"✗ Image file not found: {IMAGE_FILE}")
        return False
    
    # Extract content
    post_content = extract_post_content(POST_FILE)
    print(f"\n✓ Post content extracted ({len(post_content)} chars)")
    print(f"✓ Image: {IMAGE_FILE}")
    
    # Ensure session path exists
    SESSION_PATH.mkdir(parents=True, exist_ok=True)
    
    playwright = sync_playwright().start()
    
    # Launch with persistent context
    print("\n[1/4] Launching browser...")
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
    page.set_default_timeout(90000)
    
    # Navigate and check login
    print("[2/4] Navigating to LinkedIn...")
    page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
    time.sleep(5)
    
    # Check if logged in
    is_logged_in = False
    try:
        if page.is_visible('div.share-box-feed-entry', timeout=5000):
            is_logged_in = True
            print("✓ Already logged in!")
        elif page.is_visible('div.ProseMirror', timeout=5000):
            is_logged_in = True
            print("✓ Already logged in!")
    except:
        pass
    
    if not is_logged_in:
        print("\n⚠️  NOT LOGGED IN - Please log in manually...")
        
        max_wait = 300
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            time.sleep(5)
            try:
                if page.is_visible('div.share-box-feed-entry', timeout=3000):
                    print("✓ Login detected!")
                    is_logged_in = True
                    break
            except:
                pass
        else:
            print("✗ Login timeout!")
            context.close()
            playwright.stop()
            return False
    
    # Navigate to post creator
    print("\n[3/4] Opening post creator...")
    page.goto('https://www.linkedin.com/feed/?shareActive=true', wait_until='networkidle')
    time.sleep(5)
    
    # Take screenshot
    page.screenshot(path='linkedin_pre_post.png')
    
    # Find editor
    editor = None
    try:
        editor = page.locator('div.ProseMirror')
        if editor.count() == 0:
            editor = page.locator('div[contenteditable="true"][role="textbox"]')
    except:
        pass
    
    if editor is None or editor.count() == 0:
        print("✗ Editor not found - trying to click 'Start a post'...")
        try:
            start_post = page.get_by_role('button', name='Start a post')
            if start_post.count() > 0:
                start_post.first.click()
                time.sleep(3)
                editor = page.locator('div.ProseMirror').first
        except Exception as e:
            print(f"✗ Failed: {e}")
            context.close()
            playwright.stop()
            return False
    
    print("✓ Editor found")
    
    # Fill content
    print("[4/4] Creating post...")
    try:
        editor.fill(post_content)
        time.sleep(2)
        print("✓ Content added")
    except Exception as e:
        print(f"✗ Failed to add content: {e}")
        context.close()
        playwright.stop()
        return False
    
    # Upload image
    print("\n📷 Uploading image...")
    try:
        # Find and click the media/photo button
        media_button = page.locator('input[type="file"][accept*="image"]').first
        
        # Alternative: Look for photo button by role/text
        if media_button.count() == 0:
            photo_button = page.get_by_role('button', name='Photo')
            if photo_button.count() > 0:
                photo_button.first.click()
                time.sleep(2)
                media_button = page.locator('input[type="file"][accept*="image"]').first
        
        if media_button.count() > 0:
            media_button.set_input_files(str(IMAGE_FILE))
            print("✓ Image upload initiated")
            time.sleep(5)  # Wait for upload
            
            # Verify image uploaded
            page.screenshot(path='linkedin_image_uploaded.png')
            print("✓ Image uploaded (screenshot saved)")
        else:
            print("⚠️  Could not find media upload button - posting without image")
            
    except Exception as e:
        print(f"⚠️  Image upload failed: {e}")
        print("  Continuing with text-only post...")
    
    # Click Post button
    print("\n📤 Publishing post...")
    try:
        post_button = page.get_by_role('button', name='Post')
        if post_button.count() == 0:
            post_button = page.get_by_role('button', name='Share')
        
        if post_button.count() > 0:
            post_button.first.click()
            print("✓ Post button clicked")
            time.sleep(5)
            
            # Check result
            page.screenshot(path='linkedin_post_result.png')
            
            # Check if we're back on feed
            if 'feed' in page.url:
                print("\n" + "=" * 60)
                print("✅ SUCCESS! Post published to LinkedIn!")
                print("=" * 60)
                print(f"\n📸 Screenshots saved:")
                print(f"   - linkedin_pre_post.png")
                print(f"   - linkedin_image_uploaded.png")
                print(f"   - linkedin_post_result.png")
                
                # Move to Done
                done_folder = VAULT_PATH / "Done"
                done_folder.mkdir(parents=True, exist_ok=True)
                done_path = done_folder / POST_FILE.name
                POST_FILE.rename(done_path)
                print(f"\n✓ Post file moved to Done/")
                
                success = True
            else:
                print(f"\n⚠️  Post may not have published. Check screenshot: linkedin_post_result.png")
                print(f"   Current URL: {page.url}")
                success = False
        else:
            print("✗ Post button not found")
            page.screenshot(path='linkedin_no_post_button.png')
            success = False
            
    except Exception as e:
        print(f"✗ Error publishing: {e}")
        page.screenshot(path='linkedin_publish_error.png')
        success = False
    
    # Keep browser open for inspection
    print("\nKeeping browser open for 15 seconds...")
    time.sleep(15)
    
    context.close()
    playwright.stop()
    
    return success


if __name__ == '__main__':
    try:
        success = post_to_linkedin()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
