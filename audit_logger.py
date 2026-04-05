"""
Comprehensive Audit Logging System

Logs every action the AI Employee takes for review and compliance.
Implements required log format from the blueprint specification.

Features:
- JSONL structured logging
- Action categorization and tracking
- Approval status tracking
- Actor identification (which agent/component)
- Result logging
- 90-day retention minimum
- Audit trail generation
- Compliance reporting

Usage:
    from audit_logger import AuditLogger
    
    logger = AuditLogger(vault_path="/path/to/vault")
    logger.log_action(
        action_type="email_send",
        actor="claude_code",
        target="client@example.com",
        parameters={"subject": "Invoice #123"},
        approval_status="approved",
        approved_by="human",
        result="success"
    )
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions that can be logged"""
    EMAIL_SEND = "email_send"
    EMAIL_DRAFT = "email_draft"
    EMAIL_REPLY = "email_reply"
    EMAIL_FORWARD = "email_forward"
    WHATSAPP_SEND = "whatsapp_send"
    WHATSAPP_REPLY = "whatsapp_reply"
    SOCIAL_POST = "social_post"
    SOCIAL_SCHEDULE = "social_schedule"
    PAYMENT_INITIATE = "payment_initiate"
    PAYMENT_APPROVE = "payment_approve"
    PAYMENT_EXECUTE = "payment_execute"
    FILE_CREATE = "file_create"
    FILE_READ = "file_read"
    FILE_DELETE = "file_delete"
    FILE_MOVE = "file_move"
    TASK_CLAIM = "task_claim"
    TASK_RELEASE = "task_release"
    TASK_COMPLETE = "task_complete"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_GRANT = "approval_grant"
    APPROVAL_REJECT = "approval_reject"
    SYNC_PUSH = "sync_push"
    SYNC_PULL = "sync_pull"
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    SYSTEM_RESTART = "system_restart"
    WATCHER_TRIGGER = "watcher_trigger"
    BRIEFING_GENERATE = "briefing_generate"
    CONFIG_CHANGE = "config_change"
    ERROR_OCCURRED = "error_occurred"


