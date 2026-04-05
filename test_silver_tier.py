"""
Silver Tier Verification Test

Tests all Silver Tier components:
- WhatsApp Watcher
- LinkedIn Poster
- Email MCP Client
- Plan Generator
- HITL Approval Workflow
- Scheduler

Usage:
    python test_silver_tier.py
"""

import sys
from pathlib import Path


def test_imports():
    """Test that all Silver Tier modules can be imported."""
    print("=" * 60)
    print("Silver Tier Import Tests")
    print("=" * 60)
    
    results = []
    
    # Watchers
    print("\n[Watchers]")
    try:
        from watchers.whatsapp_watcher import WhatsAppWatcher
        print("  ✓ whatsapp_watcher imported")
        results.append(("WhatsApp Watcher", True))
    except Exception as e:
        print(f"  ✗ whatsapp_watcher failed: {e}")
        results.append(("WhatsApp Watcher", False))
    
    try:
        from watchers.gmail_watcher import GmailWatcher
        print("  ✓ gmail_watcher imported")
        results.append(("Gmail Watcher", True))
    except Exception as e:
        print(f"  ✗ gmail_watcher failed: {e}")
        results.append(("Gmail Watcher", False))
    
    try:
        from watchers.filesystem_watcher import FileSystemWatcher
        print("  ✓ filesystem_watcher imported")
        results.append(("File System Watcher", True))
    except Exception as e:
        print(f"  ✗ filesystem_watcher failed: {e}")
        results.append(("File System Watcher", False))
    
    # Skills
    print("\n[Skills]")
    try:
        from skills.plan_generator import PlanGenerator
        print("  ✓ plan_generator imported")
        results.append(("Plan Generator", True))
    except Exception as e:
        print(f"  ✗ plan_generator failed: {e}")
        results.append(("Plan Generator", False))
    
    try:
        from skills.email_mcp_client import EmailMCPClient
        print("  ✓ email_mcp_client imported")
        results.append(("Email MCP Client", True))
    except Exception as e:
        print(f"  ✗ email_mcp_client failed: {e}")
        results.append(("Email MCP Client", False))
    
    try:
        from skills.linkedin_poster import LinkedInPoster
        print("  ✓ linkedin_poster imported")
        results.append(("LinkedIn Poster", True))
    except Exception as e:
        print(f"  ✗ linkedin_poster failed: {e}")
        results.append(("LinkedIn Poster", False))
    
    try:
        from skills.approval_workflow import ApprovalWorkflow
        print("  ✓ approval_workflow imported")
        results.append(("HITL Approval Workflow", True))
    except Exception as e:
        print(f"  ✗ approval_workflow failed: {e}")
        results.append(("HITL Approval Workflow", False))
    
    # Scheduler
    try:
        import apscheduler
        print("  ✓ apscheduler imported")
        results.append(("Scheduler (APScheduler)", True))
    except Exception as e:
        print(f"  ✗ apscheduler failed: {e}")
        results.append(("Scheduler (APScheduler)", False))
    
    # Playwright
    try:
        from playwright.sync_api import sync_playwright
        print("  ✓ playwright imported")
        results.append(("Playwright", True))
    except Exception as e:
        print(f"  ✗ playwright failed: {e}")
        results.append(("Playwright", False))
    
    # Google API
    try:
        from googleapiclient.discovery import build
        print("  ✓ google-api-python-client imported")
        results.append(("Gmail API Client", True))
    except Exception as e:
        print(f"  ✗ google-api-python-client failed: {e}")
        results.append(("Gmail API Client", False))
    
    return results


def test_vault_structure():
    """Test Silver Tier vault structure."""
    print("\n" + "=" * 60)
    print("Vault Structure Tests")
    print("=" * 60)
    
    vault_path = Path("AI_Employee_Vault")
    
    required_folders = [
        "Inbox",
        "Needs_Action",
        "Done",
        "Plans",
        "Accounting",
        "Briefings",
        "Pending_Approval",
        "Approved",
        "Rejected",
        "In_Progress",
        "Logs",
    ]
    
    results = []
    for folder in required_folders:
        folder_path = vault_path / folder
        if folder_path.exists() and folder_path.is_dir():
            print(f"  ✓ {folder}/")
            results.append((folder, True))
        else:
            print(f"  ✗ {folder}/ - MISSING")
            results.append((folder, False))
    
    return results


def test_vault_files():
    """Test required vault files."""
    print("\n" + "=" * 60)
    print("Vault Files Tests")
    print("=" * 60)
    
    vault_path = Path("AI_Employee_Vault")
    
    required_files = [
        "Dashboard.md",
        "Company_Handbook.md",
        "Business_Goals.md",
    ]
    
    results = []
    for file in required_files:
        file_path = vault_path / file
        if file_path.exists():
            print(f"  ✓ {file}")
            results.append((file, True))
        else:
            print(f"  ✗ {file} - MISSING")
            results.append((file, False))
    
    return results


