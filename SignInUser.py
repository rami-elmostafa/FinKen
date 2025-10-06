from SupabaseClient import _sb
from passwordHash import verify_password

def sign_in_user(username, password, sb = None):
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
        sb = sb or _sb()
        
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
        response = sb.table('users').select('*').eq('Username', username).execute()
        
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
                sb.table('users').update({
                    'FailedLoginAttempts': failed_attempts,
                    'LastFailedLogin': 'now()'
                }).eq('Username', username).execute()
                
                # Check if user should be suspended after 3 failed attempts
                if failed_attempts >= 3:
                    sb.table('users').update({
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
            sb.table('users').update({
                'FailedLoginAttempts': 0,
                'LastLogin': 'now()'
            }).eq('Username', username).execute()
        except Exception:
            # If updating login info fails, continue with successful login
            pass

        # Resolve role name from RoleID via roles table; normalize and fallback
        role_name = 'accountant'
        role_id_raw = user_record.get('RoleID')
        role_id = None
        try:
            if role_id_raw is not None:
                role_id = int(role_id_raw)
        except (TypeError, ValueError):
            role_id = None

        if role_id is not None:
            try:
                role_resp = sb.table('roles').select('RoleName').eq('RoleID', role_id).limit(1).execute()
                if role_resp.data and len(role_resp.data) > 0:
                    rn = role_resp.data[0].get('RoleName')
                    if isinstance(rn, str) and rn.strip():
                        role_name = rn.strip().lower()
            except Exception:
                pass

        if role_name not in ('administrator', 'manager', 'accountant'):
            role_name = {1: 'administrator', 2: 'manager', 3: 'accountant'}.get(role_id, 'accountant')
        
        # Return successful authentication with user data (excluding sensitive info)
        user_data = {
            'user_id': user_record.get('UserID'),
            'username': user_record.get('Username'),
            'first_name': user_record.get('FirstName'),
            'last_name': user_record.get('LastName'),
            'email': user_record.get('Email'),
            'role': role_name,
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
