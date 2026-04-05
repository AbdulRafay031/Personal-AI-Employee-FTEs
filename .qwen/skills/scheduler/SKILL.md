# Scheduling/Cron Integration Skill

Schedule recurring tasks for your AI Employee using cron (Linux/Mac) or Task Scheduler (Windows). Automate daily briefings, weekly audits, and periodic task processing.

## Overview

This skill enables your AI Employee to:
- Schedule recurring task processing
- Automate daily/weekly briefings
- Run periodic health checks
- Execute time-sensitive operations
- Manage scheduled task queue

## Architecture

```
System Scheduler (cron/Task Scheduler)
        ↓
Triggers orchestrator.py with specific flags
        ↓
Executes scheduled tasks:
├── Daily Briefing (8:00 AM)
├── Task Processing (every hour)
├── Weekly Audit (Sunday 10:00 PM)
└── Health Check (every 15 minutes)
```

## Scheduling Options

### Option 1: Cron (Linux/Mac)

Best for: Server deployments, always-on machines

### Option 2: Windows Task Scheduler

Best for: Windows desktop deployments

### Option 3: Python APScheduler

Best for: Cross-platform, no system dependencies

### Option 4: Systemd Timers (Linux)

Best for: Modern Linux distributions

## Cron Setup (Linux/Mac)

### Basic Cron Configuration

```bash
# Edit crontab
crontab -e

# Add scheduled tasks
```

### Example Crontab

```bash
# AI Employee Scheduled Tasks

# Environment variables
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
PYTHONPATH=/path/to/Personal-AI-Employee-FTEs

# Process tasks every hour
0 * * * * cd /path/to/Personal-AI-Employee-FTEs && /usr/bin/python3 orchestrator.py /path/to/vault --once >> /path/to/vault/Logs/cron_orchestrator.log 2>&1

# Daily briefing at 8:00 AM
0 8 * * * cd /path/to/Personal-AI-Employee-FTEs && /usr/bin/python3 skills/plan_generator.py /path/to/vault --auto-generate >> /path/to/vault/Logs/cron_plans.log 2>&1

# Execute approved actions every 15 minutes
*/15 * * * * cd /path/to/Personal-AI-Employee-FTEs && /usr/bin/python3 skills/approval_workflow.py /path/to/vault --execute-approved >> /path/to/vault/Logs/cron_approvals.log 2>&1

# Weekly audit on Sunday at 10:00 PM
0 22 * * 0 cd /path/to/Personal-AI-Employee-FTEs && /usr/bin/python3 skills/weekly_audit.py /path/to/vault >> /path/to/vault/Logs/cron_audit.log 2>&1

# Health check every 5 minutes
*/5 * * * * cd /path/to/Personal-AI-Employee-FTEs && /usr/bin/python3 skills/health_check.py /path/to/vault >> /path/to/vault/Logs/cron_health.log 2>&1

# LinkedIn post check at 9:00 AM on weekdays
0 9 * * 1-5 cd /path/to/Personal-AI-Employee-FTEs && /usr/bin/python3 skills/linkedin_poster.py /path/to/vault --action scheduled-post >> /path/to/vault/Logs/cron_linkedin.log 2>&1
```

### Cron Syntax Reference

```
* * * * * command
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7, Sunday=0 or 7)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

### Special Cron Strings

| String | Meaning | Equivalent |
|--------|---------|------------|
| `@hourly` | Every hour | `0 * * * *` |
| `@daily` | Every day at midnight | `0 0 * * *` |
| `@weekly` | Every week on Sunday | `0 0 * * 0` |
| `@monthly` | First of every month | `0 0 1 * *` |

## Windows Task Scheduler Setup

### PowerShell Script for Task Creation

```powershell
# Create-ScheduledTasks.ps1

$vaultPath = "C:\path\to\vault"
$projectPath = "C:\path\to\Personal-AI-Employee-FTEs"
$pythonExe = "C:\Python311\python.exe"

# Task 1: Process tasks every hour
$action = New-ScheduledTaskAction -Execute $pythonExe `
  -Argument "orchestrator.py $vaultPath --once" `
  -WorkingDirectory $projectPath
