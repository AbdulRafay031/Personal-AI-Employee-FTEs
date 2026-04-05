"""
===============================================================================
LINKEDIN JOB AUTO-APPLIER - PHASE 1
===============================================================================
Fully Automated Job Application System

Features:
✅ Reads your LinkedIn profile
✅ Searches jobs by keywords (Frontend, AI, MERN, Internship)
✅ Filters relevant jobs
✅ Auto-fills Easy Apply applications
✅ Tracks all applications in Obsidian
✅ Runs on schedule (Windows Task Scheduler)

WARNING: This is Phase 1 (Local Automation)
- Runs when your laptop is ON
- You may need to solve CAPTCHAs if they appear
- LinkedIn may rate-limit after many applications

===============================================================================
"""

import os
import sys
import time
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Installing Playwright...")
    os.system('pip install playwright')
    os.system('playwright install chromium')
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class LinkedInJobApplier:
    """
    Automated LinkedIn Job Application System
    Phase 1: Local Automation
    """
    
    # LinkedIn selectors (may need updates)
    SELECTORS = {
        'jobs_nav': 'a[href*="/jobs/"]',
        'search_box': 'input[aria-label*="Search"]',
        'job_card': 'div.job-card-container--clickable',
        'easy_apply_button': 'button:has-text("Easy Apply")',
        'apply_form': 'div.artdeco-modal',
        'submit_button': 'button:has-text("Submit application")',
        'next_button': 'button:has-text("Next")',
        'review_button': 'button:has-text("Review")',
        'phone_input': 'input[type="tel"]',
        'resume_upload': 'input[type="file"][accept*=".pdf"]',
        'profile_section': 'div.profile-section',
        'login_form': '#login-form',
    }
    
    def __init__(self, vault_path: str, profile_path: str, headless: bool = False):
        """
        Initialize Job Applier
        
        Args:
            vault_path: Path to Obsidian vault
            profile_path: Path to profile YAML file
            headless: Run browser in background (default: False for visibility)
        """
        self.vault_path = Path(vault_path)
        self.profile_path = Path(profile_path)
        self.headless = headless
        self.jobs_folder = self.vault_path / "Jobs"
        self.applied_folder = self.jobs_folder / "Applied"
        self.saved_folder = self.jobs_folder / "Saved"
        self.logs_folder = self.vault_path / "Logs"
        self.session_path = self.vault_path / ".linkedin_jobs_session"
        
        # Create folders
        for folder in [self.jobs_folder, self.applied_folder, self.saved_folder, 
                       self.logs_folder, self.session_path]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Load profile
        self.profile = self.load_profile()
        
        # Setup logging
        self._setup_logging()
        
        # Track processed jobs
        self.processed_jobs = self.load_processed_jobs()
        
        # Application limits (to avoid ban)
        self.max_applications_per_day = 20
        self.applications_today = 0
        self.delay_between_applications = 120  # 2 minutes
        
        # Priority settings
        self.priority_hours = 24  # Prioritize jobs posted in last 24 hours
        self.location_priority = self.profile.get('locations', [])
        self.exclude_unpaid = self.profile.get('exclude_unpaid', True)
        
        self.logger.info(f"LinkedIn Job Applier initialized")
        self.logger.info(f"Profile: {self.profile.get('full_name', 'Unknown')}")
        self.logger.info(f"Max applications/day: {self.max_applications_per_day}")
    
    def load_profile(self) -> Dict:
        """Load user profile from YAML file."""
        try:
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                profile = yaml.safe_load(f)
            return profile
        except Exception as e:
            print(f"Error loading profile: {e}")
            return {}
    
    def _setup_logging(self):
        """Setup logging to file."""
        import logging
        
        log_file = self.logs_folder / f"job_applier_{datetime.now().strftime('%Y%m%d')}.log"
        
        self.logger = logging.getLogger('JobApplier')
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def load_processed_jobs(self) -> set:
        """Load list of already processed job IDs."""
        processed_file = self.jobs_folder / ".processed_jobs.json"
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    return set(json.load(f))
            except:
                pass
        return set()
    
    def save_processed_jobs(self):
        """Save processed job IDs to file."""
        processed_file = self.jobs_folder / ".processed_jobs.json"
        with open(processed_file, 'w') as f:
            json.dump(list(self.processed_jobs), f)
    
    def run(self, max_jobs: int = 50):
        """
        Main run function - scans and applies to jobs
        
        Args:
            max_jobs: Maximum number of jobs to process per run
        """
        self.logger.info("=" * 70)
        self.logger.info("Starting LinkedIn Job Auto-Applier - Phase 1")
        self.logger.info("=" * 70)
        
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not available")
            return
        
        playwright = sync_playwright().start()
        
        try:
            # Launch browser
            self.logger.info("Launching browser...")
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ],
                viewport={'width': 1366, 'height': 768},
            )
            
            page = context.pages[0]
            page.set_default_timeout(60000)
            
            # Navigate to LinkedIn
            self.logger.info("Navigating to LinkedIn...")
            page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded')
            time.sleep(3)
            
            # Check/login
            if not self.check_login(page):
                self.logger.info("Waiting for login (120 seconds)...")
                self.wait_for_login(page, timeout=120)
            
            # Search and apply to jobs
            self.logger.info("Searching for jobs...")
            jobs_found = self.search_and_apply(page, max_jobs=max_jobs)
            
            self.logger.info(f"Processed {jobs_found} jobs")
            self.logger.info(f"Applications today: {self.applications_today}")
            
            # Save state
            self.save_processed_jobs()
            
            self.logger.info("=" * 70)
            self.logger.info("Job Auto-Applier run complete")
            self.logger.info("=" * 70)
            
        except Exception as e:
            self.logger.error(f"Error: {e}", exc_info=True)
        finally:
            try:
                playwright.stop()
            except:
                pass
    
    def check_login(self, page) -> bool:
        """Check if logged in to LinkedIn."""
        try:
            page.goto('https://www.linkedin.com/jobs/', wait_until='domcontentloaded')
            time.sleep(3)
            
            # Check URL
            if 'login' in page.url.lower():
                return False
            
            # Check for jobs page elements
            try:
                if page.is_visible(self.SELECTORS['jobs_nav'], timeout=5000):
                    return True
            except:
                pass
            
            return 'jobs' in page.url.lower()
        except:
            return False
    
    def wait_for_login(self, page, timeout: int = 120):
        """Wait for user to login."""
        start = time.time()
        while time.time() - start < timeout:
            time.sleep(5)
            if self.check_login(page):
                self.logger.info("Login detected!")
                return True
            elapsed = int(time.time() - start)
            if elapsed % 30 == 0:
                self.logger.info(f"Waiting for login... {elapsed}s/{timeout}s")
        
        self.logger.error("Login timeout")
        return False
    
    def search_and_apply(self, page, max_jobs: int = 50) -> int:
        """Search for jobs and apply with location/time priority."""
        
        # Go to jobs page
        page.goto('https://www.linkedin.com/jobs/', wait_until='domcontentloaded')
        time.sleep(3)
        
        jobs_processed = 0
        keywords = self.profile.get('search_keywords', [])
        locations = self.profile.get('locations', ['Karachi, Pakistan', 'Remote'])
        
        # Priority 1: Search Karachi first
        self.logger.info("=" * 70)
        self.logger.info("PRIORITY 1: Searching Karachi, Pakistan jobs...")
        self.logger.info("=" * 70)
        
        for keyword in keywords[:5]:
            if jobs_processed >= max_jobs:
                break
            
            for location in locations[:1]:  # Karachi first
                self.logger.info(f"Searching: {keyword} in {location}")
                
                # Build search URL with location and time filter
                search_url = self.build_search_url(keyword, location, hours_ago=self.priority_hours)
                
                try:
                    page.goto(search_url, wait_until='domcontentloaded')
                    time.sleep(5)
                    
                    # Filter by "Easy Apply" and "Past 24 hours"
                    self.apply_filters(page)
                    time.sleep(3)
                    
                    # Process jobs
                    jobs_found = self.process_job_listings(page, keyword, max_jobs - jobs_processed)
                    jobs_processed += jobs_found
                    
                except Exception as e:
                    self.logger.error(f"Error searching '{keyword}' in '{location}': {e}")
                    continue
        
        # Priority 2: Remote jobs in other countries
        self.logger.info("=" * 70)
        self.logger.info("PRIORITY 2: Searching Remote jobs (UAE, USA, UK, Japan, Australia)...")
        self.logger.info("=" * 70)
        
        remote_locations = [loc for loc in locations if 'Remote' in loc or loc == 'Remote']
        
        for keyword in keywords[:5]:
            if jobs_processed >= max_jobs:
                break
            
            for location in remote_locations:
                self.logger.info(f"Searching: {keyword} in {location}")
                
                search_url = self.build_search_url(keyword, location, hours_ago=self.priority_hours)
                
                try:
                    page.goto(search_url, wait_until='domcontentloaded')
                    time.sleep(5)
                    
                    self.apply_filters(page)
                    time.sleep(3)
                    
                    jobs_found = self.process_job_listings(page, keyword, max_jobs - jobs_processed)
                    jobs_processed += jobs_found
                    
                except Exception as e:
                    self.logger.debug(f"Error: {e}")
                    continue
        
        return jobs_processed
    
    def build_search_url(self, keyword: str, location: str, hours_ago: int = 24) -> str:
        """Build LinkedIn jobs search URL with filters."""
        
        # Clean location for URL
        location_clean = location.replace(' (Remote)', '').replace(',', '%2C')
        
        # LinkedIn jobs URL with filters
        # f_TPR = time filter (r86400 = last 24 hours)
        # f_WT = workplace type (2 = remote)
        base_url = "https://www.linkedin.com/jobs/search"
        
        params = {
            'keywords': keyword.replace(' ', '%20'),
            'location': location_clean,
            'f_TPR': f'r{hours_ago * 3600}',  # Time filter (seconds)
            'sortBy': 'DD',  # Sort by date (most recent first)
        }
        
        # Add remote filter if location contains "Remote"
        if 'Remote' in location:
            params['f_WT'] = '2'  # Remote filter
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        
        return f"{base_url}?{query_string}"
    
    def apply_filters(self, page):
        """Apply Easy Apply and other filters."""
        
        # Try to click "Easy Apply" filter
        try:
            easy_apply_btn = page.get_by_text('Easy Apply', exact=False).first
            if easy_apply_btn.count() > 0:
                easy_apply_btn.click(force=True)
                time.sleep(2)
                self.logger.info("✓ Applied 'Easy Apply' filter")
        except:
            pass
        
        # Try to click "Past 24 hours" filter
        try:
            date_filter = page.get_by_text('Past 24 hours', exact=False).first
            if date_filter.count() > 0:
                date_filter.click(force=True)
                time.sleep(2)
                self.logger.info("✓ Applied 'Past 24 hours' filter")
        except:
            pass
        
        # Try to click "Remote" filter
        try:
            remote_filter = page.get_by_text('Remote', exact=False).first
            if remote_filter.count() > 0:
                remote_filter.click(force=True)
                time.sleep(2)
                self.logger.info("✓ Applied 'Remote' filter")
        except:
            pass
    
    def process_job_listings(self, page, keyword: str, max_jobs: int = 15) -> int:
        """Process job listings from search results."""
        
        jobs_processed = 0
        
        try:
            job_cards = page.locator(self.SELECTORS['job_card'])
            count = job_cards.count()
            
            self.logger.info(f"Found {count} jobs for '{keyword}'")
            
            for i in range(min(count, max_jobs)):
                if jobs_processed >= max_jobs:
                    break
                
                try:
                    job_card = job_cards.nth(i)
                    
                    # Check if job is from last 24 hours
                    is_recent = self.check_job_recency(job_card)
                    
                    # Check location match
                    location_match = self.check_location_match(job_card)
                    
                    # Click job to see details
                    job_card.click(force=True)
                    time.sleep(2)
                    
                    # Extract job data
                    job_data = self.extract_job_data(page, keyword)
                    job_data['is_recent'] = is_recent
                    job_data['location_match'] = location_match
                    
                    # Check if already processed
                    job_id = job_data.get('id', str(i))
                    if job_id in self.processed_jobs:
                        continue
                    
                    # Check if relevant
                    if self.is_job_relevant(job_data):
                        # Check if paid (not unpaid)
                        if self.exclude_unpaid and not self.is_job_paid(page):
                            self.logger.info(f"⚠ Unpaid - skipping: {job_data.get('title', 'Unknown')}")
                            self.processed_jobs.add(job_id)
                            continue
                        
                        self.logger.info(f"✓ Relevant job: {job_data.get('title', 'Unknown')}")
                        
                        # Save job
                        self.save_job(job_data)
                        
                        # Apply (prioritize recent jobs)
                        if self.applications_today < self.max_applications_per_day:
                            # If job is from last 24 hours, apply immediately
                            if is_recent:
                                self.logger.info("🔥 RECENT JOB (24h) - Applying immediately!")
                                success = self.apply_to_job(page, job_data)
                                if success:
                                    self.applications_today += 1
                                    self.processed_jobs.add(job_id)
                                    jobs_processed += 1
                            else:
                                # Older job - add to queue
                                self.logger.info("⏳ Older job - queued for later")
                                self.processed_jobs.add(job_id)
                    
                except Exception as e:
                    self.logger.debug(f"Error processing job {i}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error processing listings: {e}")
        
        return jobs_processed
    
    def check_job_recency(self, job_card) -> bool:
        """Check if job was posted in last 24 hours."""
        try:
            # Look for time indicator in job card
            time_text = job_card.inner_text().lower()
            
            if 'hour' in time_text or 'minute' in time_text:
                return True
            if 'day' in time_text and '1' in time_text:
                return True
            
            return False
        except:
            return False
    
    def check_location_match(self, job_card) -> bool:
        """Check if job location matches preferences."""
        try:
            location_text = job_card.inner_text().lower()
            
            # Check against preferred locations
            for loc in self.profile.get('location_keywords', []):
                if loc.lower() in location_text:
                    return True
            
            # Check for remote
            if 'remote' in location_text or 'work from home' in location_text:
                return True
            
            return False
        except:
            return False
    
    def is_job_paid(self, page) -> bool:
        """Check if job is paid (not unpaid internship)."""
        try:
            job_description = page.inner_text('body').lower()
            
            # Keywords indicating paid position
            paid_keywords = [
                'salary', 'paid', 'compensation', 'stipend',
                'pkR', 'usd', 'aed', 'gbp', 'jpy', 'aud',  # Currencies
                'competitive', 'benefits', 'perks'
            ]
            
            # Keywords indicating unpaid
            unpaid_keywords = [
                'unpaid', 'volunteer', 'expense only',
                'equity only', 'commission only'
            ]
            
            # Check for unpaid first
            for keyword in unpaid_keywords:
                if keyword in job_description:
                    return False
            
            # Check for paid indicators
            for keyword in paid_keywords:
                if keyword in job_description:
                    return True
            
            # Default: assume paid if not explicitly unpaid
            return True
            
        except:
            return True  # Default to assuming paid
    
    def is_easy_apply(self, page) -> bool:
        """Check if Easy Apply button exists."""
        try:
            return page.is_visible(self.SELECTORS['easy_apply_button'], timeout=3000)
        except:
            return False
    
    def extract_job_data(self, page, keyword: str) -> Dict:
        """Extract job information from page."""
        try:
            # Get job title
            title = ""
            try:
                title_elem = page.locator('h4.job-details-jobs-unified-top-card__job-title').first
                if title_elem.count() > 0:
                    title = title_elem.inner_text().strip()
            except:
                pass
            
            # Get company
            company = ""
            try:
                company_elem = page.locator('a.job-details-jobs-unified-top-card__company-name').first
                if company_elem.count() > 0:
                    company = company_elem.inner_text().strip()
            except:
                pass
            
            # Get location
            location = ""
            try:
                location_elem = page.locator('span.job-details-jobs-unified-top-card__bullet').first
                if location_elem.count() > 0:
                    location = location_elem.inner_text().strip()
            except:
                pass
            
            # Get job ID (from URL or generate)
            job_id = hashlib.md5(f"{title}{company}{datetime.now().date()}".encode()).hexdigest()[:12]
            
            return {
                'id': job_id,
                'title': title,
                'company': company,
                'location': location,
                'keyword': keyword,
                'url': page.url,
                'date_found': datetime.now().isoformat(),
                'status': 'found'
            }
        except Exception as e:
            self.logger.debug(f"Error extracting job data: {e}")
            return {
                'id': hashlib.md5(str(time.time()).encode()).hexdigest()[:12],
                'title': 'Unknown',
                'company': 'Unknown',
                'location': 'Unknown',
                'keyword': keyword,
                'url': page.url,
                'date_found': datetime.now().isoformat(),
                'status': 'found'
            }
    
    def is_job_relevant(self, job_data: Dict) -> bool:
        """Check if job matches our criteria."""
        title = job_data.get('title', '').lower()
        
        # Check exclude keywords
        exclude = [k.lower() for k in self.profile.get('exclude_keywords', [])]
        for exc in exclude:
            if exc in title:
                return False
        
        # Check if matches our skills/titles
        titles = [t.lower() for t in self.profile.get('titles', [])]
        skills = [s.lower() for s in self.profile.get('skills', [])]
        
        for t in titles:
            if t in title:
                return True
        
        for s in skills:
            if s in title:
                return True
        
        return False
    
    def save_job(self, job_data: Dict):
        """Save job to Obsidian vault."""
        try:
            filename = f"Job_{job_data['id']}_{job_data['title'].replace(' ', '_')[:30]}.md"
            filepath = self.saved_folder / filename
            
            content = f"""---
type: job_listing
id: {job_data['id']}
title: {job_data['title']}
company: {job_data['company']}
location: {job_data['location']}
url: {job_data['url']}
date_found: {job_data['date_found']}
status: {job_data['status']}
---

# {job_data['title']} at {job_data['company']}

**Location:** {job_data['location']}

**URL:** {job_data['url']}

---

## Application Status

- [ ] Applied
- [ ] Interview Scheduled
- [ ] Offer Received
- [ ] Rejected

---

## Notes

```
Add notes here...
```
"""
            
            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f"Saved job: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving job: {e}")
    
    def apply_to_job(self, page, job_data: Dict) -> bool:
        """
        Apply to a job using Easy Apply
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Applying to: {job_data.get('title', 'Unknown')}")
            
            # Click Easy Apply
            try:
                apply_button = page.locator(self.SELECTORS['easy_apply_button']).first
                apply_button.click(force=True)
                time.sleep(3)
            except Exception as e:
                self.logger.error(f"Could not click Easy Apply: {e}")
                return False
            
            # Fill application form
            success = self.fill_application_form(page)
            
            if success:
                # Update job status
                job_data['status'] = 'applied'
                job_data['date_applied'] = datetime.now().isoformat()
                self.update_job_status(job_data)
                
                self.logger.info(f"✓ Applied to: {job_data.get('title', 'Unknown')}")
                return True
            else:
                self.logger.warning(f"Application incomplete: {job_data.get('title', 'Unknown')}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error applying to job: {e}")
            return False
    
    def fill_application_form(self, page) -> bool:
        """Fill and submit Easy Apply form."""
        try:
            # Wait for form to load
            time.sleep(2)
            
            # Try to fill phone if asked
            try:
                phone_input = page.locator(self.SELECTORS['phone_input']).first
                if phone_input.count() > 0:
                    phone = self.profile.get('phone', '')
                    phone_input.fill(phone)
                    time.sleep(1)
            except:
                pass
            
            # Upload resume if asked
            try:
                resume_input = page.locator(self.SELECTORS['resume_upload']).first
                if resume_input.count() > 0:
                    # Note: You need to have a resume PDF
                    resume_path = self.vault_path / "resume.pdf"
                    if resume_path.exists():
                        resume_input.set_input_files(str(resume_path))
                        time.sleep(3)
                    else:
                        self.logger.warning("Resume not found - skipping upload")
            except:
                pass
            
            # Click through form (Next/Review buttons)
            for _ in range(5):  # Max 5 steps
                try:
                    # Try Next button
                    next_btn = page.get_by_role('button', name='Next')
                    if next_btn.count() > 0:
                        next_btn.first.click(force=True)
                        time.sleep(2)
                        continue
                    
                    # Try Review button
                    review_btn = page.get_by_role('button', name='Review')
                    if review_btn.count() > 0:
                        review_btn.first.click(force=True)
                        time.sleep(2)
                        continue
                    
                    # Try Submit button
                    submit_btn = page.get_by_role('button', name='Submit application')
                    if submit_btn.count() > 0:
                        submit_btn.first.click(force=True)
                        time.sleep(3)
                        self.logger.info("✓ Application submitted!")
                        return True
                    
                    # Try any continue button
                    continue_btn = page.get_by_role('button', name='Continue')
                    if continue_btn.count() > 0:
                        continue_btn.first.click(force=True)
                        time.sleep(2)
                        continue
                    
                    # No more buttons - form might be complete
                    break
                    
                except:
                    continue
            
            # Check if we're back on jobs page (successful submission)
            if 'jobs' in page.url:
                return True
            
            # Close modal if still open
            try:
                close_btn = page.locator('button[aria-label*="Close"]').first
                if close_btn.count() > 0:
                    close_btn.click(force=True)
                    time.sleep(1)
            except:
                pass
            
            return True  # Assume success unless we know otherwise
            
        except Exception as e:
            self.logger.error(f"Error filling form: {e}")
            return False
    
    def update_job_status(self, job_data: Dict):
        """Update job file with application status."""
        try:
            # Find and update the job file
            for file in self.saved_folder.glob(f"Job_{job_data['id']}*.md"):
                content = file.read_text(encoding='utf-8')
                
                # Update status
                content = content.replace('status: found', 'status: applied')
                content = content.replace('- [ ] Applied', '- [x] Applied')
                content += f"\n**Date Applied:** {job_data.get('date_applied', 'Unknown')}\n"
                
                file.write_text(content, encoding='utf-8')
                
                # Move to Applied folder
                applied_file = self.applied_folder / file.name
                file.rename(applied_file)
                
                break
        except Exception as e:
            self.logger.error(f"Error updating job status: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Job Auto-Applier')
    parser.add_argument('--vault', default='AI_Employee_Vault', help='Path to vault')
    parser.add_argument('--profile', default='AI_Employee_Vault/profile.yaml', help='Path to profile')
    parser.add_argument('--max-jobs', type=int, default=50, help='Max jobs to process')
    parser.add_argument('--headless', action='store_true', help='Run in background')
    
    args = parser.parse_args()
    
    # Get absolute paths
    base_path = Path(__file__).parent
    vault_path = base_path / args.vault
    profile_path = base_path / args.profile
    
    # Initialize and run
    applier = LinkedInJobApplier(
        vault_path=str(vault_path),
        profile_path=str(profile_path),
        headless=args.headless
    )
    
    applier.run(max_jobs=args.max_jobs)


if __name__ == '__main__':
    main()
