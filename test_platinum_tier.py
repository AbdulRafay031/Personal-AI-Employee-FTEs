"""
Platinum Tier Test Suite

Comprehensive test suite for validating all Platinum tier components.

Usage:
    python test_platinum_tier.py --vault-path /path/to/vault
    python test_platinum_tier.py --vault-path /path/to/vault --test-all
    python test_platinum_tier.py --vault-path /path/to/vault --test RalphWiggumLoop
"""

import os
import sys
import json
import time
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "watchers"))

from ralph_wiggum_loop import RalphWiggumLoop, RalphTask
from finance_watcher import FinanceWatcher, Transaction
from ceo_briefing_generator import CEOBriefingGenerator
from cloud_local_split import CloudLocalOrchestrator, ClaimByMoveRule, VaultSyncManager
from health_monitor import HealthMonitor, ProcessManager
from audit_logger import AuditLogger, AuditLogEntry, ActionType, ActionResult


class TestRalphWiggumLoop(unittest.TestCase):
    """Test Ralph Wiggum persistence loop"""
    
    def setUp(self):
        """Create temporary vault for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.test_dir)
        (self.vault_path / "Done").mkdir()
        (self.vault_path / "Needs_Action").mkdir()
        (self.vault_path / "In_Progress").mkdir()
        self.loop = RalphWiggumLoop(self.vault_path)
    
    def tearDown(self):
        """Cleanup temporary vault"""
        # Close any logging handlers that might be holding files open
        import logging
        for handler in logging.root.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logging.root.removeHandler(handler)
        
        # Small delay to ensure file handles are released on Windows
        import time
        time.sleep(0.5)
        
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_create_task(self):
        """Test task creation"""
        task_id = self.loop.create_task(
            prompt="Test task",
            max_iterations=5,
            completion_promise="TASK_COMPLETE"
        )
        self.assertIsNotNone(task_id)
        
        task = self.loop.load_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task.prompt, "Test task")
        self.assertEqual(task.max_iterations, 5)
        self.assertEqual(task.status, "pending")
    
    def test_task_completion_via_promise(self):
        """Test task completion via promise"""
        task_id = self.loop.create_task(
            prompt="Test task",
            max_iterations=5,
            completion_promise="TASK_COMPLETE"
        )
        
        # Simulate Claude output without completion
        is_complete = self.loop.run_iteration(task_id, "Working on it...")
        self.assertFalse(is_complete)
        
        # Simulate Claude output with completion
        is_complete = self.loop.run_iteration(task_id, "Done! TASK_COMPLETE")
        self.assertTrue(is_complete)
        
        task = self.loop.load_task(task_id)
        self.assertEqual(task.status, "completed")
    
    def test_max_iterations(self):
        """Test max iterations enforcement"""
        task_id = self.loop.create_task(
            prompt="Test task",
            max_iterations=3,
            completion_promise="TASK_COMPLETE"
        )
        
        # Run 3 iterations without completion
        for i in range(3):
            self.loop.run_iteration(task_id, f"Iteration {i+1}")
        
        # Should be marked as max_iterations_reached
        task = self.loop.load_task(task_id)
        self.assertEqual(task.status, "max_iterations_reached")
    
    def test_should_continue(self):
        """Test should_continue logic"""
        task_id = self.loop.create_task(
            prompt="Test task",
            max_iterations=5,
            completion_promise="TASK_COMPLETE"
        )
        
        self.assertTrue(self.loop.should_continue(task_id))
        
        # Complete the task
        self.loop.run_iteration(task_id, "TASK_COMPLETE")
        self.assertFalse(self.loop.should_continue(task_id))
    
    def test_get_next_prompt(self):
        """Test next prompt generation"""
        task_id = self.loop.create_task(
            prompt="Original prompt",
            max_iterations=10,
            completion_promise="TASK_COMPLETE"
        )
        
        prompt = self.loop.get_next_prompt(task_id)
        self.assertIn("Original prompt", prompt)
        self.assertIn("Iteration 1/10", prompt)
        self.assertIn("TASK_COMPLETE", prompt)


class TestFinanceWatcher(unittest.TestCase):
    """Test Finance/Bank transaction watcher"""
    
    def setUp(self):
        """Create temporary vault for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.test_dir)
        (self.vault_path / "Needs_Action").mkdir()
        (self.vault_path / "Accounting").mkdir()
        
        # Create CSV drop folder
        self.csv_folder = Path(self.test_dir) / "Bank_CSVs"
        self.csv_folder.mkdir()
        
        self.watcher = FinanceWatcher(
            vault_path=self.vault_path,
            mode="csv",
            bank_config={"csv_folder": str(self.csv_folder)}
        )
    
    def tearDown(self):
        """Cleanup temporary vault"""
        # Close any logging handlers that might be holding files open
        import logging
        for handler in logging.root.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logging.root.removeHandler(handler)
        
        # Small delay to ensure file handles are released on Windows
        import time
        time.sleep(0.5)
        
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_parse_csv(self):
        """Test CSV parsing"""
        # Create test CSV
        csv_content = """date,description,amount,balance
2026-04-01,Client Payment,1500.00,5000.00
2026-04-02,Netflix Subscription,-15.99,4984.01
2026-04-03,Office Supplies,-45.50,4938.51
"""
        csv_file = self.csv_folder / "test_bank.csv"
        csv_file.write_text(csv_content)
        
        # Get transactions
        transactions = self.watcher.check_for_updates()
        self.assertEqual(len(transactions), 3)
        
        # Verify first transaction
        txn = transactions[0]
        self.assertEqual(txn.description, "Client Payment")
        self.assertEqual(txn.amount, 1500.00)
    
    def test_categorize_transaction(self):
        """Test transaction categorization"""
        # Income
        txn_income = Transaction(
            transaction_id="test1",
            date="2026-04-01",
            description="Client Payment",
            amount=1500.00,
            balance=5000.00
        )
        category = self.watcher._categorize_transaction(txn_income)
        self.assertEqual(category, "income")
        
        # Subscription
        txn_sub = Transaction(
            transaction_id="test2",
            date="2026-04-02",
            description="NETFLIX.COM Subscription",
            amount=-15.99,
            balance=4984.01
        )
        category = self.watcher._categorize_transaction(txn_sub)
        self.assertIn("Netflix", category)
    
    def test_anomaly_detection(self):
        """Test anomaly detection"""
        # Large transaction (above threshold)
        txn_large = Transaction(
            transaction_id="test3",
            date="2026-04-01",
            description="Large Payment",
            amount=5000.00,
            balance=10000.00
        )
        self.assertTrue(self.watcher._detect_anomaly(txn_large))
        
        # Small transaction (below threshold)
        txn_small = Transaction(
            transaction_id="test4",
            date="2026-04-01",
            description="Small Purchase",
            amount=25.00,
            balance=5000.00
        )
        self.assertFalse(self.watcher._detect_anomaly(txn_small))
    
    def test_monthly_log(self):
        """Test monthly accounting log"""
        txn = Transaction(
            transaction_id="test5",
            date="2026-04-01",
            description="Test Transaction",
            amount=100.00,
            balance=5000.00
        )
        
        self.watcher._log_to_monthly(txn)
        
        # Check file was created
        current_month_file = self.vault_path / "Accounting" / "Current_Month.md"
        self.assertTrue(current_month_file.exists())
        
        content = current_month_file.read_text()
        self.assertIn("Test Transaction", content)
        self.assertIn("$100.00", content)


