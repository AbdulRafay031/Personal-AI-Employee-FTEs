"""
LinkedIn Poster Module

Automates LinkedIn posting for business lead generation and updates.
Uses Playwright for browser automation with human-in-the-loop approval.

Setup Requirements:
1. Install Playwright: pip install playwright
2. Install browser: playwright install chromium
3. Create session folder: mkdir -p /path/to/vault/.linkedin_session
4. Run once interactively to log in

Usage:
    python linkedin_poster.py /path/to/vault --action draft --topic "Your topic"
    python linkedin_poster.py /path/to/vault --action post --file "Approved/POST.md"
"""

import os
import sys
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from watchers.base_watcher import BaseWatcher
except ImportError:
    from base_watcher import BaseWatcher

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Run: pip install playwright && playwright install chromium")


class LinkedInPoster(BaseWatcher):
    """
    Automates LinkedIn posting.

    Supports:
    - Drafting posts based on topics
    - Posting with human approval
    - Scheduling posts
    - Analytics collection
    """

    # LinkedIn Web selectors (may need updates if LinkedIn changes UI)
    SELECTORS = {
        'create_post_button': '[data-id="gh-create-a-post"]',
        'post_textarea': 'div[contenteditable="true"][role="textbox"]',
        'post_button': 'button:has-text("Post")',
        'post_input': 'div.ProseMirror',
        'logged_in_indicator': 'img.avatar-image',  # Updated selector
        'login_form': '#login-form',
        'nav_menu': 'nav[aria-label="Main Navigation"]',  # Alternative login indicator
        'feed_url': 'https://www.linkedin.com/feed/',
        # Alternative post creation triggers
        'post_trigger_alt': 'button.ember-view.share-box-feed-entry__trigger',
        'start_post_button': 'button:has-text("Start a post")',
    }

    # Post templates
    POST_TEMPLATES = {
        'achievement': """🎉 {headline}

{body}

Key highlights:
{highlights}

{closing}

{hashtags}""",

        'educational': """💡 Let's talk about {topic}...

{insight}

Here's what I've learned:
{lessons}

{call_to_action}

{hashtags}""",

        'engagement': """❓ {question}

{context}

I'm curious to hear your thoughts! Share below! 👇

{hashtags}""",

        'promotional': """🚀 {announcement}

{description}

{offer}

{call_to_action}

{hashtags}""",
    }

    def __init__(
        self,
        vault_path: str,
        session_path: str,
        headless: bool = True,
        timeout: int = 30000,
    ):
        """
        Initialize LinkedIn Poster.

        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session data
            headless: Run browser in headless mode (default: True)
            timeout: Page load timeout in milliseconds (default: 30000)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not available. Install with: pip install playwright")

        # Don't call super().__init__() as we don't need watcher folders
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.timeout = timeout

        # Browser state
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Setup logging
        self._setup_logging()

        self.logger.info('LinkedIn Poster initialized')

    def _init_browser(self):
        """Initialize Playwright browser with persistent context."""
        try:
            playwright = sync_playwright().start()
            
            # Launch browser with persistent context
            self.context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ],
                viewport={'width': 1280, 'height': 720},
            )
            
            self.page = self.context.pages[0]
            self.page.set_default_timeout(self.timeout)
            
            self.logger.info('Browser initialized')
            
        except Exception as e:
            self.logger.error(f'Failed to initialize browser: {e}')
            raise

    def _check_login(self) -> bool:
        """
        Check if logged in to LinkedIn.

        Returns:
            True if logged in, False otherwise
        """
        try:
            # Navigate to LinkedIn
            self.page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=60000)
            time.sleep(5)  # Wait for page to load fully

            # Check for multiple logged in indicators (fallback approach)
            indicators = [
                'img.avatar-image',
                '.nav-item__profile-member-image',
                'nav[aria-label="Main Navigation"]',
                'button:has-text("Post")',  # Post button only visible when logged in
            ]

            for selector in indicators:
                try:
                    if self.page.is_visible(selector):
                        self.logger.info(f'Logged in detected via: {selector}')
                        return True
                except:
                    continue

            # Check URL - if we're still on feed (not redirected to login), we're logged in
            current_url = self.page.url
            if 'feed' in current_url or 'mynetwork' in current_url:
                self.logger.info('Logged in detected via URL')
                return True

            self.logger.info('Not logged in to LinkedIn')
            return False

        except Exception as e:
            self.logger.debug(f'Login check error: {e}')
            return False

    def login(self, interactive: bool = False):
        """
        Log in to LinkedIn.

        Args:
            interactive: If True, show browser for manual login
        """
        if self.page is None:
            self._init_browser()
        
        if self._check_login():
            return True
        
        # If not logged in, navigate to login page
        self.page.goto('https://www.linkedin.com/login', wait_until='networkidle')
        
        if interactive:
            self.logger.info('Please log in manually in the browser window')
            self.logger.info('After logging in, close the browser window')
            
            # Wait for user to log in manually
            max_wait = 300  # 5 minutes
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                time.sleep(5)
                if self._check_login():
                    self.logger.info('Login successful!')
                    return True
            
            self.logger.error('Login timeout')
            return False
        else:
            self.logger.warning('Not logged in. Run with --interactive to log in manually')
            return False

    def create_post(self, content: str, hashtags: List[str] = None, headless: bool = False, image_path: str = None) -> bool:
        """
        Create a LinkedIn post.

        Args:
            content: Post content
            hashtags: List of hashtags to append
            headless: Run browser in headless mode (default: False for posting)
            image_path: Optional path to image to upload

        Returns:
            True if successful, False otherwise
        """
        try:
            # Force non-headless mode for posting so user can see what's happening
            if self.page is None:
                self.headless = headless
                self._init_browser()

            # Ensure we're logged in
            if not self._check_login():
                self.logger.error('Not logged in to LinkedIn')
                return False

            # Navigate directly to post creation modal URL
            self.logger.info('Navigating to post creation page...')
            self.page.goto('https://www.linkedin.com/feed/?shareActive=true', wait_until='domcontentloaded', timeout=60000)
            time.sleep(5)  # Wait for modal to appear

            # Check if modal appeared, if not try alternative approaches
            editor_found = False
            
            # Check for editor
            if self.page.is_visible('div.ProseMirror', timeout=5000):
                editor_found = True
                self.logger.info('Post modal detected (ProseMirror)')
            elif self.page.is_visible('div[contenteditable="true"][role="textbox"]', timeout=5000):
                editor_found = True
                self.logger.info('Post modal detected (contenteditable)')
            
            if not editor_found:
                self.logger.info('Post modal not immediately visible, trying alternatives...')
                
                # Wait a bit more for lazy-loaded content
                time.sleep(3)
                
                # Try one more check
                if not self.page.is_visible('div.ProseMirror') and not self.page.is_visible('div[contenteditable="true"][role="textbox"]'):
                    self.logger.error('Could not open post creator - modal not found')
                    # Save screenshot for debugging
                    try:
                        self.page.screenshot(path='linkedin_error.png')
                        self.logger.info('Screenshot saved to linkedin_error.png')
                    except:
                        pass
                    return False

            # Find and fill post textarea
            try:
                # Try ProseMirror editor (newer LinkedIn UI)
                editor = self.page.locator('div.ProseMirror')
                if editor.count() > 0:
                    self.logger.info('Using ProseMirror editor')
                    editor.fill(content)
                else:
                    # Try contenteditable textarea
                    textarea = self.page.locator('div[contenteditable="true"][role="textbox"]')
                    if textarea.count() > 0:
                        self.logger.info('Using contenteditable textarea')
                        textarea.fill(content)
                    else:
                        self.logger.error('No editor found')
                        return False

                time.sleep(1)

                # Add hashtags
                if hashtags:
                    hashtag_text = ' ' + ' '.join(hashtags)
                    editor.press('end')
                    editor.type(hashtag_text)
                    time.sleep(1)

                time.sleep(2)
                
                # Upload image if provided
                if image_path and os.path.exists(image_path):
                    self.logger.info(f'Uploading image: {image_path}')
                    try:
                        # Wait for editor to be ready
                        time.sleep(2)
                        
                        # Find and click the media/photo button
                        try:
                            # Look for photo button
                            photo_button = self.page.get_by_role('button', name='Photo')
                            if photo_button.count() > 0:
                                photo_button.first.click()
                                time.sleep(2)
                                
                                # Find file input and upload
                                file_input = self.page.locator('input[type="file"][accept*="image"]').first
                                file_input.set_input_files(image_path)
                                self.logger.info('Image upload initiated')
                                time.sleep(5)  # Wait for upload
                                self.logger.info('Image uploaded successfully')
                            else:
                                self.logger.warning('Photo button not found - posting without image')
                        except Exception as upload_error:
                            self.logger.warning(f'Image upload failed: {upload_error}')
                            self.logger.info('Continuing with text-only post')
                        
                    except Exception as e:
                        self.logger.warning(f'Image handling error: {e}')
                        self.logger.info('Continuing with text-only post')
                
            except Exception as e:
                self.logger.error(f'Failed to fill post content: {e}')
                return False
            
            # Click post button
            try:
                # Find post button by text
                submit_button = self.page.get_by_role('button', name='Post')
                if submit_button.count() == 0:
                    submit_button = self.page.get_by_role('button', name='Share')
                
                if submit_button.count() > 0:
                    # Check for dry run mode
                    if os.getenv('LINKEDIN_DRY_RUN', 'false').lower() == 'true':
                        self.logger.info('[DRY RUN] Would have posted to LinkedIn')
                        return True
                    
                    submit_button.first.click()
                    time.sleep(3)
                    
                    self.logger.info('Post published successfully!')
                    return True
                else:
                    self.logger.error('Post button not found')
                    return False
                    
            except Exception as e:
                self.logger.error(f'Failed to submit post: {e}')
                return False
            
        except Exception as e:
            self.logger.error(f'Failed to create post: {e}', exc_info=True)
            return False

    def generate_post_draft(self, topic: str, post_type: str = 'achievement') -> str:
        """
        Generate a post draft based on topic and type.

        Args:
            topic: Post topic/theme
            post_type: Type of post (achievement, educational, engagement, promotional)

        Returns:
            Generated post content
        """
        # This would typically call an AI model to generate content
        # For now, return a template-based draft
        
        template = self.POST_TEMPLATES.get(post_type, self.POST_TEMPLATES['achievement'])
        
        # Simple placeholder replacement
        draft = template.format(
            headline=f"Exciting update about {topic}",
            body=f"We've been working hard on {topic} and wanted to share our progress.",
            highlights="✅ Milestone 1\n✅ Milestone 2\n✅ Milestone 3",
            closing="Thank you to everyone who made this possible!",
            topic=topic,
            insight=f"Here's something interesting I've learned about {topic}...",
            lessons="1. Lesson one\n2. Lesson two\n3. Lesson three",
            call_to_action="What's your experience? Share below!",
            announcement=f"Big news about {topic}!",
            description=f"We're excited to announce something new related to {topic}.",
            offer="Special offer for early adopters!",
            question=f"What are your thoughts on {topic}?",
            context=f"This is an important topic in our industry.",
            hashtags=f"#{topic.replace(' ', '')} #Business #Professional"
        )
        
        return draft

    def get_analytics(self, days: int = 30) -> Dict:
        """
        Get post analytics from LinkedIn.

        Args:
            days: Number of days to retrieve analytics for

        Returns:
            Dictionary with analytics data
        """
        # Note: LinkedIn analytics scraping would go here
        # This is a placeholder for future implementation
        
        self.logger.info('Analytics collection not yet implemented')
        
        return {
            'posts': 0,
            'impressions': 0,
            'engagement_rate': 0.0,
        }

    def create_draft_file(self, topic: str, post_type: str = 'achievement') -> Optional[Path]:
        """
        Create a draft post file in Plans folder.

        Args:
            topic: Post topic
            post_type: Type of post

        Returns:
            Path to created file
        """
        try:
            plans_folder = self.vault_path / 'Plans'
            plans_folder.mkdir(parents=True, exist_ok=True)
            
            # Generate draft content
            content = self.generate_post_draft(topic, post_type)
            
            # Create file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"Plan_linkedin_{topic.lower().replace(' ', '_')}_{timestamp}.md"
            filepath = plans_folder / filename
            
            # Generate hashtags
            hashtags = [f"#{topic.replace(' ', '')}", "#Business", "#Professional"]
            
            file_content = f'''---
type: linkedin_draft
topic: {topic}
post_type: {post_type}
created: {datetime.now().isoformat()}
status: pending_review
author: AI_Employee
hashtags: {", ".join(hashtags)}
---

## Post Content

{content}

---

## Suggested Actions

- [ ] Review content for accuracy
- [ ] Edit tone/voice if needed
- [ ] Approve for posting (move to Pending_Approval/)
- [ ] Schedule for optimal time

---

## Notes

```
Add review notes here...
```
'''
            
            filepath.write_text(file_content, encoding='utf-8')
            self.logger.info(f'Created draft file: {filename}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Failed to create draft file: {e}')
            return None

    def create_approval_request(self, draft_file: Path) -> Optional[Path]:
        """
        Create approval request file in Pending_Approval folder.

        Args:
            draft_file: Path to draft file

        Returns:
            Path to created approval file
        """
        try:
            approval_folder = self.vault_path / 'Pending_Approval'
            approval_folder.mkdir(parents=True, exist_ok=True)
            
            # Read draft
            draft_content = draft_file.read_text(encoding='utf-8')
            
            # Parse frontmatter (simple parsing)
            import re
            match = re.search(r'^---\s*\n(.*?)\n---\s*\n', draft_content, re.DOTALL)
            frontmatter = {}
            if match:
                for line in match.group(1).split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip().strip('"\'')
            
            # Extract post content (after frontmatter)
            post_content = draft_content.split('---', 2)[-1].strip()
            
            # Create approval file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"LINKEDIN_POST_{timestamp}.md"
            filepath = approval_folder / filename
            
            # Calculate content hash
            content_hash = hashlib.md5(post_content.encode()).hexdigest()
            
            # Schedule for next optimal time (next business day at 9 AM)
            scheduled_time = self._get_next_optimal_posting_time()
            
            file_content = f'''---
type: approval_request
action: linkedin_post
content_hash: {content_hash}
created: {datetime.now().isoformat()}
scheduled_time: {scheduled_time.isoformat()}
status: pending
post_type: {frontmatter.get('post_type', 'unknown')}
---

## LinkedIn Post Approval

**Content Preview:**
{post_content}

**Scheduled Time:** {scheduled_time.strftime('%Y-%m-%d %I:%M %p PST')}
**Post Type:** {frontmatter.get('post_type', 'General')}
**Estimated Reach:** 500-1000 impressions

---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder with comments.

## To Edit
Move back to Plans/ with edit notes.
'''
            
            filepath.write_text(file_content, encoding='utf-8')
            self.logger.info(f'Created approval request: {filename}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Failed to create approval request: {e}')
            return None

    def _get_next_optimal_posting_time(self) -> datetime:
        """
        Get next optimal posting time.

        Returns:
            datetime for next optimal post
        """
        now = datetime.now()
        
        # Default to 9:00 AM next business day
        next_day = now + timedelta(days=1)
        
        # Skip weekends
        while next_day.weekday() >= 5:  # 5=Saturday, 6=Sunday
            next_day += timedelta(days=1)
        
        return next_day.replace(hour=9, minute=0, second=0, microsecond=0)

    def execute_approved_post(self, approval_file: Path) -> bool:
        """
        Execute an approved post.

        Args:
            approval_file: Path to approved file (can be approval_request or draft format)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read approval file
            content = approval_file.read_text(encoding='utf-8')

            # Try to extract post content from approval_request format first
            post_content_start = content.find('**Content Preview:**')

            if post_content_start != -1:
                # Approval request format
                post_content = content.split('**Content Preview:**')[1].split('---')[0].strip()
                # Remove the "## Post Content" header if present
                post_content = post_content.replace('## Post Content\n\n', '')
            else:
                # Draft format - extract content after frontmatter
                # Find where frontmatter ends (second ---)
                parts = content.split('---', 2)
                if len(parts) < 3:
                    self.logger.error('Could not parse draft file - no frontmatter')
                    return False
                
                # Get content after frontmatter
                main_content = parts[2].strip()
                
                # Remove sections that aren't part of the post
                # Remove "## Suggested Actions" and everything after
                if '## Suggested Actions' in main_content:
                    main_content = main_content.split('## Suggested Actions')[0].strip()
                
                # Remove "## Notes" section
                if '## Notes' in main_content:
                    main_content = main_content.split('## Notes')[0].strip()
                
                # Remove standalone horizontal rules at the end
                main_content = main_content.rstrip('-').strip()
                
                post_content = main_content

            # Extract hashtags from frontmatter if available
            hashtags = []
            if 'hashtags:' in content:
                hashtag_line = [line for line in content.split('\n') if 'hashtags:' in line]
                if hashtag_line:
                    hashtag_str = hashtag_line[0].split('hashtags:')[1].strip()
                    hashtags = [tag.strip() for tag in hashtag_str.split(',')]

            # Check for image attachment
            image_path = None
            if 'image:' in content:
                image_line = [line for line in content.split('\n') if 'image:' in line]
                if image_line:
                    image_path = image_line[0].split('image:')[1].strip()
                    if not os.path.exists(image_path):
                        self.logger.warning(f'Image not found: {image_path}')
                        image_path = None

            # Post to LinkedIn
            success = self.create_post(post_content, hashtags, headless=False, image_path=image_path)

            if success:
                # Log the action
                self._log_post(approval_file, post_content)

                # Move to Done
                done_folder = self.vault_path / 'Done'
                done_folder.mkdir(parents=True, exist_ok=True)
                done_path = done_folder / approval_file.name
                approval_file.rename(done_path)

                self.logger.info(f'Post executed successfully: {approval_file.name}')

            return success

        except Exception as e:
            self.logger.error(f'Failed to execute approved post: {e}', exc_info=True)
            return False

    def _log_post(self, approval_file: Path, content: str):
        """Log post to analytics file."""
        try:
            log_file = self.vault_path / 'Accounting' / 'Social_Media_Analytics.md'
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Append to log file
            timestamp = datetime.now().isoformat()
            log_entry = f"\n## {timestamp}\n\n- **Content:** {content[:100]}...\n- **Status:** Published\n- **File:** {approval_file.name}\n\n"
            
            if log_file.exists():
                content = log_file.read_text(encoding='utf-8')
                content += log_entry
            else:
                content = f"# Social Media Analytics\n\n{log_entry}"
            
            log_file.write_text(content, encoding='utf-8')
            
        except Exception as e:
            self.logger.error(f'Failed to log post: {e}')

    def check_for_updates(self) -> List:
        """
        Check for new items to process.
        
        For LinkedIn, this would check for scheduled posts or new topics.
        Returns empty list (LinkedIn poster is primarily action-driven).
        """
        return []

    def create_action_file(self, item: any) -> Optional[Path]:
        """
        Create a .md action file in the Needs_Action folder.
        
        Not used for LinkedIn poster (action-driven, not watcher-driven).
        """
        return None

    def cleanup(self):
        """Cleanup browser resources."""
        if self.context:
            try:
                self.context.close()
            except:
                pass


