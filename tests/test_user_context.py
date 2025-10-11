#!/usr/bin/env python3
"""
Simple test to verify user context is being passed correctly
Run this after setting up the enhanced audit system
"""

import sys
import os
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from SupabaseClient import _sb, set_current_user
    print("✓ Successfully imported SupabaseClient functions")
except ImportError as e:
    print(f"✗ Failed to import SupabaseClient: {e}")
    sys.exit(1)

def test_user_context_propagation():
    """Test that user context is properly passed to the database"""
    print("\n🔍 Testing User Context Propagation...")
    
    try:
        # Set a test user context
        test_user_id = 2  # Change this to an existing user ID in your system
        set_current_user(test_user_id)
        print(f"✓ Set user context to: {test_user_id}")
        
        # Get Supabase client (this should set the session variable)
        sb = _sb()
        print("✓ Created Supabase client with user context")
        
        # Insert a test security question
        test_question = f"User context test - {datetime.now()}"
        result = sb.table('security_questions').insert({
            'QuestionText': test_question
        }).execute()
        
        if result.data:
            question_id = result.data[0]['QuestionID']
            print(f"✓ Inserted test security question with ID: {question_id}")
            
            # Check the audit log
            audit_result = sb.table('event_logs').select('*').eq('tablename', 'security_questions').eq('recordid', question_id).eq('actiontype', 'INSERT').execute()
            
            if audit_result.data:
                audit_log = audit_result.data[0]
                logged_user_id = audit_log['userid']
                
                if logged_user_id == test_user_id:
                    print(f"🎉 SUCCESS: Audit log shows correct user ID: {logged_user_id}")
                else:
                    print(f"⚠️  ISSUE: Expected user ID {test_user_id}, but audit log shows: {logged_user_id}")
                
                print(f"   Audit details: Action={audit_log['actiontype']}, Table={audit_log['tablename']}, Time={audit_log['timestamp']}")
            else:
                print("✗ No audit log found for the test operation")
            
            # Clean up
            sb.table('security_questions').delete().eq('QuestionID', question_id).execute()
            print("✓ Cleaned up test data")
            
        else:
            print("✗ Failed to insert test security question")
            return False
            
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")
        return False
    
    return True

def test_without_user_context():
    """Test what happens when no user context is set"""
    print("\n🔍 Testing Without User Context...")
    
    try:
        # Don't set user context
        sb = _sb()
        
        # Insert a test security question
        test_question = f"No context test - {datetime.now()}"
        result = sb.table('security_questions').insert({
            'QuestionText': test_question
        }).execute()
        
        if result.data:
            question_id = result.data[0]['QuestionID']
            print(f"✓ Inserted test security question without user context")
            
            # Check the audit log
            audit_result = sb.table('event_logs').select('*').eq('tablename', 'security_questions').eq('recordid', question_id).eq('actiontype', 'INSERT').execute()
            
            if audit_result.data:
                audit_log = audit_result.data[0]
                logged_user_id = audit_log['userid']
                print(f"✓ Audit log created with fallback user ID: {logged_user_id}")
            else:
                print("✗ No audit log found for operation without user context")
            
            # Clean up
            sb.table('security_questions').delete().eq('QuestionID', question_id).execute()
            print("✓ Cleaned up test data")
        
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")

if __name__ == "__main__":
    print("🧪 User Context Audit Test Suite")
    print("=" * 50)
    
    # Test with user context
    success = test_user_context_propagation()
    
    # Test without user context
    test_without_user_context()
    
    if success:
        print("\n✅ User context propagation is working!")
        print("\nNext steps:")
        print("1. Update a user through your Flask app")
        print("2. Check event_logs table to see if it shows the correct user")
    else:
        print("\n❌ User context propagation needs debugging")
        print("\nTroubleshooting steps:")
        print("1. Make sure you've run enhanced_audit_with_context.sql")
        print("2. Verify the RPC function set_audit_user_context exists")
        print("3. Check if user ID exists in your users table")