"""
Finance/Bank Transaction Watcher

Monitors bank transactions via CSV import or API polling and logs them
to /Accounting/Current_Month.md for the AI Employee to process.

Supports:
1. CSV file monitoring (drop folder for manual import)
2. Bank API polling (pluggable interface for different banks)
3. Transaction categorization and anomaly detection
4. Monthly accounting log generation

Usage:
    python finance_watcher.py --vault-path /path/to/vault --mode csv
    python finance_watcher.py --vault-path /path/to/vault --mode api --bank-config config.json
"""

import csv
import time
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict

from base_watcher import BaseWatcher

logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    """Represents a bank transaction"""
    transaction_id: str
    date: str
    description: str
    amount: float
    balance: Optional[float]
    category: Optional[str] = None  # income, expense, transfer, subscription
    status: str = "pending"  # pending, categorized, flagged, reconciled
    metadata: Optional[Dict] = None


class BankAPI(ABC):
    """Abstract base class for bank API integrations"""
    
    @abstractmethod
    def get_transactions(self, since: datetime) -> List[Transaction]:
        """Fetch transactions since the given date"""
        pass
    
    @abstractmethod
    def get_balance(self) -> float:
        """Get current account balance"""
        pass


class CSVBankAPI(BankAPI):
    """CSV-based bank API (for manual imports)"""
    
    def __init__(self, csv_folder: Path, date_format: str = "%Y-%m-%d"):
        self.csv_folder = Path(csv_folder)
        self.date_format = date_format
        self.processed_files = set()
        self.processed_hashes = set()
    
    def get_transactions(self, since: datetime) -> List[Transaction]:
        """Read transactions from CSV files in the drop folder"""
        transactions = []
        
        if not self.csv_folder.exists():
            return transactions
        
        for csv_file in self.csv_folder.glob("*.csv"):
            # Skip if already processed
            file_hash = hashlib.md5(csv_file.read_bytes()).hexdigest()
            if csv_file.name in self.processed_files or file_hash in self.processed_hashes:
                continue
            
            try:
                transactions.extend(self._parse_csv(csv_file, since))
                self.processed_files.add(csv_file.name)
                self.processed_hashes.add(file_hash)
            except Exception as e:
                logger.error(f"Error parsing {csv_file}: {e}")
        
        return transactions
    
    def _parse_csv(self, csv_file: Path, since: datetime) -> List[Transaction]:
        """Parse a bank CSV file"""
        transactions = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Flexible column mapping
                date_str = row.get('date', row.get('Date', row.get('DATE', '')))
                description = row.get('description', row.get('Description', row.get('DESCRIPTION', '')))
                amount_str = row.get('amount', row.get('Amount', row.get('AMOUNT', '0')))
                balance_str = row.get('balance', row.get('Balance', row.get('BALANCE', '')))
                
                try:
                    date = datetime.strptime(date_str, self.date_format)
                    if date < since:
                        continue
                    
                    amount = float(amount_str.replace(',', '').replace('$', ''))
                    balance = float(balance_str.replace(',', '').replace('$', '')) if balance_str else None
                    
                    # Generate unique transaction ID
                    txn_id = hashlib.md5(
                        f"{date_str}{description}{amount}".encode()
                    ).hexdigest()[:12]
                    
                    transactions.append(Transaction(
                        transaction_id=txn_id,
                        date=date.isoformat(),
                        description=description,
                        amount=amount,
                        balance=balance
                    ))
                except Exception as e:
                    logger.warning(f"Skipping invalid row: {e}")
        
        return transactions
    
    def get_balance(self) -> float:
        """Get balance from latest CSV file"""
        # This would need to be implemented based on your bank's CSV format
        return 0.0


