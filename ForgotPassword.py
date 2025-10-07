from SupabaseClient import _sb
from passwordHash import *
from FinishSignUp import _password_policy_ok, _now_utc

def find_user(email: str, username: str, sb = None):
    """
    Verify if a user exists in the database by email and username.
    
    Args:
        email (str): The user's email address
        username (str): The user's username
    Returns:
        dict: Response containing status and message
    """

    try:
        #Initialize Supabase client
        sb = sb or _sb()
        
        #Query users table to match username and email
        response = sb.table('users').select('UserID, Email, Username').eq('Username', username).execute()
        
        #Verify user exists
        if not response.data or len(response.data) == 0:
            return {
                'success': False,
                'message': 'Email address and username combination does not exist. Contact an admin for more information.'
            }
        
        #Check if email matches
        user = response.data[0]  # Get first (and should be only) result
        if user.get('Email') != email:
            return {
                'success': False, 
                'message': 'Email address and username combination does not exist. Contact an admin for more information.'
            }
        return {
            'success': True,
            'message': 'User exists',
            'user_id': user.get('UserID')  # Return the actual UserID for later use
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': 'Email address and username combination does not exist. Contact an admin for more information.'
        }
    
    
def security_answer(user_id: int, answer: str, sb = None):
    """
    Verify the answer to a security question for a given user.
    
    Args:
        user_id (int): The user's ID    
        question_id (int): The ID of the security question provided by form
        answer (str): The answer to verify
    Returns:
        dict: Response containing status and message
    """
    try:
        #Initialize Supabase client
        sb = sb or _sb()
        
        #Query the security_answers table to verify the answer
        response = sb.table('user_security_answers').select('*').eq('UserID', user_id).single().execute()

        if not response.data:
            return {
                'success': False,
                'message': 'No security question found for this user'
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
    

def change_password(userid: int, new_password: str, sb = None):
    """
    Reset the password for a given user.
    
    Args:
        user_id (int): The user's ID
        new_password (str): The new password to set
    Returns:
        dict: Response containing status and message
    """
    try:
        #Initialize Supabase client
        sb = sb or _sb()

        #Validate the new password against the policy
        is_valid, message = _password_policy_ok(new_password)
        
        if not is_valid: 
            return {
                'success': False,
                'message': f'Password does not meet policy requirements: {message}'
            }

        #Hash the new password
        hashed_password = hash_password(new_password)

        #Verify that new password hasn't been used
        for row in (sb.table('password_history').select('PasswordHash').eq("UserID", userid).execute()).data:
            if verify_password(new_password, row['PasswordHash']):
                return {
                    'success': False,
                    'message': 'New password cannot be the same as a previous password'
                }
            
        #Update the user's password in the database
        response = sb.table('users').update({'PasswordHash': hashed_password}).eq('UserID', userid).execute()
        created_at = _now_utc()
        response = sb.table('password_history').insert({'PasswordHash': hashed_password, 'UserID': userid, 'DateSet': created_at.isoformat()}).execute()
        
        #Check if update was successful
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

    
