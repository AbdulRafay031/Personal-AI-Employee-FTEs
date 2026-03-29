"""
Orchestrator Module

Master process for the AI Employee system. Responsibilities:
1. Monitor Needs_Action folder for pending tasks
2. Trigger Qwen Code (via OpenRouter API) to process tasks
3. Monitor Approved folder for human-approved actions
4. Execute approved actions via MCP servers
5. Update Dashboard.md with current status
6. Manage task lifecycle (pending → in_progress → done)

Usage:
    python orchestrator.py /path/to/vault --model qwen-2.5-coder-32b-instruct

Environment Variables (create .env file):
    OPENROUTER_API_KEY=your-api-key
    OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
    QWEN_MODEL=qwen/qwen-2.5-coder-32b-instruct
"""

import os
import sys
import time
import subprocess
import logging
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class TaskStatus:
    """Represents the status of a task file."""
    path: Path
    task_type: str
    priority: str
    created: datetime
    status: str  # pending, in_progress, approved, done


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.

    Coordinates between watchers, Qwen Code (via OpenRouter API), and human approval.
    """

    # Folder structure
    FOLDERS = [
        'Inbox',
        'Needs_Action',
        'In_Progress',
        'Pending_Approval',
        'Approved',
        'Rejected',
        'Done',
        'Plans',
        'Accounting',
        'Briefings',
        'Logs',
    ]

    def __init__(self, vault_path: str, model: str = None):
        """
        Initialize the Orchestrator.

        Args:
            vault_path: Path to Obsidian vault
            model: Qwen model to use for reasoning (default from env or qwen-2.5-coder-32b-instruct)
        """
        self.vault_path = Path(vault_path)
        
        # Get model from parameter or environment
        self.model = model or os.getenv('QWEN_MODEL', 'qwen/qwen-2.5-coder-32b-instruct')
        
        # OpenRouter API configuration
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.site_url = os.getenv('OPENROUTER_SITE_URL', '')
        self.app_name = os.getenv('OPENROUTER_APP_NAME', 'AI Employee FTE')
        
        # Ensure all folders exist
        for folder in self.FOLDERS:
            (self.vault_path / folder).mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

        # Track processed files
        self.processed_files: set = set()

        # Dashboard cache
        self.dashboard_path = self.vault_path / 'Dashboard.md'
        
        # API client (initialized on first use)
        self._api_client = None

        # Log API configuration status
        if self.api_key:
            key_preview = self.api_key[:10] + '...' if len(self.api_key) > 10 else self.api_key
            self.logger.info(f'OpenRouter API configured (key: {key_preview})')
        else:
            self.logger.warning('OpenRouter API key not found. AI automation disabled.')
            self.logger.warning('Create .env file with OPENROUTER_API_KEY or set environment variable')

        self.logger.info(f'Orchestrator initialized for vault: {vault_path}')
        self.logger.info(f'Using model: {self.model}')

    def _setup_logging(self):
        """Setup logging configuration."""
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f'orchestrator_{datetime.now().strftime("%Y%m%d")}.log'

        self.logger = logging.getLogger('Orchestrator')
        self.logger.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def _get_api_client(self):
        """Get or create OpenAI API client configured for OpenRouter."""
        if self._api_client is None:
            try:
                from openai import OpenAI
                self._api_client = OpenAI(
                    base_url=self.api_base_url,
                    api_key=self.api_key,
                    default_headers={
                        "HTTP-Referer": self.site_url,
                        "X-Title": self.app_name,
                    }
                )
            except ImportError:
                self.logger.error('OpenAI package not installed. Run: pip install openai')
                return None
            except Exception as e:
                self.logger.error(f'Failed to create API client: {e}')
                return None
        return self._api_client

    def _parse_frontmatter(self, content: str) -> Dict:
        """Parse YAML frontmatter from markdown content."""
        import re

        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return {}

        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"\'')

        return frontmatter

    def _get_task_files(self, folder: str) -> List[TaskStatus]:
        """
        Get all task files in a folder with their metadata.

        Args:
            folder: Folder name to scan

        Returns:
            List of TaskStatus objects
        """
        folder_path = self.vault_path / folder
        if not folder_path.exists():
            return []

        tasks = []
        for file_path in folder_path.glob('*.md'):
            try:
                content = file_path.read_text(encoding='utf-8')
                frontmatter = self._parse_frontmatter(content)

                tasks.append(TaskStatus(
                    path=file_path,
                    task_type=frontmatter.get('type', 'unknown'),
                    priority=frontmatter.get('priority', 'medium'),
                    created=datetime.fromisoformat(frontmatter.get('created', datetime.now().isoformat())),
                    status=folder.lower()
                ))
            except Exception as e:
                self.logger.error(f'Error reading {file_path}: {e}')

        return tasks

    def _update_dashboard(self):
        """Update Dashboard.md with current status."""
        try:
            # Count tasks in each folder
            needs_action = len(list((self.vault_path / 'Needs_Action').glob('*.md')))
            in_progress = len(list((self.vault_path / 'In_Progress').glob('*.md')))
            pending_approval = len(list((self.vault_path / 'Pending_Approval').glob('*.md')))

            # Count completed today
            done_folder = self.vault_path / 'Done'
            today = datetime.now().strftime('%Y-%m-%d')
            completed_today = 0
            for f in done_folder.glob('*.md'):
                try:
                    content = f.read_text()
                    fm = self._parse_frontmatter(content)
                    if today in fm.get('completed', ''):
                        completed_today += 1
                except Exception:
                    pass

            # Get recent activity
            recent_activity = []
            for folder in ['Done', 'Approved', 'Rejected']:
                folder_path = self.vault_path / folder
                for f in sorted(folder_path.glob('*.md'), reverse=True)[:5]:
                    try:
                        content = f.read_text()
                        fm = self._parse_frontmatter(content)
                        recent_activity.append({
                            'time': fm.get('completed', fm.get('created', 'Unknown')),
                            'task': f.stem,
                            'status': folder
                        })
                    except Exception:
                        pass

            # Update dashboard
            if self.dashboard_path.exists():
                content = self.dashboard_path.read_text(encoding='utf-8')

                # Update status table
                import re
                new_status = f'''| **Pending Tasks** | {needs_action} |
| **In Progress** | {in_progress} |
| **Awaiting Approval** | {pending_approval} |
| **Completed Today** | {completed_today} |'''

                content = re.sub(
                    r'\| \*\*Pending Tasks\*\* \|.*?\| \*\*Completed Today\*\* \|.*?\n',
                    new_status + '\n',
                    content,
                    flags=re.DOTALL
                )

                # Update recent activity table
                activity_rows = '\n'.join([
                    f"| {a['time'][:19]} | {a['task'][:40]} | {a['status']} |"
                    for a in recent_activity[:5]
                ])
                if not activity_rows:
                    activity_rows = '| - | - | - |'

                content = re.sub(
                    r'(\| Time \| Task \| Status \|\n\|------\|------\|--------\|\n).*?(\n---)',
                    f'\\1{activity_rows}\\2',
                    content,
                    flags=re.DOTALL
                )

                # Update timestamp
                content = re.sub(
                    r'last_updated:.*',
                    f'last_updated: {datetime.now().isoformat()}',
                    content
                )

                self.dashboard_path.write_text(content, encoding='utf-8')
                self.logger.debug('Dashboard updated')

        except Exception as e:
            self.logger.error(f'Failed to update dashboard: {e}')

    def _trigger_qwen_api(self, prompt: str) -> bool:
        """
        Trigger Qwen Code via OpenRouter API to process tasks.

        Args:
            prompt: Prompt to give Qwen

        Returns:
            True if successful, False otherwise
        """
        if not self.api_key:
            self.logger.warning('API key not configured. Cannot trigger Qwen Code.')
            self.logger.info('To enable AI automation:')
            self.logger.info('  1. Get API key from https://openrouter.ai/keys')
            self.logger.info('  2. Create .env file with OPENROUTER_API_KEY=your-key')
            return False

        try:
            client = self._get_api_client()
            if not client:
                return False

            self.logger.info(f'Sending request to Qwen ({self.model})...')

            # System prompt for AI Employee behavior
            system_prompt = '''You are an AI Employee assistant managing tasks in an Obsidian vault.

Your responsibilities:
1. Read task files from the Needs_Action folder
2. Create Plan.md files for complex multi-step tasks
3. Request approval for sensitive actions:
   - Payments > $100
   - Payments to new vendors
   - Sending emails to new contacts
   - Any irreversible actions
4. Move completed tasks to the Done folder
5. Update Dashboard.md with current status
6. Follow rules in Company_Handbook.md

Always be helpful, thorough, and cautious with sensitive operations.'''

            # Call OpenRouter API
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
            )

            # Get response content
            assistant_message = response.choices[0].message.content
            
            # Log the response (first 500 chars)
            response_preview = assistant_message[:500] + '...' if len(assistant_message) > 500 else assistant_message
            self.logger.info(f'Qwen response received ({len(assistant_message)} chars)')
            self.logger.debug(f'Response preview: {response_preview}')

            # Note: In a full implementation, you would parse the response
            # and execute the suggested actions. For Bronze tier, we just
            # log that the API call was successful.
            
            self.logger.info('Qwen Code processed tasks successfully via OpenRouter API')
            return True

        except Exception as e:
            self.logger.error(f'Failed to trigger Qwen Code: {e}')
            return False

    def _execute_approved_action(self, approval_file: Path) -> bool:
        """
        Execute an approved action.

        Args:
            approval_file: Path to approval file in Approved folder

        Returns:
            True if successful, False otherwise
        """
        try:
            content = approval_file.read_text(encoding='utf-8')
            frontmatter = self._parse_frontmatter(content)

            action_type = frontmatter.get('action', 'unknown')

            self.logger.info(f'Executing approved action: {action_type}')

            # For Bronze tier, we just log the action and move to Done
            # Silver/Gold tiers would integrate with MCP servers here

            # Log the action
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action_type': action_type,
                'actor': 'orchestrator',
                'file': str(approval_file),
                'result': 'success'
            }

            log_file = self.vault_path / 'Logs' / f'{datetime.now().strftime("%Y-%m-%d")}.jsonl'
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

            # Move to Done
            done_path = self.vault_path / 'Done' / approval_file.name
            shutil.move(str(approval_file), str(done_path))

            self.logger.info(f'Action completed: {approval_file.name}')
            return True

        except Exception as e:
            self.logger.error(f'Failed to execute action: {e}')
            return False

    def process_needs_action(self):
        """Process all files in Needs_Action folder."""
        tasks = self._get_task_files('Needs_Action')

        if not tasks:
            return

        self.logger.info(f'Processing {len(tasks)} tasks from Needs_Action')

        # Build prompt for Qwen Code
        task_list = '\n'.join([f"- {t.path.name} ({t.task_type}, {t.priority})" for t in tasks])

        prompt = f'''I have {len(tasks)} tasks in the Needs_Action folder that need processing:

{task_list}

Please:
1. Read each task file
2. Create a Plan.md for complex multi-step tasks
3. Request approval for any sensitive actions (payments, new contacts)
4. Move completed tasks to the Done folder
5. Update the Dashboard.md

Remember to follow the rules in Company_Handbook.md.'''

        # Trigger Qwen Code via API
        self._trigger_qwen_api(prompt)

        # Update dashboard
        self._update_dashboard()

    def process_approved(self):
        """Process all files in Approved folder."""
        approved_files = list((self.vault_path / 'Approved').glob('*.md'))

        for approval_file in approved_files:
            self._execute_approved_action(approval_file)

        if approved_files:
            self._update_dashboard()

    def run(self, check_interval: int = 60):
        """
        Main run loop.

        Args:
            check_interval: Seconds between checks
        """
        self.logger.info(f'Starting Orchestrator (interval: {check_interval}s)')

        try:
            while True:
                try:
                    # Process pending tasks
                    self.process_needs_action()

                    # Execute approved actions
                    self.process_approved()

                    # Update dashboard
                    self._update_dashboard()

                except Exception as e:
                    self.logger.error(f'Error in orchestration loop: {e}', exc_info=True)

                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            raise


def main():
    """Main entry point for Orchestrator."""
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument(
        '--model',
        default=None,
        help='Qwen model to use (default from env or qwen-2.5-coder-32b-instruct)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (for testing)'
    )

    args = parser.parse_args()

    orchestrator = Orchestrator(args.vault_path, args.model)

    if args.once:
        # Run once for testing
        orchestrator.process_needs_action()
        orchestrator.process_approved()
        orchestrator._update_dashboard()
    else:
        # Run continuously
        orchestrator.run(args.interval)


if __name__ == '__main__':
    main()
