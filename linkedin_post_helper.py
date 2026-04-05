"""
LinkedIn Post Helper - Opens LinkedIn with content ready to paste
This is the most reliable method - script prepares everything, you click Post.
"""

import sys
import time
import webbrowser
from pathlib import Path

# Configuration
VAULT_PATH = Path("AI_Employee_Vault")
POST_FILE = VAULT_PATH / "Approved" / "Plan_linkedin_testing_linkedin_watcher_technologies.md"
IMAGE_FILE = VAULT_PATH / "Plans" / "linkedin_post_image.png"


def extract_post_content(file_path):
    """Extract clean post content."""
    content = file_path.read_text(encoding='utf-8')
    
    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            content = parts[2]
    
    # Remove sections
    if '## Suggested Actions' in content:
        content = content.split('## Suggested Actions')[0]
    if '## Notes' in content:
        content = content.split('## Notes')[0]
    
    content = content.strip().rstrip('-').strip()
    
    return content


def main():
    """Main function."""
    
    print("=" * 70)
    print("📝 LINKEDIN POST PREPARATION")
    print("=" * 70)
    
    # Check files
    if not POST_FILE.exists():
        print(f"\n✗ Post file not found: {POST_FILE}")
        return False
    
    # Extract content
    post_content = extract_post_content(POST_FILE)
    
    print("\n✅ POST CONTENT READY")
    print("=" * 70)
    print("\n📋 COPY THIS CONTENT:\n")
    print("-" * 70)
    print(post_content)
    print("-" * 70)
    
    # Save to clipboard file
    clipboard_file = VAULT_PATH / "Plans" / "linkedin_post_clipboard.txt"
    clipboard_file.write_text(post_content, encoding='utf-8')
    print(f"\n💾 Content also saved to: {clipboard_file}")
    
    print("\n🖼️ IMAGE:")
    if IMAGE_FILE.exists():
        print(f"   {IMAGE_FILE}")
        print(f"   (Upload this image first)")
    else:
        print("   No image")
    
    print("\n" + "=" * 70)
    print("📤 PUBLISHING STEPS")
    print("=" * 70)
    print("\n1. Opening LinkedIn in your browser...")
    print("2. Click 'Start a post'")
    print("3. Upload image (optional): " + str(IMAGE_FILE))
    print("4. Paste the content from above")
    print("5. Click 'Post' button")
    print("\nOpening LinkedIn in 3 seconds...")
    
    time.sleep(3)
    
    # Open LinkedIn
    webbrowser.open('https://www.linkedin.com/feed/')
    
    print("\n✅ LinkedIn opened!")
    print("\nAfter posting, run this to mark as complete:")
    print(f"   move {POST_FILE} AI_Employee_Vault\\Done\\")
    
    print("\n" + "=" * 70)
    print("GOOD LUCK WITH YOUR POST! 🚀")
    print("=" * 70)
    
    return True


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Cancelled")
    except Exception as e:
        print(f"\n✗ Error: {e}")
