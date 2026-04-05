"""
Ralph Wiggum Persistence Loop Implementation

This module implements the "Ralph Wiggum" pattern: a Stop hook that intercepts
Claude's exit and re-injects the prompt until the task is complete.

How it works:
1. Orchestrator creates state file with task prompt
2. Claude works on task
3. Claude tries to exit
4. Stop hook checks: Is task file in /Done?
5. YES → Allow exit (complete)
6. NO → Block exit, re-inject prompt (loop continues)
7. Repeat until complete or max iterations

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
"""

import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class RalphTask:
    """Represents a task being processed in the Ralph loop"""
    task_id: str
    prompt: str
    created_at: str
    max_iterations: int
    current_iteration: int = 0
    completion_promise: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, failed, max_iterations_reached
    last_output: Optional[str] = None
    error_message: Optional[str] = None


class RalphWiggumLoop:
    """
    Manages the Ralph Wiggum persistence loop for autonomous task completion.
    
    Usage:
        ralph = RalphWiggumLoop(vault_path="/path/to/vault")
        task_id = ralph.create_task(
            prompt="Process all files in /Needs_Action",
            max_iterations=10,
            completion_promise="TASK_COMPLETE"
        )
        
        while not ralph.is_complete(task_id):
            ralph.run_iteration(task_id, claude_output)
            if ralph.should_continue(task_id):
                # Re-inject prompt to Claude
                prompt = ralph.get_next_prompt(task_id)
                claude_input = prompt
            else:
                break
    """
    
    def __init__(self, vault_path: Path, state_file: Optional[Path] = None):
        self.vault_path = Path(vault_path)
        self.state_dir = state_file or self.vault_path / ".ralph_state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.done_path = self.vault_path / "Done"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.in_progress_path = self.vault_path / "In_Progress"
        
    def create_task(
        self,
        prompt: str,
        max_iterations: int = 10,
        completion_promise: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> str:
        """Create a new Ralph loop task"""
        if task_id is None:
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = RalphTask(
            task_id=task_id,
            prompt=prompt,
            created_at=datetime.now().isoformat(),
            max_iterations=max_iterations,
            completion_promise=completion_promise
        )
        
        state_file = self.state_dir / f"{task_id}.json"
        state_file.write_text(json.dumps(asdict(task), indent=2))
        
        logger.info(f"Created Ralph task: {task_id}")
        return task_id
    
    def load_task(self, task_id: str) -> Optional[RalphTask]:
        """Load task state from disk"""
        state_file = self.state_dir / f"{task_id}.json"
        if not state_file.exists():
            return None
        
        data = json.loads(state_file.read_text())
        return RalphTask(**data)
    
    def save_task(self, task: RalphTask):
        """Save task state to disk"""
        state_file = self.state_dir / f"{task.task_id}.json"
        state_file.write_text(json.dumps(asdict(task), indent=2))
    
    def is_complete(self, task_id: str) -> bool:
        """Check if task is complete"""
        task = self.load_task(task_id)
        if task is None:
            return True
        
        return task.status in ["completed", "failed", "max_iterations_reached"]
    
    def should_continue(self, task_id: str) -> bool:
        """Determine if the Ralph loop should continue"""
        task = self.load_task(task_id)
        if task is None:
            return False
        
        # Check if task is already complete
        if task.status in ["completed", "failed", "max_iterations_reached"]:
            return False
        
        # Check if we've hit max iterations
        if task.current_iteration >= task.max_iterations:
            task.status = "max_iterations_reached"
            self.save_task(task)
            logger.warning(f"Task {task_id} reached max iterations ({task.max_iterations})")
            return False
        
        # Check if completion promise is met in last output
        if task.completion_promise and task.last_output:
            if task.completion_promise in task.last_output:
                task.status = "completed"
                self.save_task(task)
                logger.info(f"Task {task_id} completed (promise met)")
                return False
        
        return True
    
    def run_iteration(self, task_id: str, claude_output: str) -> bool:
        """
        Run one iteration of the Ralph loop.
        
        Returns True if task is complete, False if we should continue.
        """
        task = self.load_task(task_id)
        if task is None:
            logger.error(f"Task {task_id} not found")
            return True
        
        task.current_iteration += 1
        task.last_output = claude_output
        
        # Check if we've hit max iterations
        if task.current_iteration >= task.max_iterations:
            task.status = "max_iterations_reached"
            self.save_task(task)
            logger.warning(f"Task {task_id} reached max iterations ({task.max_iterations})")
            return True
        
        # Check for completion promise FIRST
        if task.completion_promise and task.completion_promise in claude_output:
            task.status = "completed"
            self.save_task(task)
            logger.info(f"Task {task_id} completed on iteration {task.current_iteration}")
            return True
        
        # Only set to in_progress if not complete
        task.status = "in_progress"
        
        # Check if task file moved to Done
        if self._check_task_in_done(task_id):
            task.status = "completed"
            self.save_task(task)
            logger.info(f"Task {task_id} completed (file in Done)")
            return True
        
        self.save_task(task)
        return False
    
    def get_next_prompt(self, task_id: str) -> str:
        """Get the next prompt to inject into Claude"""
        task = self.load_task(task_id)
        if task is None:
            return ""
        
        return f"""
[RALPH WIGGUM LOOP - Iteration {task.current_iteration + 1}/{task.max_iterations}]

Previous task prompt:
{task.prompt}

Your previous output did not indicate completion.
Please continue working on this task.

If you have completed the task, output: {task.completion_promise or 'TASK_COMPLETE'}

Continue now:
"""
    
    def _check_task_in_done(self, task_id: str) -> bool:
        """Check if task file has been moved to Done folder"""
        # Check if any file in Done folder contains the task_id
        if not self.done_path.exists():
            return False
        
        for done_file in self.done_path.glob("**/*"):
            if done_file.is_file() and task_id in done_file.read_text():
                return True
        
        return False
    
    def fail_task(self, task_id: str, error_message: str):
        """Mark a task as failed"""
        task = self.load_task(task_id)
        if task:
            task.status = "failed"
            task.error_message = error_message
            self.save_task(task)
            logger.error(f"Task {task_id} failed: {error_message}")
    
    def get_task_stats(self) -> dict:
        """Get statistics for all Ralph tasks"""
        tasks = []
        for state_file in self.state_dir.glob("*.json"):
            try:
                data = json.loads(state_file.read_text())
                tasks.append(RalphTask(**data))
            except:
                continue
        
        return {
            "total": len(tasks),
            "completed": sum(1 for t in tasks if t.status == "completed"),
            "failed": sum(1 for t in tasks if t.status == "failed"),
            "in_progress": sum(1 for t in tasks if t.status == "in_progress"),
            "max_iterations_reached": sum(1 for t in tasks if t.status == "max_iterations_reached")
        }


class RalphWiggumClaudePlugin:
    """
    Claude Code plugin that implements the Ralph Wiggum Stop hook.
    
    This plugin intercepts Claude's exit and re-injects the prompt
    until the task is complete.
    
    Installation:
    1. Copy this file to ~/.config/claude-code/plugins/ralph-wiggum.py
    2. Configure in Claude Code settings
    """
    
    def __init__(self, vault_path: Path):
        self.loop = RalphWiggumLoop(vault_path)
        self.current_task_id = None
    
    def on_stop(self, claude_output: str) -> dict:
        """
        Called when Claude tries to exit.
        
        Returns:
            dict with 'block_exit' (bool) and 'reinject_prompt' (str)
        """
        if not self.current_task_id:
            return {"block_exit": False, "reinject_prompt": ""}
        
        # Run one iteration check
        is_complete = self.loop.run_iteration(self.current_task_id, claude_output)
        
        if is_complete:
            # Allow Claude to exit
            self.current_task_id = None
            return {"block_exit": False, "reinject_prompt": ""}
        else:
            # Block exit and re-inject prompt
            next_prompt = self.loop.get_next_prompt(self.current_task_id)
            return {"block_exit": True, "reinject_prompt": next_prompt}
    
    def start_task(self, prompt: str, max_iterations: int = 10, completion_promise: str = "TASK_COMPLETE"):
        """Start a new Ralph loop task"""
        self.current_task_id = self.loop.create_task(
            prompt=prompt,
            max_iterations=max_iterations,
            completion_promise=completion_promise
        )
        return self.current_task_id


# CLI Interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ralph Wiggum Persistence Loop")
    parser.add_argument("--vault-path", required=True, help="Path to Obsidian vault")
    parser.add_argument("--create-task", help="Create a new task")
    parser.add_argument("--max-iterations", type=int, default=10, help="Max iterations")
    parser.add_argument("--completion-promise", default="TASK_COMPLETE", help="Completion promise string")
    parser.add_argument("--check-task", help="Check if task is complete")
    parser.add_argument("--stats", action="store_true", help="Show task statistics")
    
    args = parser.parse_args()
    
    loop = RalphWiggumLoop(Path(args.vault_path))
    
    if args.create_task:
        task_id = loop.create_task(
            prompt=args.create_task,
            max_iterations=args.max_iterations,
            completion_promise=args.completion_promise
        )
        print(f"Created task: {task_id}")
    
    elif args.check_task:
        task = loop.load_task(args.check_task)
        if task:
            print(f"Task: {task.task_id}")
            print(f"Status: {task.status}")
            print(f"Iteration: {task.current_iteration}/{task.max_iterations}")
            print(f"Complete: {loop.is_complete(args.check_task)}")
    
    elif args.stats:
        stats = loop.get_task_stats()
        print(json.dumps(stats, indent=2))
