"""
LinkedIn Debug Script - Capture page structure for selector analysis
"""

from playwright.sync_api import sync_playwright
import time
import os

def debug_linkedin_feed():
    """Open LinkedIn and capture page structure for analysis."""
    
    print("Starting LinkedIn debug session...")
    print("This will open LinkedIn in a visible browser window.")
    print("After you log in, the page HTML will be saved for analysis.")
    
    playwright = sync_playwright().start()
    
    # Launch visible browser
    browser = playwright.chromium.launch(
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
    
    context = browser.new_context(
        viewport={'width': 1280, 'height': 720}
    )
    
    page = context.new_page()
    
    # Navigate to LinkedIn
    print("\nNavigating to LinkedIn...")
    page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
    
    # Wait for user to log in if needed
    print("\nIf you see login page, please log in now.")
    print("Waiting 60 seconds for page to stabilize...")
    
    for i in range(60, 0, -1):
        time.sleep(1)
        if i % 10 == 0:
            print(f"  {i} seconds remaining...")
    
    # Save page HTML for analysis
    html_content = page.content()
    output_file = 'linkedin_page_snapshot.html'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✓ Page HTML saved to: {output_file}")
    print(f"✓ Current URL: {page.url}")
    
    # Try to find common LinkedIn elements
    print("\n--- Element Detection ---")
    
    selectors_to_test = [
        ('[data-id="gh-create-a-post"]', 'Create post button (data-id)'),
        ('button:has-text("Start a post")', 'Start a post button (text)'),
        ('div.share-box-feed-entry__trigger', 'Share box trigger'),
        ('div.ProseMirror', 'ProseMirror editor'),
        ('div[contenteditable="true"][role="textbox"]', 'Content editable textarea'),
        ('img.avatar-image', 'Avatar image'),
        ('.nav-item__profile-member-image', 'Nav profile image'),
        ('nav[aria-label="Main Navigation"]', 'Main navigation'),
    ]
    
    for selector, description in selectors_to_test:
        try:
            count = page.locator(selector).count()
            status = "✓ FOUND" if count > 0 else "✗ NOT FOUND"
            print(f"{status}: {description} - {count} element(s)")
        except Exception as e:
            print(f"✗ ERROR: {description} - {str(e)[:50]}")
    
    # Take a screenshot
    screenshot_file = 'linkedin_snapshot.png'
    page.screenshot(path=screenshot_file)
    print(f"\n✓ Screenshot saved to: {screenshot_file}")
    
    print("\n--- Instructions ---")
    print("1. Open linkedin_page_snapshot.html in a text editor")
    print("2. Search for 'Start a post' or 'Create a post' to find the correct selector")
    print("3. Look for buttons with aria-label or data-testid attributes")
    print("\nKeeping browser open for 30 more seconds for manual inspection...")
    
    time.sleep(30)
    
    browser.close()
    playwright.stop()
    print("\nDebug session complete!")


if __name__ == '__main__':
    debug_linkedin_feed()