def test_env_configuration():
    """Test .env file configuration."""
    print("\n" + "=" * 60)
    print("Environment Configuration Tests")
    print("=" * 60)
    
    env_path = Path(".env")
    if not env_path.exists():
        print("  ✗ .env file MISSING")
        print("     → Copy .env.example to .env and fill in your details")
        return [(".env", False)]
    
    print("  ✓ .env file found")
    
    # Check required variables
    required_vars = [
        "OPENROUTER_API_KEY",
        "GMAIL_USER",
        "GMAIL_APP_PASSWORD",
        "VAULT_PATH",
        "WHATSAPP_SESSION_PATH",
        "LINKEDIN_SESSION_PATH",
    ]
    
    results = [(".env exists", True)]
    
    with open(env_path, "r") as f:
        content = f.read()
    
    for var in required_vars:
        if var in content and not content.split(f"{var}=")[1].split("\n")[0].strip().startswith("your-"):
            print(f"  ✓ {var} configured")
            results.append((var, True))
        else:
            print(f"  ⚠ {var} - needs configuration")
            results.append((var, False))
    
    return results


def test_skills_directory():
    """Test .qwen/skills directory."""
    print("\n" + "=" * 60)
    print("Skills Directory Tests")
    print("=" * 60)
    
    skills_path = Path(".qwen/skills")
    
    required_skills = [
        "browsing-with-playwright",
        "whatsapp-watcher",
        "linkedin-poster",
        "email-mcp",
        "plan-generator",
        "hitl-approval",
        "scheduler",
    ]
    
    results = []
    for skill in required_skills:
        skill_path = skills_path / skill
        if skill_path.exists():
            print(f"  ✓ {skill}/")
            results.append((skill, True))
        else:
            print(f"  ✗ {skill}/ - MISSING")
            results.append((skill, False))
    
    return results


def test_watcher_scripts():
    """Test watcher scripts exist."""
    print("\n" + "=" * 60)
    print("Watcher Scripts Tests")
    print("=" * 60)
    
    watchers_path = Path("watchers")
    
    required_scripts = [
        "base_watcher.py",
        "whatsapp_watcher.py",
        "gmail_watcher.py",
        "filesystem_watcher.py",
    ]
    
    results = []
    for script in required_scripts:
        script_path = watchers_path / script
        if script_path.exists():
            print(f"  ✓ {script}")
            results.append((script, True))
        else:
            print(f"  ✗ {script} - MISSING")
            results.append((script, False))
    
    return results


def test_skill_scripts():
    """Test skill scripts exist."""
    print("\n" + "=" * 60)
    print("Skill Scripts Tests")
    print("=" * 60)
    
    skills_path = Path("skills")
    
    required_scripts = [
        "plan_generator.py",
        "email_mcp_client.py",
        "linkedin_poster.py",
        "approval_workflow.py",
    ]
    
    results = []
    for script in required_scripts:
        script_path = skills_path / script
        if script_path.exists():
            print(f"  ✓ {script}")
            results.append((script, True))
        else:
            print(f"  ✗ {script} - MISSING")
            results.append((script, False))
    
    return results


def print_summary(all_results):
    """Print test summary."""
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total = len(all_results)
    passed = sum(1 for _, result in all_results if result)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All Silver Tier tests passed!")
        print("\nYour AI Employee Silver Tier is ready!")
        print("\nNext steps:")
        print("  1. Start WhatsApp watcher:")
        print("     python watchers/whatsapp_watcher.py AI_Employee_Vault --session-path AI_Employee_Vault/.whatsapp_session")
        print("\n  2. Start Gmail watcher:")
        print("     python watchers/gmail_watcher.py AI_Employee_Vault")
        print("\n  3. Start orchestrator:")
        print("     python orchestrator.py AI_Employee_Vault")
        print("\n  4. (Optional) Start scheduler for automated tasks:")
        print("     python -m apscheduler")
        print("\n  5. Open AI_Employee_Vault in Obsidian to monitor progress")
        return 0
    else:
        print("\n⚠ Some tests failed or need configuration.")
        print("\nReview the failures above and:")
        print("  - Install missing components")
        print("  - Configure .env file with your credentials")
        print("  - Ensure all vault folders exist")
        return 1


def main():
    """Run all Silver Tier tests."""
    print("\n" + "=" * 60)
    print("SILVER TIER VERIFICATION TEST")
    print("AI Employee FTE - Autonomous Business Assistant")
    print("=" * 60)
    
    all_results = []
    
    # Run all test categories
    all_results.extend(test_imports())
    all_results.extend(test_vault_structure())
    all_results.extend(test_vault_files())
    all_results.extend(test_env_configuration())
    all_results.extend(test_skills_directory())
    all_results.extend(test_watcher_scripts())
    all_results.extend(test_skill_scripts())
    
    # Print summary
    return print_summary(all_results)


if __name__ == "__main__":
    sys.exit(main())
