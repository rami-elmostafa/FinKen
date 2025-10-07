#!/usr/bin/env python3
"""
Test script for password expiry notifications
Run this script to test the password expiry notification functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from EmailUser import send_password_expiry_notifications
from datetime import datetime, timedelta, timezone
from SupabaseClient import _sb

def create_test_user_with_expiring_password():
    """
    Create a test user with a password that expires in 2 days for testing purposes
    """
    try:
        sb = _sb()
        
        # Calculate expiry date (2 days from now)
        expiry_date = datetime.now(timezone.utc) + timedelta(days=2)
        
        test_user_data = {
            'Username': 'test_expiry_user',
            'FirstName': 'Test',
            'LastName': 'User',
            'Email': 'test@example.com',  # Change this to your test email
            'PasswordHash': 'dummy_hash',
            'PasswordExpiryDate': expiry_date.isoformat(),
            'IsActive': True,
            'IsSuspended': False,
            'RoleID': 3  # Accountant role
        }
        
        response = sb.table('users').insert(test_user_data).execute()
        
        if response.data:
            print(f"✅ Test user created with ID: {response.data[0]['UserID']}")
            print(f"   Username: {test_user_data['Username']}")
            print(f"   Email: {test_user_data['Email']}")
            print(f"   Password expires: {expiry_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            return response.data[0]['UserID']
        else:
            print("❌ Failed to create test user")
            return None
            
    except Exception as e:
        print(f"❌ Error creating test user: {str(e)}")
        return None

def cleanup_test_user(user_id):
    """
    Remove the test user after testing
    """
    try:
        sb = _sb()
        response = sb.table('users').delete().eq('UserID', user_id).execute()
        print(f"🧹 Cleaned up test user with ID: {user_id}")
    except Exception as e:
        print(f"⚠️  Error cleaning up test user: {str(e)}")

def test_password_expiry_notifications():
    """
    Test the password expiry notification system
    """
    print("🔧 Testing Password Expiry Notification System")
    print("=" * 50)
    
    # Step 1: Create a test user
    print("\n1. Creating test user with expiring password...")
    test_user_id = create_test_user_with_expiring_password()
    
    if not test_user_id:
        print("❌ Cannot proceed without test user")
        return False
    
    try:
        # Step 2: Test the notification function
        print("\n2. Testing password expiry notification function...")
        result = send_password_expiry_notifications()
        
        print(f"\n📊 Test Results:")
        print(f"   Success: {result.get('success')}")
        print(f"   Message: {result.get('message')}")
        print(f"   Users notified: {result.get('users_notified', 0)}")
        
        if result.get('notifications_sent'):
            print(f"\n📧 Notifications sent to:")
            for notification in result['notifications_sent']:
                print(f"   - {notification['name']} ({notification['email']})")
                print(f"     Password expires in {notification['days_until_expiry']} days")
        
        if result.get('errors'):
            print(f"\n⚠️  Errors encountered:")
            for error in result['errors']:
                print(f"   - {error}")
        
        success = result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error testing notifications: {str(e)}")
        success = False
    
    finally:
        # Step 3: Cleanup
        print("\n3. Cleaning up test data...")
        cleanup_test_user(test_user_id)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Test completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Update your email in the test script to receive actual notifications")
        print("   2. Deploy the code to your production environment")
        print("   3. Set up the Supabase cron job using the provided SQL script")
    else:
        print("❌ Test failed - check error messages above")
    
    return success

def check_users_with_expiring_passwords():
    """
    Check how many real users currently have expiring passwords
    """
    try:
        sb = _sb()
        
        # Get users with passwords expiring in the next 7 days
        cutoff_date = datetime.now(timezone.utc) + timedelta(days=7)
        
        response = sb.table('users').select(
            'UserID, Username, FirstName, LastName, Email, PasswordExpiryDate'
        ).lte('PasswordExpiryDate', cutoff_date.isoformat()).eq('IsActive', True).execute()
        
        print("\n📋 Current users with passwords expiring in the next 7 days:")
        print("-" * 60)
        
        if not response.data:
            print("   No users found with expiring passwords")
            return
        
        for user in response.data:
            if user.get('PasswordExpiryDate'):
                expiry_date = datetime.fromisoformat(user['PasswordExpiryDate'].replace('Z', '+00:00'))
                days_until_expiry = (expiry_date - datetime.now(timezone.utc)).days
                
                status = "🔴 EXPIRED" if days_until_expiry < 0 else f"⏰ {days_until_expiry} days"
                
                print(f"   {user['FirstName']} {user['LastName']} ({user['Username']})")
                print(f"      Email: {user['Email']}")
                print(f"      Status: {status}")
                print(f"      Expires: {expiry_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                print()
        
    except Exception as e:
        print(f"❌ Error checking expiring passwords: {str(e)}")

if __name__ == "__main__":
    print("Password Expiry Notification Test Script")
    print("========================================")
    
    # Check current expiring passwords
    check_users_with_expiring_passwords()
    
    # Ask user if they want to run the test
    print("\n" + "⚠️  WARNING: This test will create a temporary user and send a test email!")
    print("Make sure to update the test email address in the script before running.")
    
    response = input("\nDo you want to proceed with the test? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        test_password_expiry_notifications()
    else:
        print("Test cancelled.")