class TestCEOBriefingGenerator(unittest.TestCase):
    """Test CEO Briefing Generator"""
    
    def setUp(self):
        """Create temporary vault for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.test_dir)
        (self.vault_path / "Briefings").mkdir()
        (self.vault_path / "Accounting").mkdir()
        (self.vault_path / "Done").mkdir()
        (self.vault_path / "Needs_Action").mkdir()
        (self.vault_path / "In_Progress").mkdir()
        (self.vault_path / "Plans").mkdir()
        
        # Create Business_Goals.md
        business_goals = """---
last_updated: 2026-04-01
review_frequency: weekly
---

## Q1 2026 Objectives

### Revenue Target
- Monthly goal: $10,000
- Current MTD: $4,500
"""
        (self.vault_path / "Business_Goals.md").write_text(business_goals)
        
        self.generator = CEOBriefingGenerator(self.vault_path)
    
    def tearDown(self):
        """Cleanup temporary vault"""
        # Close any logging handlers that might be holding files open
        import logging
        for handler in logging.root.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logging.root.removeHandler(handler)
        
        # Small delay to ensure file handles are released on Windows
        import time
        time.sleep(0.5)
        
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_generate_briefing(self):
        """Test briefing generation"""
        briefing_file = self.generator.generate_briefing(period_days=7)
        
        self.assertTrue(briefing_file.exists())
        
        content = briefing_file.read_text(encoding="utf-8")
        self.assertIn("CEO Briefing", content)
        self.assertIn("Revenue", content)
        self.assertIn("Completed Tasks", content)
    
    def test_parse_business_goals(self):
        """Test business goals parsing"""
        goals = self.generator._parse_business_goals()
        self.assertEqual(goals.get('monthly_revenue_target'), 10000.0)


class TestClaimByMoveRule(unittest.TestCase):
    """Test claim-by-move rule implementation"""
    
    def setUp(self):
        """Create temporary vault for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.test_dir)
        (self.vault_path / "Needs_Action").mkdir()
        (self.vault_path / "In_Progress").mkdir()
        
        self.agent1_rule = ClaimByMoveRule(self.vault_path, "agent-1")
        self.agent2_rule = ClaimByMoveRule(self.vault_path, "agent-2")
    
    def tearDown(self):
        """Cleanup temporary vault"""
        # Close any logging handlers that might be holding files open
        import logging
        for handler in logging.root.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logging.root.removeHandler(handler)
        
        # Small delay to ensure file handles are released on Windows
        import time
        time.sleep(0.5)
        
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_claim_task(self):
        """Test task claiming"""
        # Create test task
        task_file = self.vault_path / "Needs_Action" / "test_task.md"
        task_file.write_text("---\ntype: test\n---\n\nTest task")
        
        # Agent 1 claims task
        claimed = self.agent1_rule.claim_task(task_file)
        self.assertTrue(claimed)
        
        # Verify task moved to In_Progress/agent-1
        agent1_path = self.vault_path / "In_Progress" / "agent-1"
        self.assertTrue((agent1_path / "test_task.md").exists())
        self.assertFalse(task_file.exists())
    
    def test_double_claim_prevention(self):
        """Test that double claiming is prevented"""
        # Create test task
        task_file = self.vault_path / "Needs_Action" / "test_task.md"
        task_file.write_text("---\ntype: test\n---\n\nTest task")
        
        # Agent 1 claims task
        self.agent1_rule.claim_task(task_file)
        
        # Agent 2 tries to claim (should fail)
        claimed = self.agent2_rule.claim_task(task_file)
        self.assertFalse(claimed)
    
    def test_get_available_tasks(self):
        """Test getting available tasks"""
        # Create test tasks
        for i in range(3):
            task_file = self.vault_path / "Needs_Action" / f"task_{i}.md"
            task_file.write_text(f"---\ntype: test\n---\n\nTask {i}")
        
        available = self.agent1_rule.get_available_tasks()
        self.assertEqual(len(available), 3)
        
        # Claim one task
        self.agent1_rule.claim_task(available[0])
        
        # Should have 2 available
        available = self.agent1_rule.get_available_tasks()
        self.assertEqual(len(available), 2)