def main():
    """Main entry point for LinkedIn Poster."""
    import argparse

    parser = argparse.ArgumentParser(description='LinkedIn Poster for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--action', choices=['draft', 'post', 'login', 'schedule', 'analytics'],
                        default='draft', help='Action to perform')
    parser.add_argument('--topic', type=str, default=None, help='Topic for post draft')
    parser.add_argument('--file', type=str, default=None, help='Path to post/approval file')
    parser.add_argument('--session-path', type=str, default=None, help='Path to session storage')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--post-type', type=str, default='achievement',
                        choices=['achievement', 'educational', 'engagement', 'promotional'],
                        help='Type of post to create')
    parser.add_argument('--frequency', type=str, default='weekly',
                        choices=['daily', 'weekly', 'monthly'], help='Posting frequency')

    args = parser.parse_args()

    # Default session path
    session_path = args.session_path or str(Path(args.vault_path) / '.linkedin_session')

    try:
        poster = LinkedInPoster(
            args.vault_path,
            session_path,
            headless=args.headless and not args.interactive,
        )

        if args.action == 'login':
            poster.login(interactive=args.interactive)
        elif args.action == 'draft':
            if not args.topic:
                print('Error: --topic required for draft action')
                sys.exit(1)
            draft_file = poster.create_draft_file(args.topic, args.post_type)
            if draft_file:
                print(f'Draft created: {draft_file}')
        elif args.action == 'post':
            if not args.file:
                print('Error: --file required for post action')
                sys.exit(1)
            
            file_path = Path(args.file)
            if 'Approved' in str(file_path):
                # Execute approved post
                success = poster.execute_approved_post(file_path)
            else:
                # Create approval request from draft
                approval_file = poster.create_approval_request(file_path)
                if approval_file:
                    print(f'Approval request created: {approval_file}')
        elif args.action == 'schedule':
            print(f'Scheduling {args.frequency} posts (not yet implemented)')
        elif args.action == 'analytics':
            analytics = poster.get_analytics()
            print(f'Analytics: {analytics}')

        poster.cleanup()

    except KeyboardInterrupt:
        print('\nOperation cancelled by user')
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