class FinanceWatcher(BaseWatcher):
    """
    Monitors bank transactions and creates accounting logs.
    
    Features:
    - CSV file monitoring (drop folder)
    - Bank API polling (pluggable)
    - Transaction categorization
    - Anomaly detection (unusual amounts)
    - Monthly accounting log generation
    """
    
    def __init__(
        self,
        vault_path: Path,
        mode: str = "csv",
        bank_config: Optional[Dict] = None,
        check_interval: int = 300  # 5 minutes
    ):
        super().__init__(vault_path, check_interval)
        
        self.mode = mode
        self.accounting_path = self.vault_path / "Accounting"
        self.current_month_file = self.accounting_path / "Current_Month.md"
        
        # Initialize bank API
        if mode == "csv":
            csv_folder = bank_config.get("csv_folder", str(self.vault_path / "Bank_CSVs")) if bank_config else str(self.vault_path / "Bank_CSVs")
            date_format = bank_config.get("date_format", "%Y-%m-%d") if bank_config else "%Y-%m-%d"
            self.bank_api = CSVBankAPI(Path(csv_folder), date_format)
        elif mode == "api":
            # TODO: Implement specific bank APIs
            raise NotImplementedError("API mode requires bank-specific implementation")
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        # Load known transactions
        self.processed_transactions = self._load_processed_transactions()
        
        # Subscription patterns for auto-categorization
        self.subscription_patterns = {
            'netflix.com': 'Netflix',
            'spotify.com': 'Spotify',
            'adobe.com': 'Adobe Creative Cloud',
            'notion.so': 'Notion',
            'slack.com': 'Slack',
            'aws.amazon.com': 'AWS',
            'azure.microsoft.com': 'Azure',
            'github.com': 'GitHub',
        }
        
        # Anomaly detection thresholds
        self.large_transaction_threshold = 1000.0  # Flag transactions > $1000
        self.unusual_frequency = 10  # Flag if > 10 transactions/day
        
        # Disable file-based logging for testing (use console only)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def check_for_updates(self) -> List[Transaction]:
        """Fetch new transactions from bank API/CSV"""
        # Get transactions from last 7 days
        since = datetime.now() - timedelta(days=7)
        
        try:
            transactions = self.bank_api.get_transactions(since)
            # Filter out already processed
            new_transactions = [
                t for t in transactions
                if t.transaction_id not in self.processed_transactions
            ]
            return new_transactions
        except Exception as e:
            logger.error(f"Error fetching transactions: {e}")
            return []
    
    def create_action_file(self, transaction: Transaction):
        """Create action file for unusual transactions or monthly log entry"""
        # Categorize transaction
        transaction.category = self._categorize_transaction(transaction)
        
        # Check for anomalies
        is_anomaly = self._detect_anomaly(transaction)
        
        if is_anomaly:
            # Create action file for review
            content = f"""---
type: finance_transaction
transaction_id: {transaction.transaction_id}
date: {transaction.date}
description: {transaction.description}
amount: {transaction.amount}
category: {transaction.category}
status: flagged
flagged_reason: large_amount
---

# Flagged Transaction

## Details
- **Date**: {transaction.date}
- **Description**: {transaction.description}
- **Amount**: ${transaction.amount:.2f}
- **Category**: {transaction.category}

## Action Required
- [ ] Review transaction
- [ ] Categorize correctly/confirm
- [ ] Move to /Done when reviewed
"""
            filepath = self.needs_action / f"FINANCE_{transaction.transaction_id}.md"
            filepath.write_text(content)
            logger.info(f"Created flagged transaction file: {filepath}")
        
        # Always log to current month file
        self._log_to_monthly(transaction)
        
        # Mark as processed
        self.processed_transactions.add(transaction.transaction_id)
        self._save_processed_transactions()
    
    def _categorize_transaction(self, transaction: Transaction) -> str:
        """Auto-categorize transaction"""
        description = transaction.description.lower()
        
        # Check for subscriptions
        for pattern, name in self.subscription_patterns.items():
            if pattern in description:
                return f"subscription:{name}"
        
        # Basic categorization
        if transaction.amount > 0:
            return "income"
        else:
            return "expense"
    
    def _detect_anomaly(self, transaction: Transaction) -> bool:
        """Detect anomalous transactions"""
        # Large transaction check
        if abs(transaction.amount) > self.large_transaction_threshold:
            return True
        
        # TODO: Add frequency-based detection
        # TODO: Add ML-based anomaly detection
        
        return False
    
    def _log_to_monthly(self, transaction: Transaction):
        """Append transaction to monthly accounting log"""
        now = datetime.now()
        month_str = now.strftime("%Y-%m")
        
        # Create accounting file if it doesn't exist
        if not self.current_month_file.exists():
            self.current_month_file.write_text(f"""---
month: {month_str}
created: {now.isoformat()}
last_updated: {now.isoformat()}
---

# Accounting Log: {month_str}

## Summary
- **Total Income**: $0.00
- **Total Expenses**: $0.00
- **Net**: $0.00

## Transactions

| Date | Description | Amount | Category | Status |
|------|-------------|--------|----------|--------|
""")
        
        # Read current content
        content = self.current_month_file.read_text()
        
        # Add transaction row
        new_row = f"| {transaction.date} | {transaction.description} | ${transaction.amount:.2f} | {transaction.category} | {transaction.status} |\n"
        
        # Insert before the last line (or append)
        lines = content.split('\n')
        # Find the table and add the row
        for i, line in enumerate(lines):
            if line.startswith('| Date |'):
                # Find next header or end
                for j in range(i+1, len(lines)):
                    if lines[j].startswith('|') and j > i+1:
                        lines.insert(j, new_row.strip())
                        break
                else:
                    lines.append(new_row.strip())
                break
        else:
            lines.append(new_row.strip())
        
        # Update last_updated
        content = '\n'.join(lines)
        content = content.replace(
            f"last_updated: {month_str}",
            f"last_updated: {now.isoformat()}"
        )
        
        self.current_month_file.write_text(content)
    
    def _load_processed_transactions(self) -> set:
        """Load set of processed transaction IDs"""
        state_file = self.accounting_path / ".processed_transactions.json"
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
                return set(data)
            except:
                pass
        return set()
    
    def _save_processed_transactions(self):
        """Save processed transaction IDs"""
        state_file = self.accounting_path / ".processed_transactions.json"
        state_file.write_text(json.dumps(list(self.processed_transactions), indent=2))
    
    def generate_monthly_summary(self) -> Path:
        """Generate a monthly summary report"""
        now = datetime.now()
        month_str = now.strftime("%Y-%m")
        summary_file = self.accounting_path / f"{month_str}_Summary.md"
        
        # Parse current month transactions
        if not self.current_month_file.exists():
            return None
        
        content = self.current_month_file.read_text()
        
        # Calculate totals
        total_income = 0.0
        total_expenses = 0.0
        transactions = []
        
        # Simple parsing (in production, use proper CSV/Markdown parser)
        for line in content.split('\n'):
            if line.startswith('|') and '$' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 3:
                    try:
                        amount_str = parts[2].replace('$', '').replace(',', '')
                        amount = float(amount_str)
                        if amount > 0:
                            total_income += amount
                        else:
                            total_expenses += abs(amount)
                    except:
                        pass
        
        # Generate summary
        summary = f"""---
month: {month_str}
generated: {now.isoformat()}
---

# Monthly Summary: {month_str}

## Financial Overview
- **Total Income**: ${total_income:.2f}
- **Total Expenses**: ${total_expenses:.2f}
- **Net Profit**: ${total_income - total_expenses:.2f}
- **Profit Margin**: {(total_income - total_expenses) / total_income * 100 if total_income > 0 else 0:.1f}%

## Key Metrics
- Average daily income: ${total_income / now.day:.2f}
- Average daily expense: ${total_expenses / now.day:.2f}

## Top Expenses
(To be implemented: sort and list top 10 expenses)

## Subscriptions
(To be implemented: list all subscription transactions)

---
*Generated by Finance Watcher v0.1*
"""
        
        summary_file.write_text(summary)
        logger.info(f"Generated monthly summary: {summary_file}")
        return summary_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Finance/Bank Transaction Watcher")
    parser.add_argument("--vault-path", required=True, help="Path to Obsidian vault")
    parser.add_argument("--mode", choices=["csv", "api"], default="csv", help="Monitoring mode")
    parser.add_argument("--csv-folder", help="Path to CSV drop folder")
    parser.add_argument("--check-interval", type=int, default=300, help="Check interval in seconds")
    parser.add_argument("--generate-summary", action="store_true", help="Generate monthly summary")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    vault_path = Path(args.vault_path)
    
    bank_config = {}
    if args.csv_folder:
        bank_config["csv_folder"] = args.csv_folder
    
    watcher = FinanceWatcher(
        vault_path=vault_path,
        mode=args.mode,
        bank_config=bank_config,
        check_interval=args.check_interval
    )
    
    if args.generate_summary:
        watcher.generate_monthly_summary()
    else:
        logger.info(f"Starting Finance Watcher (mode={args.mode})")
        watcher.run()
