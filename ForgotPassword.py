import os
from supabase import create_client, Client
from passwordHash import hash_password
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
        
        # Query the users table to check for existence
        response = supabase.table('users').select('UserID', 'Email').eq('UserID', userid).single().execute()
        
        if response.data:
            user = response.data[0]
            if user.get('Email') == email:
                return {
                    'success': True,
                    'message': 'User exists',
                    'user': user,  # Return the matching user
                    'user_id': user.get('UserID')
                }
            else:
                return {
                    'success': False, 
                    'message': 'Email does not match userid'
                }
        else:
            return {
                'success': False,
                'message': 'User not found'
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

        # Hash the provided answer
        hashed_answer = hash_password(answer)
        
        # Query the security_answers table to verify the answer
        response = supabase.table('security_answers').select('*').eq('UserID', user_id).eq('QuestionID', question_id).execute()

        # Null data handling
        rows = response.data or []
        if not rows:
            return {
                'success': False,
                'message': 'No security answer found for this user and question'
            }
        
        if response.data:
            if response.data[0].get('AnswerHash') == hashed_answer:
                return {
                    'success': True,
                    'message': 'Security answer verified'
                }
            else:
                return {
                    'success': False,
                    'message': 'Incorrect answer to security question'
                }
        else:
            return {
                'success': False,
                'message': 'Incorrect answer to security question'
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

        # Ensure the new password is not the same as an old one
        histoy_response = supabase.table('password_history').select('PasswordHash').eq("UserID", user_id).eq("PasswordHash", hashed_password).limit(1).execute()
        
        if histoy_response.data:
            return {
                'success': False,
                'message': 'New password cannot be the same as a previous password'
            }
        
        # Update the user's password in the database
        response = supabase.table('users').update({'PasswordHash': hashed_password}).eq('UserID', user_id).execute()
        
        if response.data:
            return {
                'success': True,
                'message': 'Password reset successfully'
            }
        else:
            return {
                'success': False,
                'message': 'Failed to reset password'
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }