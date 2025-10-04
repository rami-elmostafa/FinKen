import os
from supabase import create_client, Client
from passwordHash import *
from FinishSignUp import _password_policy_ok
from dotenv import load_dotenv  # <-- 1. IMPORT the library
load_dotenv()

def find_user(email: str, userid: int):
    """
    Verify if a user exists in the database by email or username.
    
    Args:
        email (str): The user's email address
        userid (str): The user's suerid
    Returns:
        dict: Response containing status and message
    """

    try:
        # Initialize Supabase client
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and API key must be set in environment variables")
        
        supabase = create_client(supabase_url, supabase_key)
        
        #Query users table to match userid and email
        response = supabase.table('users').select('UserID', 'Email').eq('UserID', userid).single().execute()
        
        #verify user exists
        if not response.data:
            return {
                'success': False,
                'message': 'UserID not found'
            }
    
        #check if email matches
        user = response.data[0]
        if user.get('Email') != email:
            return {
                'success': False, 
                'message': 'Email does not match userid'
            }
        
        return {
            'success': True,
            'message': 'User exists',
            'user': user,  # Return the matching user
            'user_id': user.get('UserID')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    
def security_answer(user_id: int, question_id: int, answer: str):
    """
    Verify the answer to a security question for a given user.
    
    Args:
        user_id (int): The user's ID    
        question_id (int): The ID of the security question
        answer (str): The answer to verify
    Returns:
        dict: Response containing status and message
    """
    try:
        # Initialize Supabase client
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and API key must be set in environment variables")
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Query the security_answers table to verify the answer
        response = supabase.table('security_answers').select('*').eq('UserID', user_id).eq('QuestionID', question_id).single().execute()

        if not response.data:
            return {
                'success': False,
                'message': 'No security answer found for this user and question'
            }

        stored_hash = response.data.get('AnswerHash')
        
        if not verify_password(answer, stored_hash):
            return {
                'success': False,
                'message': 'Incorrect answer to security question'
            }

        return {
            'success': True,
            'message': 'Security answer verified'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    

def reset_password(user_id: int, new_password: str):
    """
    Reset the password for a given user.
    
    Args:
        user_id (int): The user's ID
        new_password (str): The new password to set
    Returns:
        dict: Response containing status and message
    """
    try:
        # Initialize Supabase client
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and API key must be set in environment variables")
        
        supabase = create_client(supabase_url, supabase_key)

        # Validate the new password against the policy
        is_valid, message = _password_policy_ok(new_password)
        
        if not is_valid: 
            return {
                'success': False,
                'message': f'Password does not meet policy requirements: {message}'
            }

        # Hash the new password
        hashed_password = hash_password(new_password)

        # Verify that new password hasn't been used
        for row in (supabase.table('password_history').select('PasswordHash').eq("UserID", user_id).execute()).data:
            if verify_password(new_password, row['PasswordHash']):
                return {
                    'success': False,
                    'message': 'New password cannot be the same as a previous password'
                }
        
        # Update the user's password in the database
        response = supabase.table('users').update({'PasswordHash': hashed_password}).eq('UserID', user_id).single().execute()
        response = supabase.table('password_history').update({'PasswordHash': hashed_password}).eq('UserID', user_id).single().execute()
        
        #check if update was successful
        if not response.data:
            return {
                'success': False,
                'message': 'Failed to reset password'
            }
        
        return {
            'success': True,
            'message': 'Password reset successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }