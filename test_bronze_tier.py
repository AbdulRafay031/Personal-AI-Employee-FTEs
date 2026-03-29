"""
Test Script for Bronze Tier

Quick verification that all components are working correctly.

Usage:
    python test_bronze_tier.py
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from watchers.base_watcher import BaseWatcher
        print("  ✓ base_watcher imported")
    except Exception as e:
        print(f"  ✗ base_watcher failed: {e}")
        return False
    
    try:
        from watchers.filesystem_watcher import FileSystemWatcher
        print("  ✓ filesystem_watcher imported")
    except Exception as e:
        print(f"  ✗ filesystem_watcher failed: {e}")
        return False
    
    try:
        from watchers.gmail_watcher import GmailWatcher
        print("  ✓ gmail_watcher imported (Gmail API optional)")
    except ImportError:
        print("  ⚠ gmail_watcher: Gmail API not installed (optional)")
    except Exception as e:
        print(f"  ✗ gmail_watcher failed: {e}")
        return False
    
    try:
        from orchestrator import Orchestrator
        print("  ✓ orchestrator imported")
    except Exception as e:
        print(f"  ✗ orchestrator failed: {e}")
        return False
    
    return True


def test_vault_structure():
    """Test that vault folder structure exists."""
    print("\nTesting vault structure...")
    
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
    
    all_exist = True
    for folder in required_folders:
        folder_path = vault_path / folder
        if folder_path.exists() and folder_path.is_dir():
            print(f"  ✓ {folder}/")
        else:
            print(f"  ✗ {folder}/ - MISSING")
            all_exist = False
    
    return all_exist


def test_vault_files():
    """Test that required vault files exist."""
    print("\nTesting vault files...")
    
    vault_path = Path("AI_Employee_Vault")
    
    required_files = [
        "Dashboard.md",
        "Company_Handbook.md",
        "Business_Goals.md",
    ]
    
    all_exist = True
    for file in required_files:
        file_path = vault_path / file
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_exist = False
    
    return all_exist


def test_project_files():
    """Test that required project files exist."""
    print("\nTesting project files...")
    
    required_files = [
        "README.md",
        "requirements.txt",
        "orchestrator.py",
        "watchers/base_watcher.py",
        "watchers/gmail_watcher.py",
        "watchers/filesystem_watcher.py",
    ]
    
    all_exist = True
    for file in required_files:
        file_path = Path(file)
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_exist = False
    
    return all_exist


def test_drop_folder():
    """Create test drop folder if it doesn't exist."""
    print("\nTesting drop folder...")
    
    drop_folder = Path("test_drop")
    drop_folder.mkdir(exist_ok=True)
    print(f"  ✓ Test drop folder created: {drop_folder}")
    
    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("Bronze Tier Verification Tests")
    print("=" * 50)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Vault Structure", test_vault_structure()))
    results.append(("Vault Files", test_vault_files()))
    results.append(("Project Files", test_project_files()))
    results.append(("Drop Folder", test_drop_folder()))
    
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Bronze Tier implementation complete!")
        print("\nNext steps:")
        print("  1. Open AI_Employee_Vault in Obsidian")
        print("  2. Review Dashboard.md and Company_Handbook.md")
        print("  3. Install dependencies: pip install -r requirements.txt")
        print("  4. Start watchers: python watchers/filesystem_watcher.py AI_Employee_Vault --watch-folder test_drop")
        print("  5. Start orchestrator: python orchestrator.py AI_Employee_Vault")
        print("  6. Use Qwen Code to process tasks: qwen")
        return 0
    else:
        print("\n❌ Some tests failed. Please review and fix.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
