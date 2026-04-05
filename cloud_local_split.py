"""
Cloud/Local Split Architecture Implementation

This module implements the Platinum tier Cloud/Local split:
- Cloud owns: Email triage + draft replies + social post drafts/scheduling (draft-only)
- Local owns: Approvals, WhatsApp session, payments/banking, final "send/post" actions

Agents communicate by writing files into synced folders with claim-by-move coordination.
"""

import os
import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class AgentIdentity:
    """Represents an AI agent instance"""
    agent_id: str
    agent_type: str  # "cloud" or "local"
    domains: List[str]  # Domains this agent owns
    created_at: str
    last_heartbeat: Optional[str] = None
    status: str = "active"  # active, inactive, error


@dataclass
class TaskItem:
    """Represents a task in the system"""
    task_id: str
    domain: str
    source: str  # email, whatsapp, finance, social_media
    created_at: str
    status: str  # pending, claimed, in_progress, completed, rejected
    claimed_by: Optional[str] = None
    claimed_at: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict] = None


class ClaimByMoveRule:
    """
    Implements the claim-by-move rule for multi-agent coordination.
    
    First agent to move an item from /Needs_Action to /In_Progress/<agent>/ owns it.
    Other agents must ignore claimed tasks.
    """
    
    def __init__(self, vault_path: Path, agent_id: str):
        self.vault_path = Path(vault_path)
        self.agent_id = agent_id
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.in_progress_path = self.vault_path / "In_Progress"
        self.agent_path = self.in_progress_path / agent_id
        
        # Ensure directories exist
        self.needs_action_path.mkdir(parents=True, exist_ok=True)
        self.in_progress_path.mkdir(parents=True, exist_ok=True)
        self.agent_path.mkdir(parents=True, exist_ok=True)
    
    def claim_task(self, task_file: Path) -> bool:
        """
        Attempt to claim a task by moving it to agent's In_Progress folder.
        
        Returns True if successfully claimed, False if already claimed by another agent.
        """
        if not task_file.exists():
            return False
        
        # Check if file has a claim marker
        content = task_file.read_text()
        if 'claimed_by:' in content:
            # Already claimed by someone else
            import re
            claim_match = re.search(r'claimed_by:\s*(\S+)', content)
            if claim_match and claim_match.group(1) != self.agent_id:
                logger.info(f"Task {task_file.name} already claimed by {claim_match.group(1)}")
                return False
        
        try:
            # Add claim marker
            if '---' in content:
                # Insert into frontmatter
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    frontmatter = parts[1]
                    frontmatter += f"\nclaimed_by: {self.agent_id}\nclaimed_at: {datetime.now().isoformat()}\n"
                    content = f"---{frontmatter}---{parts[2] if len(parts) > 2 else ''}"
            else:
                # Add frontmatter
                frontmatter = f"""---
claimed_by: {self.agent_id}
claimed_at: {datetime.now().isoformat()}
---

"""
                content = frontmatter + content
            
            # Move file to agent's In_Progress folder
            dest = self.agent_path / task_file.name
            dest.write_text(content)
            task_file.unlink()  # Remove original
            
            logger.info(f"Agent {self.agent_id} claimed task: {task_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error claiming task {task_file.name}: {e}")
            return False
    
    def release_task(self, task_file: Path, reason: str = "unable_to_complete") -> bool:
        """Release a claimed task back to Needs_Action"""
        if not task_file.exists():
            return False
        
        try:
            content = task_file.read_text()
            
            # Remove claim markers
            import re
            content = re.sub(r'\nclaimed_by:.*', '', content)
            content = re.sub(r'\nclaimed_at:.*', '', content)
            
            # Move back to Needs_Action
            dest = self.needs_action_path / task_file.name
            dest.write_text(content)
            task_file.unlink()
            
            logger.info(f"Agent {self.agent_id} released task: {task_file.name} ({reason})")
            return True
            
        except Exception as e:
            logger.error(f"Error releasing task {task_file.name}: {e}")
            return False
    
    def get_available_tasks(self, domain: Optional[str] = None) -> List[Path]:
        """Get list of unclaimed tasks in Needs_Action"""
        available = []
        
        if not self.needs_action_path.exists():
            return available
        
        for task_file in self.needs_action_path.glob("*.md"):
            content = task_file.read_text()
            
            # Skip if already claimed
            if 'claimed_by:' in content:
                continue
            
            # Filter by domain if specified
            if domain:
                if f'domain: {domain}' not in content:
                    continue
            
            available.append(task_file)
        
        return available
    
    def get_my_tasks(self) -> List[Path]:
        """Get tasks claimed by this agent"""
        if not self.agent_path.exists():
            return []
        
        return list(self.agent_path.glob("*.md"))