class TestAuditLogger(unittest.TestCase):
    """Test comprehensive audit logging"""
    
    def setUp(self):
        """Create temporary vault for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.test_dir)
        (self.vault_path / "Logs").mkdir()
        
        self.logger = AuditLogger(self.vault_path)
    
    def tearDown(self):
        """Cleanup temporary vault"""
        # Close any logging handlers that might be holding files open
        import logging
        for handler in logging.root.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logging.root.removeHandler(handler)
        
        # Small delay to ensure file handles are released on Windows
        import time
        time.sleep(0.5)
        
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_log_action(self):
        """Test action logging"""
        entry = self.logger.log_action(
            action_type="email_send",
            actor="claude_code",
            target="client@example.com",
            parameters={"subject": "Invoice #123"},
            approval_status="approved",
            approved_by="human",
            result="success"
        )
        
        self.assertIsNotNone(entry)
        self.assertEqual(entry.action_type, "email_send")
        self.assertEqual(entry.result, "success")
        
        # Verify log file was created
        log_file = self.logger._get_log_file(datetime.now())
        self.assertTrue(log_file.exists())
    
    def test_get_logs_for_date(self):
        """Test retrieving logs for a date"""
        # Log some actions
        for i in range(5):
            self.logger.log_action(
                action_type=f"test_action_{i}",
                actor="test_actor",
                target=f"target_{i}",
                parameters={},
                result="success"
            )
        
        logs = self.logger.get_logs_for_date(datetime.now())
        self.assertEqual(len(logs), 5)
    
    def test_search_logs(self):
        """Test log search"""
        # Log some actions
        self.logger.log_action(
            action_type="email_send",
            actor="gmail_watcher",
            target="client@example.com",
            parameters={"subject": "Test"},
            result="success"
        )
        
        self.logger.log_action(
            action_type="email_send",
            actor="gmail_watcher",
            target="other@example.com",
            parameters={"subject": "Other"},
            result="failed",
            error_message="Connection timeout"
        )
        
        # Search by actor
        results = self.logger.search_logs("", actor="gmail_watcher")
        self.assertEqual(len(results), 2)
        
        # Search by query
        results = self.logger.search_logs("client@example.com")
        self.assertEqual(len(results), 1)
        
        # Search failed actions
        results = self.logger.search_logs("", result="failed")
        self.assertEqual(len(results), 1)


class TestHealthMonitor(unittest.TestCase):
    """Test health monitoring system"""
    
    def setUp(self):
        """Create temporary vault for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.test_dir)
        (self.vault_path / "Logs").mkdir()
        
        self.monitor = HealthMonitor(self.vault_path)
    
    def tearDown(self):
        """Cleanup temporary vault"""
        # Close any logging handlers that might be holding files open
        import logging
        for handler in logging.root.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logging.root.removeHandler(handler)
        
        # Small delay to ensure file handles are released on Windows
        import time
        time.sleep(0.5)
        
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_register_process(self):
        """Test process registration"""
        self.monitor.register_process(
            name="test_process",
            command="echo test",
            working_dir=self.vault_path
        )
        
        self.assertIn("test_process", self.monitor.processes)
    
    def test_check_system_health(self):
        """Test system health check"""
        health = self.monitor.check_system_health()
        
        self.assertIsNotNone(health)
        self.assertGreater(health.disk_usage_percent, 0)
        self.assertGreater(health.memory_usage_percent, 0)
        self.assertGreater(health.cpu_usage_percent, 0)
    
    def test_generate_health_dashboard(self):
        """Test health dashboard generation"""
        dashboard_file = self.monitor.generate_health_dashboard()
        
        self.assertTrue(dashboard_file.exists())
        
        content = dashboard_file.read_text(encoding="utf-8")
        self.assertIn("System Health Dashboard", content)
        self.assertIn("System Resources", content)


