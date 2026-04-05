"""
===============================================================================
WHATSAPP CLOUD API - NOTIFICATION SYSTEM
Phase 2: Cloud Deployment Add-on

Sends WhatsApp notifications for:
- New jobs found
- Applications submitted
- Daily summary reports
- Error alerts

Requirements:
- Meta Developer Account (Free)
- WhatsApp Business API (Free tier available)
- Phone number for WhatsApp Business
===============================================================================
"""

import os
import requests
import json
from datetime import datetime
from pathlib import Path


class WhatsAppNotifier:
    """Send WhatsApp notifications via Meta Cloud API."""
    
    def __init__(self, access_token: str, phone_number_id: str, recipient_number: str):
        """
        Initialize WhatsApp notifier.
        
        Args:
            access_token: Meta Cloud API access token
            phone_number_id: Your WhatsApp Business phone number ID
            recipient_number: Number to send notifications to (with country code)
        """
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.recipient_number = recipient_number
        self.base_url = f"https://graph.facebook.com/v17.0/{phone_number_id}"
        
        # Track notifications sent today
        self.notifications_today = 0
        self.max_notifications_per_day = 50
    
    def send_message(self, message: str, message_type: str = "text") -> bool:
        """
        Send WhatsApp message.
        
        Args:
            message: Message text
            message_type: "text" or "template"
            
        Returns:
            True if sent successfully
        """
        if self.notifications_today >= self.max_notifications_per_day:
            print(f"⚠ Daily notification limit reached ({self.max_notifications_per_day})")
            return False
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": self.recipient_number,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                self.notifications_today += 1
                print(f"✓ WhatsApp notification sent")
                return True
            else:
                print(f"✗ WhatsApp API error: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Error sending WhatsApp: {e}")
            return False
    
    def send_job_alert(self, job_data: dict) -> bool:
        """Send new job alert."""
        message = f"""
🔥 NEW JOB ALERT!

📌 Position: {job_data.get('title', 'Unknown')}
🏢 Company: {job_data.get('company', 'Unknown')}
📍 Location: {job_data.get('location', 'Unknown')}
⏰ Posted: {job_data.get('time_ago', 'Unknown')}

🎯 Priority: {'HIGH (Last 24h)' if job_data.get('is_recent') else 'Medium'}

🔗 Apply: {job_data.get('url', 'N/A')}

#JobAlert #Internship
"""
        return self.send_message(message)
    
    def send_application_confirmation(self, job_data: dict) -> bool:
        """Send application submitted confirmation."""
        message = f"""
✅ APPLICATION SUBMITTED!

📌 Position: {job_data.get('title', 'Unknown')}
🏢 Company: {job_data.get('company', 'Unknown')}
📍 Location: {job_data.get('location', 'Unknown')}
⏰ Applied at: {datetime.now().strftime('%I:%M %p')}

📊 Applications today: {job_data.get('applications_count', 'N/A')}/20

Good luck! 🍀
"""
        return self.send_message(message)
    
    def send_daily_summary(self, stats: dict) -> bool:
        """Send daily summary report."""
        message = f"""
📊 DAILY JOB APPLICATION SUMMARY
{datetime.now().strftime('%A, %B %d, %Y')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Jobs Scanned: {stats.get('jobs_scanned', 0)}
✅ Applications Submitted: {stats.get('applications', 0)}
🎯 Recent (24h): {stats.get('recent_apps', 0)}
📍 Karachi: {stats.get('karachi_apps', 0)}
🌍 Remote: {stats.get('remote_apps', 0)}

📈 Response Rate: {stats.get('response_rate', '0')}%
📞 Interviews: {stats.get('interviews', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI Job Auto-Applier
"""
        return self.send_message(message)
    
    def send_error_alert(self, error_message: str) -> bool:
        """Send error notification."""
        message = f"""
⚠️ ERROR ALERT

🤖 AI Job Auto-Applier
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}

Error:
{error_message[:500]}

Please check the system logs.
"""
        return self.send_message(message)
    
    def send_status_request(self) -> bool:
        """Send status update on user request."""
        message = f"""
📊 SYSTEM STATUS

✅ Status: Running
⏰ Last run: {datetime.now().strftime('%Y-%m-%d %H:%M')}
📊 Applications today: {self.notifications_today}
🔋 Cloud server: Online

Reply 'STATUS' anytime for update.
"""
        return self.send_message(message)


def setup_whatsapp():
    """
    Setup WhatsApp Cloud API.
    
    Returns:
        WhatsAppNotifier instance
    """
    print("=" * 70)
    print("WHATSAPP CLOUD API SETUP")
    print("=" * 70)
    print()
    
    # Get credentials from user
    print("Get your credentials from:")
    print("https://developers.facebook.com/apps/")
    print()
    
    access_token = input("Enter Access Token: ").strip()
    phone_number_id = input("Enter Phone Number ID: ").strip()
    recipient_number = input("Enter your WhatsApp number (with country code): ").strip()
    
    # Create notifier
    notifier = WhatsAppNotifier(access_token, phone_number_id, recipient_number)
    
    # Test message
    print("\nSending test message...")
    success = notifier.send_message("🤖 AI Job Auto-Aplier - WhatsApp setup complete!")
    
    if success:
        print("✓ WhatsApp setup complete!")
    else:
        print("✗ Setup failed. Check credentials.")
    
    return notifier


# Example usage
if __name__ == '__main__':
    # Setup (first time only)
    # notifier = setup_whatsapp()
    
    # After setup, use saved credentials
    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN', 'YOUR_TOKEN')
    phone_number_id = os.getenv('WHATSAPP_PHONE_ID', 'YOUR_PHONE_ID')
    recipient = os.getenv('WHATSAPP_RECIPIENT', '+923161163799')
    
    notifier = WhatsAppNotifier(access_token, phone_number_id, recipient)
    
    # Test message
    notifier.send_message(" AI Job Auto-Applier Phase 2 - Cloud Deployment Active!")
