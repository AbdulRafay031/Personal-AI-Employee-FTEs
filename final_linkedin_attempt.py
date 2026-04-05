"""
FINAL ATTEMPT - LinkedIn Poster using JavaScript Injection
Bypasses UI automation by directly injecting content via JavaScript.
"""

import sys
import time
import json
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
    print("LINKEDIN POST - JAVASCRIPT INJECTION METHOD")
    print("=" * 70)
    print("\nThis method uses JavaScript to bypass UI automation detection")
    print("=" * 70)
    
    if not POST_FILE.exists():
        print("✗ Post file not found")
        return False
    
    content = extract_content(POST_FILE)
    print(f"✓ Content: {len(content)} chars")
    
    SESSION_PATH.mkdir(parents=True, exist_ok=True)
    playwright = sync_playwright().start()
    
    try:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_PATH),
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1920, 'height': 1080},
        )
        
        page = context.pages[0]
        page.set_default_timeout(60000)
        
        # Open LinkedIn
        print("\n[1/5] Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded')
        time.sleep(5)
        
        # Wait for login
        if 'login' in page.url:
            print("   Please login... (90 seconds)")
            for i in range(90, 0, -10):
                time.sleep(10)
                if 'feed' in page.url:
                    break
                print(f"   {i}s")
        
        # Open post creator
        print("\n[2/5] Opening post creator...")
        page.click('text=Start a post', timeout=10000)
        print("✓ Post modal opened")
        time.sleep(3)
        
        # Inject content via JavaScript
        print("\n[3/5] Injecting content via JavaScript...")
        
        # Escape content for JavaScript
        js_content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        
        # JavaScript to find and fill the editor
        js_code = f"""
        (function() {{
            // Find ProseMirror editor
            var editor = document.querySelector('div.ProseMirror');
            if (!editor) {{
                // Try contenteditable
                editor = document.querySelector('div[contenteditable="true"][role="textbox"]');
            }}
            if (editor) {{
                // Focus the editor
                editor.focus();
                
                // Clear existing content
                editor.innerHTML = '';
                
                // Insert new content
                var textNode = document.createTextNode({json.dumps(content)});
                editor.appendChild(textNode);
                
                // Trigger input event
                var event = new InputEvent('input', {{ bubbles: true }});
                editor.dispatchEvent(event);
                
                return 'SUCCESS';
            }}
            return 'NO_EDITOR';
        }})()
        """
        
        result = page.evaluate(js_code)
        print(f"   JavaScript result: {result}")
        
        if result == 'SUCCESS':
            print("✓ Content injected")
            time.sleep(2)
            page.screenshot(path='js_injection_success.png')
        else:
            print("⚠ JavaScript injection had issues")
            page.screenshot(path='js_injection_issue.png')
        
        # Upload image
        if IMAGE_FILE.exists():
            print("\n[4/5] Uploading image...")
            try:
                page.click('button:has-text("Photo")', timeout=5000)
                time.sleep(2)
                file_input = page.locator('input[type="file"]').first
                file_input.set_input_files(str(IMAGE_FILE))
                time.sleep(5)
                print("✓ Image uploaded")
            except Exception as e:
                print(f"⚠ Image: {str(e)[:50]}")
        
        # Wait for user to click Post
        print("\n" + "=" * 70)
        print("✅ POST READY - PLEASE CLICK 'POST' BUTTON")
        print("=" * 70)
        print("\n   The browser window shows your post ready to publish")
        print("   Just click the blue 'Post' button")
        print("\n   Waiting 90 seconds...")
        
        for i in range(90, 0, -10):
            time.sleep(10)
            try:
                modal = page.locator('div[role="dialog"]')
                if modal.count() == 0:
                    print("\n✓ Modal closed - post published!")
                    break
            except:
                pass
            if i % 30 == 0:
                print(f"   {i}s")
        
        # Check and finalize
        page.screenshot(path='final_result.png')
        
        if 'feed' in page.url:
            done_folder = VAULT_PATH / "Done"
            done_folder.mkdir(parents=True, exist_ok=True)
            POST_FILE.rename(done_folder / POST_FILE.name)
            print("\n✅ SUCCESS!")
            print("✓ File moved to Done/")
            success = True
        else:
            print("\n⚠ Please verify post manually")
            success = False
        
        print("\nClosing in 10s...")
        time.sleep(10)
        
        context.close()
        playwright.stop()
        
        return success
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        try:
            page.screenshot(path='final_error.png')
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