class VaultSyncManager:
    """
    Manages vault synchronization between Cloud and Local instances.
    
    Uses Git for synchronization (Phase 1).
    Only markdown/state files sync. Secrets never sync.
    """
    
    def __init__(
        self,
        vault_path: Path,
        instance_type: str,  # "cloud" or "local"
        git_remote: Optional[str] = None,
        sync_interval: int = 60
    ):
        self.vault_path = Path(vault_path)
        self.instance_type = instance_type
        self.git_remote = git_remote
        self.sync_interval = sync_interval
        
        # Directories that should NOT sync (contain secrets)
        self.no_sync_dirs = [
            '.env',
            '.whatsapp_session',
            '.linkedin_session',
            '.linkedin_jobs_session',
            'credentials',
            'secrets',
            '.git'
        ]
        
        # Directories that sync (markdown/state only)
        self.sync_dirs = [
            'Needs_Action',
            'In_Progress',
            'Pending_Approval',
            'Approved',
            'Rejected',
            'Done',
            'Plans',
            'Briefings',
            'Accounting',
            'Logs',
            'Updates',  # Cloud writes here
            'Signals'   # Cloud writes here
        ]
        
        # Single-writer rule for Dashboard.md (Local only)
        self.dashboard_file = self.vault_path / "Dashboard.md"
    
    def initialize_git_sync(self) -> bool:
        """Initialize Git repository for vault sync"""
        try:
            # Check if already initialized
            git_dir = self.vault_path / ".git"
            if not git_dir.exists():
                # Initialize git
                self._run_git("init")
                self._run_git("config", "user.email", f"ai-employee-{self.instance_type}@local")
                self._run_git("config", "user.name", f"AI Employee ({self.instance_type.title()})")
                
                # Create .gitignore
                gitignore_content = """# Secrets - NEVER sync these
.env
*.key
*.pem
credentials/
secrets/

# Session files
.whatsapp_session/
.linkedin_session/
.linkedin_jobs_session/

# OS files
.DS_Store
Thumbs.db
"""
                gitignore_file = self.vault_path / ".gitignore"
                if not gitignore_file.exists():
                    gitignore_file.write_text(gitignore_content)
                
                # Initial commit
                self._run_git("add", ".")
                self._run_git("commit", "-m", f"Initial vault setup ({self.instance_type})")
            
            # Add remote if specified
            if self.git_remote:
                try:
                    self._run_git("remote", "get-url", "origin")
                except:
                    self._run_git("remote", "add", "origin", self.git_remote)
            
            logger.info(f"Git sync initialized for {self.instance_type} instance")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing git sync: {e}")
            return False
    
    def sync_to_remote(self) -> bool:
        """Push changes to remote (Cloud or Local)"""
        try:
            # Stage changes
            self._run_git("add", "-A")
            
            # Check if there are changes
            status = self._run_git("status", "--porcelain")
            if not status.strip():
                logger.debug("No changes to sync")
                return True
            
            # Commit
            self._run_git("commit", "-m", f"Auto-sync ({self.instance_type}): {datetime.now().isoformat()}")
            
            # Push
            if self.git_remote:
                self._run_git("push", "origin", "main", "--force-with-lease")
            
            logger.info(f"Synced to remote ({self.instance_type})")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing to remote: {e}")
            return False
    
    def sync_from_remote(self) -> bool:
        """Pull changes from remote"""
        try:
            if self.git_remote:
                # Fetch first
                self._run_git("fetch", "origin")
                
                # Check for conflicts
                self._run_git("merge", "--no-commit", "origin/main", check=False)
                
                # If there are conflicts, prefer ours for Dashboard.md (Local wins)
                dashboard_file = self.vault_path / "Dashboard.md"
                if self.instance_type == "local" and dashboard_file.exists():
                    # Local always wins for Dashboard.md
                    self._run_git("checkout", "--ours", "Dashboard.md")
            
            logger.info(f"Synced from remote ({self.instance_type})")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing from remote: {e}")
            return False
    
    def run_sync_cycle(self):
        """Run a complete sync cycle (pull -> commit -> push)"""
        # Pull first
        self.sync_from_remote()
        
        # Commit and push
        self.sync_to_remote()
    
    def _run_git(self, *args, check: bool = True) -> str:
        """Run git command and return output"""
        cmd = ["git", "-C", str(self.vault_path)] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout
    
    def write_update(self, domain: str, update_type: str, data: Dict) -> Path:
        """
        Write an update file to /Updates/ or /Signals/
        Cloud writes updates, Local merges them into Dashboard.md
        """
        updates_path = self.vault_path / "Updates"
        updates_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        update_file = updates_path / f"{domain}_{update_type}_{timestamp}.md"
        
        content = f"""---
type: update
domain: {domain}
update_type: {update_type}
timestamp: {datetime.now().isoformat()}
source: {self.instance_type}
---

# {update_type.replace('_', ' ').title()} Update

```json
{json.dumps(data, indent=2)}
```
"""
        update_file.write_text(content)
        return update_file