class ApprovalStatus(Enum):
    """Approval status for actions requiring human review"""
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ActionResult(Enum):
    """Result of an action"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class AuditLogEntry:
    """Represents a single audit log entry"""
    timestamp: str
    action_type: str
    actor: str
    target: str
    parameters: Dict[str, Any]
    approval_status: str
    approved_by: Optional[str]
    result: str
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class AuditLogger:
    """
    Comprehensive audit logger for AI Employee.
    
    Every action must be logged for:
    - Compliance and auditing
    - Debugging and troubleshooting
    - Performance analysis
    - Security monitoring
    - Weekly CEO briefings
    """
    
    def __init__(
        self,
        vault_path: Path,
        retention_days: int = 90,
        max_file_size_mb: int = 100
    ):
        self.vault_path = Path(vault_path)
        self.logs_path = self.vault_path / "Logs"
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        self.retention_days = retention_days
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        
        # Current log file (one per day)
        self.current_log_file = self._get_log_file(datetime.now())
    
    def log_action(
        self,
        action_type: str,
        actor: str,
        target: str,
        parameters: Dict[str, Any],
        approval_status: str = "not_required",
        approved_by: Optional[str] = None,
        result: str = "success",
        error_message: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLogEntry:
        """
        Log an action taken by the AI Employee.
        
        Args:
            action_type: Type of action (see ActionType enum)
            actor: Who/what performed the action (e.g., "claude_code", "gmail_watcher")
            target: Target of the action (e.g., email address, file path)
            parameters: Action parameters
            approval_status: Approval status (see ApprovalStatus enum)
            approved_by: Who approved the action (if applicable)
            result: Result of the action (see ActionResult enum)
            error_message: Error message if action failed
            duration_seconds: How long the action took
            metadata: Additional metadata
        """
        entry = AuditLogEntry(
            timestamp=datetime.now().isoformat(),
            action_type=action_type,
            actor=actor,
            target=target,
            parameters=parameters,
            approval_status=approval_status,
            approved_by=approved_by,
            result=result,
            error_message=error_message,
            duration_seconds=duration_seconds,
            metadata=metadata
        )
        
        # Write to log file
        self._write_entry(entry)
        
        # Log to Python logger as well
        log_level = logging.ERROR if result == "failed" else logging.INFO
        logger.log(
            log_level,
            f"ACTION: {action_type} by {actor} -> {target} ({result})"
        )
        
        return entry
    
    def _get_log_file(self, date: datetime) -> Path:
        """Get log file path for a specific date"""
        date_str = date.strftime("%Y-%m-%d")
        return self.logs_path / f"{date_str}.jsonl"
    
    def _write_entry(self, entry: AuditLogEntry):
        """Write a log entry to the current day's log file"""
        log_file = self._get_log_file(datetime.now())
        
        # Check file size and rotate if needed
        if log_file.exists() and log_file.stat().st_size > self.max_file_size_bytes:
            self._rotate_log_file(log_file)
        
        # Append entry
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(entry)) + '\n')
    
    def _rotate_log_file(self, log_file: Path):
        """Rotate a log file when it exceeds max size"""
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = log_file.with_name(f"{log_file.stem}_{timestamp}.jsonl")
        log_file.rename(backup_file)
        
        logger.info(f"Rotated log file: {log_file} -> {backup_file}")
    
    def get_logs_for_date(self, date: datetime) -> List[AuditLogEntry]:
        """Get all log entries for a specific date"""
        log_file = self._get_log_file(date)
        entries = []
        
        if not log_file.exists():
            return entries
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    entries.append(AuditLogEntry(**data))
                except:
                    logger.warning(f"Failed to parse log entry: {line}")
        
        return entries
    
    def get_logs_for_period(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[AuditLogEntry]:
        """Get all log entries for a date range"""
        entries = []
        current = start_date
        
        while current <= end_date:
            entries.extend(self.get_logs_for_date(current))
            current += timedelta(days=1)
        
        return entries
    
    def get_logs_by_actor(self, actor: str, days: int = 7) -> List[AuditLogEntry]:
        """Get all logs for a specific actor"""
        start_date = datetime.now() - timedelta(days=days)
        all_logs = self.get_logs_for_period(start_date, datetime.now())
        return [log for log in all_logs if log.actor == actor]
    
    def get_logs_by_action_type(
        self,
        action_type: str,
        days: int = 7
    ) -> List[AuditLogEntry]:
        """Get all logs for a specific action type"""
        start_date = datetime.now() - timedelta(days=days)
        all_logs = self.get_logs_for_period(start_date, datetime.now())
        return [log for log in all_logs if log.action_type == action_type]
    
    def get_failed_actions(self, days: int = 7) -> List[AuditLogEntry]:
        """Get all failed actions"""
        start_date = datetime.now() - timedelta(days=days)
        all_logs = self.get_logs_for_period(start_date, datetime.now())
        return [log for log in all_logs if log.result == "failed"]
    
    def get_pending_approvals(self) -> List[AuditLogEntry]:
        """Get all actions pending approval"""
        # Check last 7 days for pending approvals
        start_date = datetime.now() - timedelta(days=7)
        all_logs = self.get_logs_for_period(start_date, datetime.now())
        return [log for log in all_logs if log.approval_status == "pending"]
    
    def generate_audit_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Generate a comprehensive audit report"""
        logs = self.get_logs_for_period(start_date, end_date)
        
        # Calculate statistics
        total_actions = len(logs)
        successful = sum(1 for log in logs if log.result == "success")
        failed = sum(1 for log in logs if log.result == "failed")
        
        # Actions by type
        actions_by_type = {}
        for log in logs:
            actions_by_type[log.action_type] = actions_by_type.get(log.action_type, 0) + 1
        
        # Actions by actor
        actions_by_actor = {}
        for log in logs:
            actions_by_actor[log.actor] = actions_by_actor.get(log.actor, 0) + 1
        
        # Approval statistics
        approvals_pending = sum(1 for log in logs if log.approval_status == "pending")
        approvals_granted = sum(1 for log in logs if log.approval_status == "approved")
        approvals_rejected = sum(1 for log in logs if log.approval_status == "rejected")
        
        # Average duration
        durations = [log.duration_seconds for log in logs if log.duration_seconds is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_actions": total_actions,
                "successful": successful,
                "failed": failed,
                "success_rate": (successful / total_actions * 100) if total_actions > 0 else 0
            },
            "actions_by_type": actions_by_type,
            "actions_by_actor": actions_by_actor,
            "approvals": {
                "pending": approvals_pending,
                "granted": approvals_granted,
                "rejected": approvals_rejected
            },
            "performance": {
                "avg_duration_seconds": avg_duration,
                "total_actions_with_duration": len(durations)
            }
        }
        
        return report
    
    def generate_compliance_report(self, days: int = 90) -> Path:
        """Generate a compliance report for auditing"""
        start_date = datetime.now() - timedelta(days=days)
        report = self.generate_audit_report(start_date, datetime.now())
        
        # Add compliance-specific sections
        failed_actions = self.get_failed_actions(days)
        pending_approvals = self.get_pending_approvals()
        
        report_file = self.logs_path / f"compliance_report_{datetime.now().strftime('%Y%m%d')}.md"
        
        content = f"""---
generated: {datetime.now().isoformat()}
period_days: {days}
report_type: compliance
---

# Compliance Report

## Period
{start_date.strftime("%Y-%m-%d")} to {datetime.now().strftime("%Y-%m-%d")}

## Summary
- **Total Actions**: {report['summary']['total_actions']}
- **Successful**: {report['summary']['successful']}
- **Failed**: {report['summary']['failed']}
- **Success Rate**: {report['summary']['success_rate']:.1f}%

## Actions by Type
| Action Type | Count |
|-------------|-------|
"""
        
        for action_type, count in report['actions_by_type'].items():
            content += f"| {action_type} | {count} |\n"
        
        content += """
## Actions by Actor
| Actor | Count |
|-------|-------|
"""
        
        for actor, count in report['actions_by_actor'].items():
            content += f"| {actor} | {count} |\n"
        
        content += f"""
## Approval Statistics
- **Pending**: {report['approvals']['pending']}
- **Granted**: {report['approvals']['granted']}
- **Rejected**: {report['approvals']['rejected']}

## Failed Actions
"""
        
        if failed_actions:
            content += "| Timestamp | Action | Actor | Target | Error |\n"
            content += "|-----------|--------|-------|--------|-------|\n"
            for log in failed_actions[:20]:  # Show last 20
                content += f"| {log.timestamp} | {log.action_type} | {log.actor} | {log.target} | {log.error_message or 'N/A'} |\n"
        else:
            content += "✅ No failed actions in this period.\n"
        
        content += f"""
## Pending Approvals
"""
        
        if pending_approvals:
            content += f"⚠️ {len(pending_approvals)} action(s) awaiting approval\n"
        else:
            content += "✅ All approvals processed.\n"
        
        content += f"""
---
*Generated by Audit Logger v0.1*
"""
        
        report_file.write_text(content)
        return report_file
    
    def cleanup_old_logs(self):
        """Remove log files older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for log_file in self.logs_path.glob("*.jsonl"):
            # Extract date from filename
            try:
                date_str = log_file.stem.split('_')[0]  # Handle rotated files
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff_date:
                    log_file.unlink()
                    logger.info(f"Removed old log file: {log_file}")
            except:
                # If we can't parse the date, skip
                continue
    
    def search_logs(
        self,
        query: str,
        days: int = 30,
        actor: Optional[str] = None,
        action_type: Optional[str] = None,
        result: Optional[str] = None
    ) -> List[AuditLogEntry]:
        """Search logs with filters"""
        start_date = datetime.now() - timedelta(days=days)
        all_logs = self.get_logs_for_period(start_date, datetime.now())
        
        # Apply filters
        filtered = all_logs
        
        if actor:
            filtered = [log for log in filtered if log.actor == actor]
        
        if action_type:
            filtered = [log for log in filtered if log.action_type == action_type]
        
        if result:
            filtered = [log for log in filtered if log.result == result]
        
        if query:
            query_lower = query.lower()
            filtered = [
                log for log in filtered
                if query_lower in log.target.lower() or
                   query_lower in json.dumps(log.parameters).lower() or
                   (log.error_message and query_lower in log.error_message.lower())
            ]
        
        return filtered


# Context manager for timing actions
class TimedAction:
    """Context manager for logging timed actions"""
    
    def __init__(
        self,
        audit_logger: AuditLogger,
        action_type: str,
        actor: str,
        target: str,
        parameters: Dict,
        approval_status: str = "not_required"
    ):
        self.audit_logger = audit_logger
        self.action_type = action_type
        self.actor = actor
        self.target = target
        self.parameters = parameters
        self.approval_status = approval_status
        self.start_time = None
        self.entry = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is not None:
            # Action failed
            self.entry = self.audit_logger.log_action(
                action_type=self.action_type,
                actor=self.actor,
                target=self.target,
                parameters=self.parameters,
                approval_status=self.approval_status,
                result="failed",
                error_message=str(exc_val),
                duration_seconds=duration
            )
        else:
            # Action succeeded
            self.entry = self.audit_logger.log_action(
                action_type=self.action_type,
                actor=self.actor,
                target=self.target,
                parameters=self.parameters,
                approval_status=self.approval_status,
                result="success",
                duration_seconds=duration
            )
        
        return False  # Don't suppress exceptions


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Audit Logging System")
    parser.add_argument("--vault-path", required=True, help="Path to Obsidian vault")
    parser.add_argument("--report", action="store_true", help="Generate audit report")
    parser.add_argument("--compliance-report", action="store_true", help="Generate compliance report")
    parser.add_argument("--days", type=int, default=7, help="Number of days for report")
    parser.add_argument("--search", help="Search logs")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old logs")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    audit_logger = AuditLogger(Path(args.vault_path))
    
    if args.report:
        start_date = datetime.now() - timedelta(days=args.days)
        report = audit_logger.generate_audit_report(start_date, datetime.now())
        print(json.dumps(report, indent=2))
    
    if args.compliance_report:
        report_file = audit_logger.generate_compliance_report(args.days)
        print(f"Compliance report generated: {report_file}")
    
    if args.search:
        results = audit_logger.search_logs(args.search, days=args.days)
        print(f"Found {len(results)} matching entries:")
        for entry in results:
            print(json.dumps(asdict(entry), indent=2))
    
    if args.cleanup:
        audit_logger.cleanup_old_logs()
        print("Old logs cleaned up")