def run_tests(vault_path: Path, test_all: bool = True, specific_test: str = None):
    """Run test suite"""
    
    print("=" * 60)
    print("  Platinum Tier Test Suite")
    print("=" * 60)
    print()
    
    # Create test loader
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    if test_all:
        # Load all test classes
        test_classes = [
            TestRalphWiggumLoop,
            TestFinanceWatcher,
            TestCEOBriefingGenerator,
            TestClaimByMoveRule,
            TestAuditLogger,
            TestHealthMonitor
        ]
        
        for test_class in test_classes:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
    elif specific_test:
        # Load specific test
        test_class = globals().get(specific_test)
        if test_class and issubclass(test_class, unittest.TestCase):
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        else:
            print(f"Error: Test class '{specific_test}' not found")
            return False
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 60)
    print(f"  Test Results")
    print("=" * 60)
    print(f"  Total: {result.testsRun}")
    print(f"  Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failed: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Platinum Tier Test Suite")
    parser.add_argument("--vault-path", help="Path to vault (for integration tests)")
    parser.add_argument("--test-all", action="store_true", help="Run all tests")
    parser.add_argument("--test", help="Run specific test class")
    
    args = parser.parse_args()
    
    success = run_tests(
        vault_path=Path(args.vault_path) if args.vault_path else None,
        test_all=args.test_all,
        specific_test=args.test
    )
    
    sys.exit(0 if success else 1)