class CloudLocalOrchestrator:
    """
    Orchestrates the Cloud/Local split architecture.
    
    Domain Ownership:
    - Cloud: Email triage + draft replies + social post drafts/scheduling
    - Local: Approvals, WhatsApp session, payments/banking, final send/post
    
    Communication: File-based via synced vault
    """
    
    def __init__(
        self,
        vault_path: Path,
        instance_type: str,
        agent_id: str,
        git_remote: Optional[str] = None
    ):
        self.vault_path = Path(vault_path)
        self.instance_type = instance_type
        self.agent_id = agent_id
        
        # Initialize components
        self.claim_rule = ClaimByMoveRule(vault_path, agent_id)
        self.sync_manager = VaultSyncManager(vault_path, instance_type, git_remote)
        
        # Domain ownership
        self.cloud_domains = ["email", "social_media", "linkedin"]
        self.local_domains = ["whatsapp", "payments", "banking", "approvals"]
        
        # Pending approval path
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.pending_approval_path.mkdir(parents=True, exist_ok=True)
    
    def can_execute_action(self, action_type: str, action_data: Dict) -> bool:
        """
        Check if this instance can execute the action.
        
        Cloud can only draft (never send/post).
        Local can approve and execute.
        """
        if self.instance_type == "cloud":
            # Cloud can only draft
            if action_type in ["draft_email", "draft_social_post", "schedule_post"]:
                return True
            # Cloud cannot send/post
            elif action_type in ["send_email", "post_social", "send_whatsapp"]:
                return False
            # Cloud cannot do payments
            elif action_type in ["payment", "bank_transfer"]:
                return False
        
        elif self.instance_type == "local":
            # Local can do everything (after approval)
            return True
        
        return False
    
    def create_draft_action(self, action_type: str, action_data: Dict) -> Path:
        """Create a draft action file (Cloud creates, Local approves/executes)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if action_type in ["draft_email", "draft_social_post"]:
            # Cloud creates drafts in Pending_Approval
            draft_file = self.pending_approval_path / f"DRAFT_{action_type}_{timestamp}.md"
        else:
            draft_file = self.pending_approval_path / f"{action_type}_{timestamp}.md"
        
        content = f"""---
type: {action_type}
source: {self.instance_type}
created: {datetime.now().isoformat()}
status: pending_approval
---

# {action_type.replace('_', ' ').title()}

## Action Details
```json
{json.dumps(action_data, indent=2)}
```

## Approval Required
Move this file to /Approved to execute.
Move to /Rejected to cancel.
"""
        draft_file.write_text(content)
        logger.info(f"Created draft action: {draft_file}")
        return draft_file
    
    def process_pending_approvals(self):
        """Process pending approval files (Local only)"""
        if self.instance_type != "local":
            return
        
        if not self.pending_approval_path.exists():
            return
        
        for approval_file in self.pending_approval_path.glob("*.md"):
            content = approval_file.read_text()
            
            # Check if this was created by Cloud
            if 'source: cloud' in content:
                logger.info(f"Cloud-created approval found: {approval_file.name}")
                # Local can now review and user will move to Approved/Rejected
    
    def run_sync_and_process(self):
        """Run sync cycle and process tasks"""
        # Sync vault
        self.sync_manager.run_sync_cycle()
        
        # Get available tasks for this agent's domains
        if self.instance_type == "cloud":
            domains = self.cloud_domains
        else:
            domains = self.local_domains
        
        for domain in domains:
            available_tasks = self.claim_rule.get_available_tasks(domain=domain)
            
            for task_file in available_tasks:
                # Try to claim
                if self.claim_rule.claim_task(task_file):
                    logger.info(f"Claimed task: {task_file.name}")
                    # Process task here
                    # (Integration with existing watchers/orchestrator)
    
    def get_status(self) -> Dict:
        """Get current status of Cloud/Local split"""
        return {
            "instance_type": self.instance_type,
            "agent_id": self.agent_id,
            "domains": self.cloud_domains if self.instance_type == "cloud" else self.local_domains,
            "available_tasks": len(self.claim_rule.get_available_tasks()),
            "my_tasks": len(self.claim_rule.get_my_tasks()),
            "pending_approvals": len(list(self.pending_approval_path.glob("*.md")))
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cloud/Local Split Architecture")
    parser.add_argument("--vault-path", required=True, help="Path to Obsidian vault")
    parser.add_argument("--instance-type", required=True, choices=["cloud", "local"], help="Instance type")
    parser.add_argument("--agent-id", required=True, help="Unique agent ID")
    parser.add_argument("--git-remote", help="Git remote URL for sync")
    parser.add_argument("--init-git", action="store_true", help="Initialize git sync")
    parser.add_argument("--sync", action="store_true", help="Run sync cycle")
    parser.add_argument("--status", action="store_true", help="Show status")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    orchestrator = CloudLocalOrchestrator(
        vault_path=Path(args.vault_path),
        instance_type=args.instance_type,
        agent_id=args.agent_id,
        git_remote=args.git_remote
    )
    
    if args.init_git:
        orchestrator.sync_manager.initialize_git_sync()
    
    if args.sync:
        orchestrator.run_sync_and_process()
    
    if args.status:
        status = orchestrator.get_status()
        print(json.dumps(status, indent=2))
