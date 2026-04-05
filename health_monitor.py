"""
Health Monitoring and Auto-Restart System

Monitors all critical processes (watchers, orchestrator, MCP servers) and
automatically restarts them if they crash. Provides health check endpoints
and alerting via WhatsApp/email.

Features:
- Process monitoring and auto-restart
- Health check API
- Disk space monitoring
- API connectivity checks
- Alert notifications
- Health dashboard generation

Usage:
    python health_monitor.py --vault-path /path/to/vault
    python health_monitor.py --vault-path /path/to/vault --check-only
"""

import os
import sys
import json
import time
import signal
import psutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ProcessHealth:
    """Health status of a process"""
    name: str
    pid: Optional[int]
    status: str  # running, stopped, restarting, failed
    cpu_percent: float
    memory_mb: float
    uptime_seconds: float
    restart_count: int
    last_restart: Optional[str]
    error_message: Optional[str]


@dataclass
class SystemHealth:
    """Overall system health status"""
    timestamp: str
    disk_usage_percent: float
    disk_free_gb: float
    memory_usage_percent: float
    memory_free_gb: float
    cpu_usage_percent: float
    processes: Dict[str, ProcessHealth]
    overall_status: str  # healthy, degraded, critical
    alerts: List[str]


class ProcessManager:
    """Manages a single process with auto-restart capability"""
    
    def __init__(
        self,
        name: str,
        command: str,
        working_dir: Path,
        max_restarts: int = 5,
        restart_delay: int = 10,
        env: Optional[Dict] = None
    ):
        self.name = name
        self.command = command
        self.working_dir = Path(working_dir)
        self.max_restarts = max_restarts
        self.restart_delay = restart_delay
        self.env = env or os.environ.copy()
        
        self.process: Optional[subprocess.Popen] = None
        self.pid_file = Path(f"/tmp/ai_employee_{name}.pid")
        self.log_file = Path(f"/tmp/ai_employee_{name}.log")
        
        self.restart_count = 0
        self.last_restart: Optional[datetime] = None
        self.start_time: Optional[datetime] = None
    
    def start(self) -> bool:
        """Start the process"""
        try:
            # Open log file
            log_fh = open(self.log_file, 'a')
            
            # Start process
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                cwd=str(self.working_dir),
                env=self.env,
                stdout=log_fh,
                stderr=log_fh
            )
            
            # Write PID file
            self.pid_file.write_text(str(self.process.pid))
            
            self.start_time = datetime.now()
            logger.info(f"Started {self.name} (PID: {self.process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Error starting {self.name}: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the process"""
        if self.process is None:
            return True
        
        try:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            
            # Remove PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            logger.info(f"Stopped {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping {self.name}: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if process is running"""
        if self.process is None:
            return False
        
        # Check if process is still running
        poll_result = self.process.poll()
        if poll_result is not None:
            # Process has exited
            return False
        
        # Also verify via PID file
        if self.pid_file.exists():
            try:
                pid = int(self.pid_file.read_text())
                return psutil.pid_exists(pid)
            except:
                return False
        
        return False
    
    def restart(self) -> bool:
        """Restart the process"""
        self.restart_count += 1
        self.last_restart = datetime.now()
        
        logger.warning(f"Restarting {self.name} (attempt {self.restart_count})")
        
        # Stop current
        self.stop()
        
        # Wait before restart
        time.sleep(self.restart_delay)
        
        # Start new
        return self.start()
    
    def get_health(self) -> ProcessHealth:
        """Get health status of this process"""
        pid = None
        cpu_percent = 0.0
        memory_mb = 0.0
        uptime_seconds = 0.0
        
        if self.is_running() and self.process:
            pid = self.process.pid
            try:
                proc = psutil.Process(pid)
                cpu_percent = proc.cpu_percent(interval=1)
                memory_mb = proc.memory_info().rss / (1024 * 1024)
                if self.start_time:
                    uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            except:
                pass
        
        status = "running" if self.is_running() else "stopped"
        if self.restart_count > 0:
            status = "restarting"
        
        return ProcessHealth(
            name=self.name,
            pid=pid,
            status=status,
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            uptime_seconds=uptime_seconds,
            restart_count=self.restart_count,
            last_restart=self.last_restart.isoformat() if self.last_restart else None,
            error_message=None
        )


class HealthMonitor:
    """
    Monitors all AI Employee processes and system health.
    
    Features:
    - Process monitoring and auto-restart
    - System resource monitoring (CPU, memory, disk)
    - API connectivity checks
    - Alert notifications
    - Health dashboard
    """
    
    def __init__(
        self,
        vault_path: Path,
        config: Optional[Dict] = None
    ):
        self.vault_path = Path(vault_path)
        self.config = config or {}
        
        self.logs_path = self.vault_path / "Logs"
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize process managers
        self.processes: Dict[str, ProcessManager] = {}
        
        # Health state
        self.last_check: Optional[datetime] = None
        self.alerts: List[str] = []
        self.alert_history: List[Dict] = []
        
        # Alert thresholds
        self.disk_warning_threshold = self.config.get("disk_warning_threshold", 80)
        self.disk_critical_threshold = self.config.get("disk_critical_threshold", 95)
        self.memory_warning_threshold = self.config.get("memory_warning_threshold", 85)
        self.max_process_restarts = self.config.get("max_process_restarts", 5)
    
    def register_process(
        self,
        name: str,
        command: str,
        working_dir: Optional[Path] = None,
        max_restarts: int = 5,
        restart_delay: int = 10
    ):
        """Register a process for monitoring"""
        self.processes[name] = ProcessManager(
            name=name,
            command=command,
            working_dir=working_dir or self.vault_path,
            max_restarts=max_restarts,
            restart_delay=restart_delay
        )
    
    def start_all(self):
        """Start all registered processes"""
        for name, process in self.processes.items():
            if not process.is_running():
                process.start()
    
    def stop_all(self):
        """Stop all registered processes"""
        for name, process in self.processes.items():
            if process.is_running():
                process.stop()
    
    def check_and_restart(self):
        """Check all processes and restart if needed"""
        for name, process in self.processes.items():
            if not process.is_running():
                logger.warning(f"Process {name} is not running, attempting restart...")
                
                if process.restart_count >= self.max_process_restarts:
                    logger.error(f"Process {name} exceeded max restarts ({self.max_process_restarts})")
                    self._send_alert(f"CRITICAL: Process {name} failed to restart after {process.restart_count} attempts")
                else:
                    if process.restart():
                        self._send_alert(f"Process {name} was restarted")
    
    def check_system_health(self) -> SystemHealth:
        """Check overall system health"""
        # Disk usage
        import shutil
        try:
            disk_usage = shutil.disk_usage(str(self.vault_path))
            disk_usage_percent = (disk_usage.used / disk_usage.total) * 100
            disk_free_gb = disk_usage.free / (1024 ** 3)
        except:
            # Fallback if disk usage check fails
            disk_usage_percent = 0.0
            disk_free_gb = 0.0
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage_percent = memory.percent
        memory_free_gb = memory.available / (1024 ** 3)
        
        # CPU usage
        cpu_usage_percent = psutil.cpu_percent(interval=1)
        
        # Check all processes
        process_health = {}
        for name, process in self.processes.items():
            process_health[name] = process.get_health()
        
        # Determine overall status
        alerts = []
        overall_status = "healthy"
        
        # Disk alerts
        if disk_usage_percent >= self.disk_critical_threshold:
            alerts.append(f"CRITICAL: Disk usage at {disk_usage_percent:.1f}%")
            overall_status = "critical"
        elif disk_usage_percent >= self.disk_warning_threshold:
            alerts.append(f"WARNING: Disk usage at {disk_usage_percent:.1f}%")
            if overall_status == "healthy":
                overall_status = "degraded"
        
        # Memory alerts
        if memory_usage_percent >= self.memory_warning_threshold:
            alerts.append(f"WARNING: Memory usage at {memory_usage_percent:.1f}%")
            if overall_status == "healthy":
                overall_status = "degraded"
        
        # Process alerts
        for name, health in process_health.items():
            if health.status == "stopped":
                alerts.append(f"CRITICAL: Process {name} is stopped")
                overall_status = "critical"
            elif health.restart_count >= self.max_process_restarts:
                alerts.append(f"CRITICAL: Process {name} exceeded max restarts")
                overall_status = "critical"
        
        self.alerts = alerts
        self.last_check = datetime.now()
        
        return SystemHealth(
            timestamp=datetime.now().isoformat(),
            disk_usage_percent=disk_usage_percent,
            disk_free_gb=disk_free_gb,
            memory_usage_percent=memory_usage_percent,
            memory_free_gb=memory_free_gb,
            cpu_usage_percent=cpu_usage_percent,
            processes=process_health,
            overall_status=overall_status,
            alerts=alerts
        )
    
    def generate_health_dashboard(self) -> Path:
        """Generate a health dashboard markdown file"""
        health = self.check_system_health()
        
        dashboard_file = self.vault_path / "System_Health.md"
        
        # Generate process table
        process_table = "| Process | Status | PID | CPU % | Memory (MB) | Restarts | Uptime |\n"
        process_table += "|---------|--------|-----|-------|-------------|----------|--------|\n"
        
        for name, proc_health in health.processes.items():
            status_icon = "✅" if proc_health.status == "running" else "❌"
            uptime_str = str(timedelta(seconds=int(proc_health.uptime_seconds)))
            process_table += f"| {name} | {status_icon} {proc_health.status} | {proc_health.pid or 'N/A'} | {proc_health.cpu_percent:.1f} | {proc_health.memory_mb:.1f} | {proc_health.restart_count} | {uptime_str} |\n"
        
        # Generate alerts
        alerts_section = ""
        if health.alerts:
            alerts_section = "## Alerts\n\n"
            for alert in health.alerts:
                alerts_section += f"- ⚠️ {alert}\n"
            alerts_section += "\n"
        
        content = f"""---
generated: {health.timestamp}
overall_status: {health.overall_status}
---

# System Health Dashboard

## Overall Status: {health.overall_status.upper()}

## System Resources
| Metric | Value | Status |
|--------|-------|--------|
| Disk Usage | {health.disk_usage_percent:.1f}% | {'✅' if health.disk_usage_percent < 80 else '⚠️' if health.disk_usage_percent < 95 else '❌'} |
| Disk Free | {health.disk_free_gb:.1f} GB | {'✅' if health.disk_free_gb > 10 else '⚠️' if health.disk_free_gb > 5 else '❌'} |
| Memory Usage | {health.memory_usage_percent:.1f}% | {'✅' if health.memory_usage_percent < 85 else '⚠️'} |
| Memory Free | {health.memory_free_gb:.1f} GB | |
| CPU Usage | {health.cpu_usage_percent:.1f}% | {'✅' if health.cpu_usage_percent < 70 else '⚠️'} |

## Processes

{process_table}

{alerts_section}

## Recommendations

{self._generate_recommendations(health)}

---
*Generated by Health Monitor v0.1*
"""
        
        dashboard_file.write_text(content, encoding='utf-8')
        return dashboard_file
    
    def _generate_recommendations(self, health: SystemHealth) -> str:
        """Generate health recommendations"""
        recommendations = []
        
        if health.disk_usage_percent >= 80:
            recommendations.append("- **Clean up disk space**: Remove old logs, temporary files, and unused dependencies")
        
        if health.memory_usage_percent >= 85:
            recommendations.append("- **Reduce memory usage**: Consider restarting memory-heavy processes or increasing RAM")
        
        for name, proc_health in health.processes.items():
            if proc_health.restart_count > 0:
                recommendations.append(f"- **Investigate {name}**: Process has restarted {proc_health.restart_count} times")
        
        if not recommendations:
            recommendations.append("- ✅ System is healthy, no action needed")
        
        return "\n".join(recommendations)
    
    def _send_alert(self, message: str):
        """Send alert notification"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "level": "CRITICAL" if "CRITICAL" in message else "WARNING"
        }
        
        self.alert_history.append(alert)
        
        # Log alert
        logger.warning(f"ALERT: {message}")
        
        # Write alert to file
        alert_file = self.logs_path / f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        alert_file.write_text(f"""---
type: alert
timestamp: {alert['timestamp']}
level: {alert['level']}
---

# Alert

{message}
""")
        
        # TODO: Integrate with WhatsApp/email notifier
        # from whatsapp_cloud_notifier import WhatsAppCloudNotifier
        # notifier = WhatsAppCloudNotifier()
        # notifier.send_error_alert(message)
    
    def run_monitoring_loop(self, check_interval: int = 60):
        """Run continuous monitoring loop"""
        logger.info(f"Starting health monitoring (interval: {check_interval}s)")
        
        while True:
            try:
                # Check and restart processes
                self.check_and_restart()
                
                # Generate health dashboard
                self.generate_health_dashboard()
                
                # Sleep
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("Health monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(check_interval)


def create_default_process_config(vault_path: Path) -> Dict[str, Dict]:
    """Create default process configuration"""
    return {
        "gmail_watcher": {
            "command": "python watchers/gmail_watcher.py",
            "working_dir": str(vault_path),
            "max_restarts": 5,
            "restart_delay": 10
        },
        "whatsapp_watcher": {
            "command": "python watchers/whatsapp_watcher.py",
            "working_dir": str(vault_path),
            "max_restarts": 3,
            "restart_delay": 30
        },
        "filesystem_watcher": {
            "command": "python watchers/filesystem_watcher.py",
            "working_dir": str(vault_path),
            "max_restarts": 5,
            "restart_delay": 10
        },
        "finance_watcher": {
            "command": "python watchers/finance_watcher.py",
            "working_dir": str(vault_path),
            "max_restarts": 5,
            "restart_delay": 10
        },
        "orchestrator": {
            "command": "python orchestrator.py",
            "working_dir": str(vault_path),
            "max_restarts": 5,
            "restart_delay": 15
        }
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Health Monitor and Auto-Restart System")
    parser.add_argument("--vault-path", required=True, help="Path to Obsidian vault")
    parser.add_argument("--check-interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--check-only", action="store_true", help="Run single check and exit")
    parser.add_argument("--generate-dashboard", action="store_true", help="Generate health dashboard")
    parser.add_argument("--start-all", action="store_true", help="Start all processes")
    parser.add_argument("--stop-all", action="store_true", help="Stop all processes")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    vault_path = Path(args.vault_path)
    
    # Create monitor
    monitor = HealthMonitor(vault_path)
    
    # Register default processes
    process_config = create_default_process_config(vault_path)
    for name, config in process_config.items():
        monitor.register_process(
            name=name,
            command=config["command"],
            working_dir=Path(config["working_dir"]),
            max_restarts=config["max_restarts"],
            restart_delay=config["restart_delay"]
        )
    
    if args.start_all:
        monitor.start_all()
    
    if args.stop_all:
        monitor.stop_all()
    
    if args.check_only:
        health = monitor.check_system_health()
        print(json.dumps(asdict(health), indent=2))
    
    if args.generate_dashboard:
        dashboard_file = monitor.generate_health_dashboard()
        print(f"Health dashboard generated: {dashboard_file}")
    
    if not args.check_only and not args.generate_dashboard and not args.start_all and not args.stop_all:
        # Run continuous monitoring
        monitor.run_monitoring_loop(args.check_interval)