$trigger = New-ScheduledTaskTrigger -Once (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "AI Employee - Hourly Processing" `
  -Action $action -Trigger $trigger -Principal $principal `
  -Description "Process AI Employee tasks every hour"

# Task 2: Daily briefing at 8:00 AM
$action = New-ScheduledTaskAction -Execute $pythonExe `
  -Argument "skills/plan_generator.py $vaultPath --auto-generate" `
  -WorkingDirectory $projectPath
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
Register-ScheduledTask -TaskName "AI Employee - Daily Briefing" `
  -Action $action -Trigger $trigger `
  -Description "Generate daily briefing at 8 AM"

# Task 3: Execute approved actions every 15 minutes
$action = New-ScheduledTaskAction -Execute $pythonExe `
  -Argument "skills/approval_workflow.py $vaultPath --execute-approved" `
  -WorkingDirectory $projectPath
$trigger = New-ScheduledTaskTrigger -Once (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName "AI Employee - Approval Execution" `
  -Action $action -Trigger $trigger `
  -Description "Execute approved actions every 15 minutes"

# Task 4: Weekly audit on Sunday at 10:00 PM
$action = New-ScheduledTaskAction -Execute $pythonExe `
  -Argument "skills/weekly_audit.py $vaultPath" `
  -WorkingDirectory $projectPath
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 10:00PM
Register-ScheduledTask -TaskName "AI Employee - Weekly Audit" `
  -Action $action -Trigger $trigger `
  -Description "Weekly business audit on Sunday 10 PM"

Write-Host "Scheduled tasks created successfully!"
```

### Run PowerShell Script

```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\Create-ScheduledTasks.ps1

# Verify tasks
Get-ScheduledTask | Where-Object {$_.TaskName -like "AI Employee*"}
```

## Python APScheduler (Cross-Platform)

### Installation

```bash
pip install apscheduler
```

### Basic Scheduler Script

```python
# scheduler.py
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import subprocess
import sys
from pathlib import Path

# Configuration
VAULT_PATH = "/path/to/vault"
PROJECT_PATH = "/path/to/Personal-AI-Employee-FTEs"
PYTHON = sys.executable

def run_command(script: str, args: str = ""):
    """Run a Python script."""
    cmd = f"{PYTHON} {PROJECT_PATH}/{script} {VAULT_PATH} {args}"
    subprocess.run(cmd.split(), cwd=PROJECT_PATH)

# Create scheduler
sched = BlockingScheduler()

# Add jobs
sched.add_job(
    run_command,
    CronTrigger(minute=0),  # Every hour
    args=['orchestrator.py', '--once'],
    id='hourly_processing',
    name='Hourly Task Processing'
)

sched.add_job(
    run_command,
    CronTrigger(hour=8, minute=0),  # Daily at 8 AM
    args=['skills/plan_generator.py', '--auto-generate'],
    id='daily_briefing',
    name='Daily Briefing'
)

sched.add_job(
    run_command,
    IntervalTrigger(minutes=15),  # Every 15 minutes
    args=['skills/approval_workflow.py', '--execute-approved'],
    id='approval_execution',
    name='Execute Approved Actions'
)

sched.add_job(
    run_command,
    CronTrigger(day_of_week='sun', hour=22, minute=0),  # Sunday 10 PM
    args=['skills/weekly_audit.py'],
    id='weekly_audit',
    name='Weekly Audit'
)

print("Scheduler started. Press Ctrl+C to stop.")
sched.start()
```

### Run Scheduler

```bash
# Run in foreground
python scheduler.py

# Run as daemon (Linux)
nohup python scheduler.py > /var/log/ai_employee_scheduler.log 2>&1 &

# Run as Windows service (using NSSM)
nssm install AI_Employee_Scheduler "python" "C:\path\to\scheduler.py"
nssm start AI_Employee_Scheduler
```

## Systemd Timers (Linux)

### Service Unit

```ini
# /etc/systemd/system/ai-employee.service
[Unit]
Description=AI Employee Task Processor
After=network.target

[Service]
Type=oneshot
User=youruser
WorkingDirectory=/path/to/Personal-AI-Employee-FTEs
ExecStart=/usr/bin/python3 orchestrator.py /path/to/vault --once
Environment="PYTHONPATH=/path/to/Personal-AI-Employee-FTEs"
```

### Timer Unit

```ini
# /etc/systemd/system/ai-employee.timer
[Unit]
Description=Run AI Employee every hour
Requires=ai-employee.service

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

### Enable Timer

```bash
# Copy unit files
sudo cp ai-employee.service /etc/systemd/system/
sudo cp ai-employee.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start timer
sudo systemctl enable ai-employee.timer
sudo systemctl start ai-employee.timer

# Check status
sudo systemctl list-timers | grep ai-employee
```

## Scheduled Task Types

### 1. Daily Briefing (8:00 AM)

Generates daily summary of:
- Pending tasks
- Completed tasks (yesterday)
- Today's priorities
- Alerts/notifications

```bash
0 8 * * * python3 skills/daily_briefing.py /vault
```

### 2. Hourly Task Processing

Processes new tasks from:
- Needs_Action folder
- Email inbox
- WhatsApp messages
- File drops

```bash
0 * * * * python3 orchestrator.py /vault --once
```

### 3. Approval Execution (Every 15 minutes)

Executes approved actions:
- Send emails
- Process payments
- Post social media
- File operations

```bash
*/15 * * * * python3 skills/approval_workflow.py /vault --execute-approved
```

### 4. Weekly Audit (Sunday 10:00 PM)

Generates weekly report:
- Revenue summary
- Expense breakdown
- Task completion rate
- Bottleneck analysis
- Next week priorities

```bash
0 22 * * 0 python3 skills/weekly_audit.py /vault
```

### 5. Health Check (Every 5 minutes)

Monitors system health:
- Watcher processes running
- Disk space
- API connectivity
- Error rate

```bash
*/5 * * * * python3 skills/health_check.py /vault
```

### 6. Social Media Posting (Weekdays 9:00 AM)

Posts scheduled content:
- LinkedIn posts
- Twitter updates
- Facebook updates

```bash
0 9 * * 1-5 python3 skills/linkedin_poster.py /vault --action scheduled-post
```

## Task Calendar

### Weekly Schedule

| Time | Monday | Tuesday | Wednesday | Thursday | Friday | Saturday | Sunday |
|------|--------|---------|-----------|----------|--------|----------|--------|
| 8:00 AM | Daily Briefing | Daily Briefing | Daily Briefing | Daily Briefing | Daily Briefing | - | - |
| 9:00 AM | LinkedIn Post | LinkedIn Post | LinkedIn Post | LinkedIn Post | LinkedIn Post | - | - |
| Every Hour | Task Processing | Task Processing | Task Processing | Task Processing | Task Processing | Task Processing | Task Processing |
| 10:00 PM | - | - | - | - | - | - | Weekly Audit |

## Configuration File

### Schedule Configuration

Create `config/schedule_config.yaml`:

```yaml
# Schedule Configuration

schedules:
  daily_briefing:
    enabled: true
    cron: "0 8 * * *"
    timezone: "America/New_York"
    script: "skills/daily_briefing.py"
    args: ["--include-metrics"]

  hourly_processing:
    enabled: true
    cron: "0 * * * *"
    script: "orchestrator.py"
    args: ["--once", "--auto-retry"]

  approval_execution:
    enabled: true
    interval: "*/15 * * * *"
    script: "skills/approval_workflow.py"
    args: ["--execute-approved"]

  weekly_audit:
    enabled: true
    cron: "0 22 * * 0"
    script: "skills/weekly_audit.py"
    args: ["--generate-briefing"]

  health_check:
    enabled: true
    interval: "*/5 * * * *"
    script: "skills/health_check.py"
    args: ["--notify-on-error"]

  linkedin_post:
    enabled: true
    cron: "0 9 * * 1-5"
    script: "skills/linkedin_poster.py"
    args: ["--action", "scheduled-post"]

notifications:
  on_failure: true
  on_success: false
  channels:
    - email
    - whatsapp
  recipients:
    - human@example.com
```

## Monitoring Scheduled Tasks

### Task Execution Log

```markdown
# Scheduled Task Execution Log - January 2026

## Daily Briefing

| Date | Time | Status | Duration | Notes |
|------|------|--------|----------|-------|
| Jan 7 | 8:00 AM | ✅ Success | 2.3s | Generated 5 tasks |
| Jan 6 | 8:00 AM | ✅ Success | 1.8s | Generated 3 tasks |

## Hourly Processing

| Hour | Tasks Processed | Plans Created | Errors |
|------|-----------------|---------------|--------|
| 10:00 | 5 | 3 | 0 |
| 9:00 | 2 | 1 | 0 |

## Weekly Audit

| Week | Revenue | Expenses | Tasks Completed | Issues |
|------|---------|----------|-----------------|--------|
| Week 1 | $4,500 | $1,200 | 45 | None |
```

### Monitoring Script

```python
# monitor_schedules.py
from pathlib import Path
from datetime import datetime

def check_task_execution(log_file: Path, task_name: str):
    """Check if scheduled task executed."""
    if not log_file.exists():
        return f"❌ {task_name}: No log file"
    
    content = log_file.read_text()
    last_execution = content.split('\n')[-10:]
    
    if not last_execution:
        return f"❌ {task_name}: No executions found"
    
    return f"✅ {task_name}: Last execution OK"

# Check all tasks
tasks = [
    ('Logs/cron_orchestrator.log', 'Hourly Processing'),
    ('Logs/cron_plans.log', 'Daily Briefing'),
    ('Logs/cron_approvals.log', 'Approval Execution'),
]

for log_file, task_name in tasks:
    print(check_task_execution(Path(log_file), task_name))
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not running | Check cron syntax, verify paths are absolute |
| Permission denied | Run crontab as correct user, check file permissions |
| Python not found | Use full path to Python executable |
| Task runs but fails | Check logs, verify environment variables |
| Duplicate executions | Ensure only one scheduler is active |
| Missed executions | Check system timezone, verify cron daemon running |

### Debug Cron Issues

```bash
# Check cron daemon status
sudo systemctl status cron

# View cron logs
grep CRON /var/log/syslog

# Test script manually
cd /path/to/Personal-AI-Employee-FTEs
python3 orchestrator.py /path/to/vault --once

# Check crontab
crontab -l

# View cron logs for specific task
grep "orchestrator" /var/log/syslog
```

### Debug Windows Task Scheduler

```powershell
# View task history
Get-ScheduledTaskInfo -TaskName "AI Employee - Hourly Processing"

# Run task manually
Start-ScheduledTask -TaskName "AI Employee - Hourly Processing"

# View task logs
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" | 
  Where-Object {$_.Message -like "*AI Employee*"} | 
  Select-Object -First 20
```

## Best Practices

### For Reliable Scheduling

1. **Use absolute paths** - Don't rely on relative paths
2. **Set environment variables** - PYTHONPATH, vault path, etc.
3. **Log everything** - Capture stdout and stderr
4. **Handle failures gracefully** - Don't crash on single task failure
5. **Monitor execution** - Set up alerts for missed tasks
6. **Test before deploying** - Run manually first
7. **Document schedule** - Keep schedule_config.yaml updated

### Error Handling

```python
# In scheduled scripts
import sys
import logging
from pathlib import Path

def main():
    try:
        # Task logic here
        pass
    except Exception as e:
        logging.error(f"Scheduled task failed: {e}")
        sys.exit(1)
    finally:
        # Always log completion
        logging.info("Scheduled task completed")

if __name__ == '__main__':
    main()
```

## Related Skills

- **plan-generator:** Daily briefing generation
- **approval-workflow:** Approval execution
- **weekly-audit:** Weekly business review
- **health-check:** System monitoring

## Next Steps

After setting up scheduling:
1. Choose scheduler (cron, Task Scheduler, or APScheduler)
2. Configure basic tasks (hourly processing, daily briefing)
3. Set up logging and monitoring
4. Test each scheduled task manually
5. Enable scheduling and monitor for 24 hours
6. Add advanced tasks (weekly audit, social posting)

---

*Skill Version: 1.0.0*
*Compatible with: Silver Tier AI Employee*
*Last Updated: 2026-01-07*
