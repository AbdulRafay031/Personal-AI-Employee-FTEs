"""
CEO Briefing Generator

Autonomously audits bank transactions and tasks to generate a 
"Monday Morning CEO Briefing" report.

Features:
- Revenue analysis (weekly/monthly)
- Task completion metrics
- Bottleneck identification
- Subscription audit
- Proactive suggestions
- Cost optimization recommendations

Usage:
    python ceo_briefing_generator.py --vault-path /path/to/vault
    python ceo_briefing_generator.py --vault-path /path/to/vault --generate-only
"""

import re
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BriefingData:
    """Represents a CEO briefing report"""
    period_start: str
    period_end: str
    generated_at: str
    revenue_this_week: float
    revenue_mtd: float
    revenue_target: float
    tasks_completed: int
    tasks_pending: int
    tasks_in_progress: int
    bottlenecks: List[Dict]
    subscriptions: List[Dict]
    proactive_suggestions: List[str]
    upcoming_deadlines: List[Dict]
    cost_optimization_opportunities: List[Dict]


class CEOBriefingGenerator:
    """
    Generates comprehensive weekly CEO briefings by analyzing:
    - Task completion rates
    - Financial transactions
    - Subscription usage
    - Business goals progress
    - System health
    """
    
    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)
        self.briefings_path = self.vault_path / "Briefings"
        self.accounting_path = self.vault_path / "Accounting"
        self.plans_path = self.vault_path / "Plans"
        self.done_path = self.vault_path / "Done"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.in_progress_path = self.vault_path / "In_Progress"
        
        # Ensure briefings folder exists
        self.briefings_path.mkdir(parents=True, exist_ok=True)
        
        # Load business goals
        self.business_goals_file = self.vault_path / "Business_Goals.md"
        self.business_goals = self._parse_business_goals()
    
    def generate_briefing(self, period_days: int = 7) -> Path:
        """Generate a CEO briefing for the specified period"""
        now = datetime.now()
        period_start = now - timedelta(days=period_days)
        
        logger.info(f"Generating CEO briefing for {period_start.date()} to {now.date()}")
        
        # Collect all metrics
        revenue_data = self._analyze_revenue(period_start)
        task_data = self._analyze_tasks(period_start)
        bottlenecks = self._identify_bottlenecks(period_start)
        subscriptions = self._audit_subscriptions(period_start)
        suggestions = self._generate_suggestions(revenue_data, task_data, bottlenecks, subscriptions)
        deadlines = self._find_upcoming_deadlines()
        cost_opportunities = self._find_cost_optimizations(subscriptions)
        
        # Create briefing object
        briefing = BriefingData(
            period_start=period_start.isoformat(),
            period_end=now.isoformat(),
            generated_at=now.isoformat(),
            revenue_this_week=revenue_data['total_income'],
            revenue_mtd=revenue_data['mtd_income'],
            revenue_target=self.business_goals.get('monthly_revenue_target', 10000),
            tasks_completed=task_data['completed'],
            tasks_pending=task_data['pending'],
            tasks_in_progress=task_data['in_progress'],
            bottlenecks=bottlenecks,
            subscriptions=subscriptions,
            proactive_suggestions=suggestions,
            upcoming_deadlines=deadlines,
            cost_optimization_opportunities=cost_opportunities
        )
        
        # Generate markdown file
        briefing_file = self._write_briefing(briefing)
        
        logger.info(f"CEO briefing generated: {briefing_file}")
        return briefing_file
    
    def _analyze_revenue(self, period_start: datetime) -> Dict:
        """Analyze revenue from accounting logs"""
        total_income = 0.0
        total_expenses = 0.0
        mtd_income = 0.0
        transactions = []
        
        # Read current month accounting file
        current_month_file = self.accounting_path / "Current_Month.md"
        if current_month_file.exists():
            content = current_month_file.read_text()
            
            # Parse transaction table
            for line in content.split('\n'):
                if line.startswith('|') and '$' in line:
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 4:
                        try:
                            # Extract date and amount
                            date_str = parts[0]
                            amount_str = parts[2].replace('$', '').replace(',', '')
                            amount = float(amount_str)
                            
                            # Parse date
                            try:
                                txn_date = datetime.fromisoformat(date_str)
                            except:
                                continue
                            
                            transactions.append({
                                'date': txn_date,
                                'amount': amount,
                                'description': parts[1] if len(parts) > 1 else ''
                            })
                            
                            if amount > 0:
                                if txn_date >= period_start:
                                    total_income += amount
                                # MTD calculation
                                if txn_date.month == datetime.now().month:
                                    mtd_income += amount
                            else:
                                total_expenses += abs(amount)
                        except:
                            continue
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net': total_income - total_expenses,
            'mtd_income': mtd_income,
            'transaction_count': len(transactions)
        }
    
    def _analyze_tasks(self, period_start: datetime) -> Dict:
        """Analyze task completion metrics"""
        completed = 0
        pending = 0
        in_progress = 0
        
        # Count files in Done (completed tasks)
        if self.done_path.exists():
            for done_file in self.done_path.glob("**/*.md"):
                try:
                    content = done_file.read_text()
                    # Check if completed in this period
                    if 'completed:' in content or 'status: done' in content.lower():
                        completed += 1
                except:
                    continue
        
        # Count files in Needs_Action (pending)
        if self.needs_action_path.exists():
            pending = len(list(self.needs_action_path.glob("*.md")))
        
        # Count files in In_Progress
        if self.in_progress_path.exists():
            in_progress = len(list(self.in_progress_path.glob("**/*.md")))
        
        # Calculate completion rate
        total = completed + pending + in_progress
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        return {
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'total': total,
            'completion_rate': completion_rate
        }
    
    def _identify_bottlenecks(self, period_start: datetime) -> List[Dict]:
        """Identify tasks that took too long"""
        bottlenecks = []
        
        # Analyze plans for delayed tasks
        if self.plans_path.exists():
            for plan_file in self.plans_path.glob("**/*.md"):
                try:
                    content = plan_file.read_text()
                    
                    # Extract created date
                    created_match = re.search(r'created:\s*(.+)', content)
                    if created_match:
                        created_str = created_match.group(1).strip()
                        try:
                            created = datetime.fromisoformat(created_str)
                            age_days = (datetime.now() - created).days
                            
                            # If task is older than 3 days and not done, it's a bottleneck
                            if age_days > 3:
                                # Check if still in progress or pending
                                status_match = re.search(r'status:\s*(\w+)', content)
                                status = status_match.group(1) if status_match else 'unknown'
                                
                                if status in ['pending', 'in_progress', 'pending_approval']:
                                    bottlenecks.append({
                                        'task': plan_file.stem,
                                        'age_days': age_days,
                                        'status': status,
                                        'expected_days': 2,
                                        'delay': age_days - 2
                                    })
                        except:
                            continue
                except:
                    continue
        
        return bottlenecks
    
    def _audit_subscriptions(self, period_start: datetime) -> List[Dict]:
        """Audit active subscriptions from transactions"""
        subscriptions = []
        
        # Known subscription patterns
        subscription_patterns = {
            'netflix': {'name': 'Netflix', 'expected_cost': 15.99},
            'spotify': {'name': 'Spotify', 'expected_cost': 9.99},
            'adobe': {'name': 'Adobe Creative Cloud', 'expected_cost': 54.99},
            'notion': {'name': 'Notion', 'expected_cost': 8.00},
            'slack': {'name': 'Slack', 'expected_cost': 7.25},
            'aws': {'name': 'AWS', 'expected_cost': 50.00},
            'github': {'name': 'GitHub', 'expected_cost': 4.00},
        }
        
        # Read accounting logs
        current_month_file = self.accounting_path / "Current_Month.md"
        if current_month_file.exists():
            content = current_month_file.read_text().lower()
            
            for pattern, info in subscription_patterns.items():
                if pattern in content:
                    subscriptions.append({
                        'name': info['name'],
                        'expected_cost': info['expected_cost'],
                        'status': 'active',
                        'review_recommended': True
                    })
        
        return subscriptions
    
    def _generate_suggestions(
        self,
        revenue_data: Dict,
        task_data: Dict,
        bottlenecks: List[Dict],
        subscriptions: List[Dict]
    ) -> List[str]:
        """Generate proactive suggestions based on analysis"""
        suggestions = []
        
        # Revenue-based suggestions
        if revenue_data['mtd_income'] < revenue_data.get('mtd_target', 5000) * 0.5:
            suggestions.append(
                f"⚠️ Revenue is behind target. MTD: ${revenue_data['mtd_income']:.2f}. "
                f"Consider reaching out to pending clients or launching a promotion."
            )
        
        # Task-based suggestions
        if task_data['pending'] > 10:
            suggestions.append(
                f"📋 High pending task count ({task_data['pending']}). "
                f"Consider prioritizing or delegating tasks."
            )
        
        if task_data['completion_rate'] < 50:
            suggestions.append(
                f"📉 Low completion rate ({task_data['completion_rate']:.1f}%). "
                f"Review bottlenecks and resource allocation."
            )
        
        # Bottleneck suggestions
        if bottlenecks:
            suggestions.append(
                f"🚧 {len(bottlenecks)} task(s) are delayed. "
                f"Review: {', '.join([b['task'] for b in bottlenecks[:3]])}"
            )
        
        # Subscription suggestions
        if subscriptions:
            total_sub_cost = sum(s['expected_cost'] for s in subscriptions)
            if total_sub_cost > 100:
                suggestions.append(
                    f"💰 Monthly subscription costs: ${total_sub_cost:.2f}. "
                    f"Review unused or underutilized subscriptions."
                )
        
        # Default suggestions
        if not suggestions:
            suggestions.append("✅ All metrics look healthy. Keep up the good work!")
        
        return suggestions
    
    def _find_upcoming_deadlines(self) -> List[Dict]:
        """Find upcoming project deadlines"""
        deadlines = []
        
        # Read Business_Goals.md for active projects
        if self.business_goals_file.exists():
            content = self.business_goals_file.read_text()
            
            # Look for project entries
            project_pattern = re.findall(
                r'(\d+\.?\s+Project\s+\w+.*?Due\s+(.+?))\s*-\s*Budget\s+\$?([\d,]+)',
                content,
                re.IGNORECASE
            )
            
            for project_name, due_str, budget_str in project_pattern:
                try:
                    due_date = datetime.strptime(due_str.strip(), "%b %d")
                    days_until = (due_date - datetime.now()).days
                    
                    if 0 <= days_until <= 30:  # Next 30 days
                        deadlines.append({
                            'project': project_name.strip(),
                            'due_date': due_date.isoformat(),
                            'days_remaining': days_until,
                            'budget': float(budget_str.replace(',', ''))
                        })
                except:
                    continue
        
        return deadlines
    
    def _find_cost_optimizations(self, subscriptions: List[Dict]) -> List[Dict]:
        """Find cost optimization opportunities"""
        opportunities = []
        
        for sub in subscriptions:
            # Flag expensive subscriptions
            if sub['expected_cost'] > 50:
                opportunities.append({
                    'type': 'subscription_review',
                    'item': sub['name'],
                    'current_cost': sub['expected_cost'],
                    'suggestion': f"Review usage of {sub['name']} (${sub['expected_cost']:.2f}/mo). Consider downgrading or canceling if underutilized."
                })
        
        return opportunities
    
    def _parse_business_goals(self) -> Dict:
        """Parse Business_Goals.md for targets and objectives"""
        goals = {}
        
        if not self.business_goals_file.exists():
            return goals
        
        content = self.business_goals_file.read_text()
        
        # Extract monthly revenue target
        revenue_match = re.search(r'Monthly goal:\s*\$?([\d,]+)', content)
        if revenue_match:
            goals['monthly_revenue_target'] = float(revenue_match.group(1).replace(',', ''))
        
        # Extract key metrics
        # (Simplified - in production, parse the full table)
        
        return goals
    
    def _write_briefing(self, briefing: BriefingData) -> Path:
        """Write briefing to markdown file"""
        # Generate filename
        date_str = datetime.fromisoformat(briefing.generated_at).strftime("%Y-%m-%d")
        day_name = datetime.fromisoformat(briefing.generated_at).strftime("%A")
        filename = f"{date_str}_{day_name}_Briefing.md"
        briefing_file = self.briefings_path / filename
        
        # Calculate progress
        revenue_progress = (briefing.revenue_mtd / briefing.revenue_target * 100) if briefing.revenue_target > 0 else 0
        
        # Generate markdown
        content = f"""---
generated: {briefing.generated_at}
period: {briefing.period_start[:10]} to {briefing.period_end[:10]}
---

# {day_name} Morning CEO Briefing

## Executive Summary
{self._generate_executive_summary(briefing)}

## Revenue
- **This Week**: ${briefing.revenue_this_week:,.2f}
- **MTD**: ${briefing.revenue_mtd:,.2f} ({revenue_progress:.0f}% of ${briefing.revenue_target:,.2f} target)
- **Trend**: {'✅ On track' if revenue_progress >= 50 else '⚠️ Behind target'}

## Completed Tasks
- **This Period**: {briefing.tasks_completed} tasks completed
- **Pending**: {briefing.tasks_pending} tasks waiting
- **In Progress**: {briefing.tasks_in_progress} tasks active
- **Completion Rate**: {self._calculate_completion_rate(briefing):.1f}%

"""
        
        # Add bottlenecks
        if briefing.bottlenecks:
            content += "## Bottlenecks\n"
            content += "| Task | Expected | Actual | Delay |\n"
            content += "|------|----------|--------|-------|\n"
            for b in briefing.bottlenecks:
                content += f"| {b['task']} | {b['expected_days']} days | {b['age_days']} days | +{b['delay']} days |\n"
            content += "\n"
        
        # Add proactive suggestions
        content += "## Proactive Suggestions\n\n"
        for suggestion in briefing.proactive_suggestions:
            content += f"- {suggestion}\n"
        content += "\n"
        
        # Add cost optimization
        if briefing.cost_optimization_opportunities:
            content += "### Cost Optimization\n"
            for opp in briefing.cost_optimization_opportunities:
                content += f"- **{opp['item']}**: {opp['suggestion']}\n"
            content += "\n"
        
        # Add upcoming deadlines
        if briefing.upcoming_deadlines:
            content += "### Upcoming Deadlines\n"
            for deadline in briefing.upcoming_deadlines:
                content += f"- **{deadline['project']}**: {deadline['days_remaining']} days remaining (Budget: ${deadline['budget']:,.2f})\n"
            content += "\n"
        
        # Add subscriptions
        if briefing.subscriptions:
            content += "### Active Subscriptions\n"
            total_cost = sum(s['expected_cost'] for s in briefing.subscriptions)
            content += f"**Total Monthly Cost**: ${total_cost:,.2f}\n\n"
            for sub in briefing.subscriptions:
                content += f"- {sub['name']}: ${sub['expected_cost']:.2f}/mo\n"
            content += "\n"
        
        content += "---\n*Generated by AI Employee CEO Briefing Generator v0.1*\n"
        
        briefing_file.write_text(content, encoding='utf-8')
        return briefing_file
    
    def _generate_executive_summary(self, briefing: BriefingData) -> str:
        """Generate executive summary text"""
        parts = []
        
        if briefing.revenue_this_week > 0:
            parts.append(f"Strong week with ${briefing.revenue_this_week:,.2f} in revenue.")
        else:
            parts.append("No revenue recorded this week.")
        
        if briefing.bottlenecks:
            parts.append(f"{len(briefing.bottlenecks)} bottleneck(s) identified.")
        
        if briefing.tasks_completed > 0:
            parts.append(f"{briefing.tasks_completed} task(s) completed successfully.")
        
        return " ".join(parts) if parts else "Review metrics below."
    
    def _calculate_completion_rate(self, briefing: BriefingData) -> float:
        """Calculate task completion rate"""
        total = briefing.tasks_completed + briefing.tasks_pending + briefing.tasks_in_progress
        if total == 0:
            return 0.0
        return (briefing.tasks_completed / total) * 100


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CEO Briefing Generator")
    parser.add_argument("--vault-path", required=True, help="Path to Obsidian vault")
    parser.add_argument("--period-days", type=int, default=7, help="Analysis period in days")
    parser.add_argument("--generate-only", action="store_true", help="Generate and exit")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    generator = CEOBriefingGenerator(Path(args.vault_path))
    briefing_file = generator.generate_briefing(args.period_days)
    
    print(f"CEO Briefing generated: {briefing_file}")
