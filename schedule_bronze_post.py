"""
LinkedIn Post Scheduler - Bronze Tier Completion
Automatically publishes the Bronze Tier post 2 hours after the first post.

Usage:
    python schedule_bronze_post.py
    
This will:
1. Wait for 2 hours (7200 seconds)
2. Run the Bronze Tier post publisher
3. Exit automatically

You can run this in the background and it will execute automatically.
"""

import sys
import time
import subprocess
from datetime import datetime, timedelta


def schedule_bronze_post(delay_hours=2):
    """Schedule Bronze Tier post to be published after delay."""
    
    delay_seconds = delay_hours * 3600
    scheduled_time = datetime.now() + timedelta(hours=delay_hours)
    
    print("=" * 70)
    print("⏰ BRONZE TIER POST - SCHEDULED")
    print("=" * 70)
    print(f"\n📅 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Scheduled time: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏳ Delay: {delay_hours} hours ({delay_seconds} seconds)")
    print("\n📝 Post file: AI_Employee_Vault/Plans/Plan_linkedin_bronze_tier_completion.md")
    print("\n💡 You can close this window - it will run in background.")
    print("   Or keep it open to see the progress.")
    print("\n" + "=" * 70)
    print(f"\n⏳ Waiting {delay_seconds} seconds...")
    print("   (Progress updates every 15 minutes)\n")
    
    # Countdown with progress updates
    elapsed = 0
    update_interval = 900  # 15 minutes
    
    while elapsed < delay_seconds:
        time.sleep(min(update_interval, delay_seconds - elapsed))
        elapsed += update_interval
        remaining = delay_seconds - elapsed
        remaining_minutes = remaining // 60
        
        if remaining_minutes > 0:
            print(f"   ⏳ {remaining_minutes} minutes remaining...")
    
    # Final wait to exact time
    remaining = delay_seconds - elapsed
    if remaining > 0:
        time.sleep(remaining)
    
    print("\n" + "=" * 70)
    print("⏰ TIME TO PUBLISH!")
    print("=" * 70)
    print(f"\n📅 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🚀 Starting Bronze Tier post publisher...\n")
    
    # Run the post publisher
    try:
        result = subprocess.run(
            [sys.executable, 'auto_post_linkedin_bronze.py'],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n" + "=" * 70)
            print("✅ SCHEDULED TASK COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print(f"\n📅 Completion time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print("\n" + "=" * 70)
            print("❌ SCHEDULED TASK COMPLETED WITH ERRORS")
            print("=" * 70)
            return False
            
    except Exception as e:
        print(f"\n✗ Error running publisher: {e}")
        return False


if __name__ == '__main__':
    print("\n🤖 AI EMPLOYEE - LINKEDIN POST SCHEDULER\n")
    
    try:
        # Schedule for 2 hours from now
        success = schedule_bronze_post(delay_hours=2)
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠ Scheduler cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
