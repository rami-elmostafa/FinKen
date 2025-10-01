import os
from supabase import create_client, Client
from passwordHash import verify_password

def sign_in_user(username, password):
    """
    Authenticate a user by checking their username and password against the database.
    
    Args:
        username (str): The username to authenticate
        password (str): The plain text password to verify
        
    Returns:
        dict: Authentication result with success flag, message, and user data if successful
    """
    try:
        # Initialize Supabase client
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            return {
                'success': False,
                'message': 'Database configuration error',
                'user_data': None
            }
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Validate input
        if not username or not username.strip():
            return {
                'success': False,
                'message': 'Username is required',
                'user_data': None
            }
        
        if not password:
            return {
                'success': False,
                'message': 'Password is required',
                'user_data': None
            }
        
        # Clean the username
        username = username.strip()
        
        # Query the users table for the username
        # Note: Assuming the users table has columns: Username, PasswordHash, and user details
        response = supabase.table('Users').select('*').eq('Username', username).execute()
        
        # Check if user exists
        if not response.data or len(response.data) == 0:
            return {
                'success': False,
                'message': 'Invalid username or password',
                'user_data': None
            }
        
        user_record = response.data[0]
        
        # Check if user account is active
        if user_record.get('IsActive', True) is False:
            return {
                'success': False,
                'message': 'Account is deactivated. Please contact an administrator.',
                'user_data': None
            }
        
        # Check if user is suspended
        if user_record.get('IsSuspended', False) is True:
            return {
                'success': False,
                'message': 'Account is suspended. Please contact an administrator.',
                'user_data': None
            }
        
        # Verify the password using the passwordHash module
        stored_password_hash = user_record.get('PasswordHash')
        if not stored_password_hash:
            return {
                'success': False,
                'message': 'Account configuration error. Please contact an administrator.',
                'user_data': None
            }
        
        # Verify password
        if not verify_password(password, stored_password_hash):
            # Update failed login attempts (optional - requires FailedLoginAttempts column)
            try:
                failed_attempts = user_record.get('FailedLoginAttempts', 0) + 1
                supabase.table('Users').update({
                    'FailedLoginAttempts': failed_attempts,
                    'LastFailedLogin': 'now()'
                }).eq('Username', username).execute()
                
                # Check if user should be suspended after 3 failed attempts
                if failed_attempts >= 3:
                    supabase.table('Users').update({
                        'IsSuspended': True,
                        'SuspensionReason': 'Too many failed login attempts'
                    }).eq('Username', username).execute()
                    
                    return {
                        'success': False,
                        'message': 'Account suspended due to too many failed login attempts. Please contact an administrator.',
                        'user_data': None
                    }
                
            except Exception:
                # If updating failed attempts fails, continue with regular error message
                pass
            
            return {
                'success': False,
                'message': 'Invalid username or password',
                'user_data': None
            }
        
        # Password is correct - reset failed login attempts and update last login
        try:
            supabase.table('Users').update({
                'FailedLoginAttempts': 0,
                'LastLogin': 'now()'
            }).eq('Username', username).execute()
        except Exception:
            # If updating login info fails, continue with successful login
            pass
        
        # Return successful authentication with user data (excluding sensitive info)
        user_data = {
            'user_id': user_record.get('UserID'),
            'username': user_record.get('Username'),
            'first_name': user_record.get('FirstName'),
            'last_name': user_record.get('LastName'),
            'email': user_record.get('Email'),
            'role': user_record.get('Role', 'accountant'),  # Default to accountant role
            'is_active': user_record.get('IsActive', True)
        }
        
        return {
            'success': True,
            'message': 'Login successful',
            'user_data': user_data
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Authentication error: {str(e)}',
            'user_data': None
        }

def validate_sign_in_input(username, password):
    """
    Validate sign-in input before processing.
    
    Args:
        username (str): The username to validate
        password (str): The password to validate
        
    Returns:
        dict: Validation result with success flag and message
    """
    errors = []
    
    # Check required fields
    if not username or not username.strip():
        errors.append("Username is required")
    
    if not password:
        errors.append("Password is required")
    
    # Basic username validation
    if username and len(username.strip()) < 3:
        errors.append("Username must be at least 3 characters long")
    
    # Basic password validation
    if password and len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if errors:
        return {
            'success': False,
            'message': '; '.join(errors)
        }
    
    return {
        'success': True,
        'message': 'Validation passed'
    }
