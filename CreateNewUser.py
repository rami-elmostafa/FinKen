import os
from datetime import datetime
from supabase import create_client, Client
from passwordHash import hash_password

def create_new_user(first_name, last_name, email, dob):
    """
    Create a new user registration request in the Supabase database.
    
    Args:
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email address
        dob (str): User's date of birth (YYYY-MM-DD format)
        
    Returns:
        dict: Response from the database insertion
    """
    try:
        # Initialize Supabase client
        # You'll need to set these environment variables
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and API key must be set in environment variables")
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Validate date of birth format
        try:
            datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date of birth must be in YYYY-MM-DD format")
        
        # Prepare user data for insertion
        user_data = {
            'FirstName': first_name.strip(),
            'LastName': last_name.strip(),
            'Email': email.strip().lower(),
            'DOB': dob,
            'Address': '',  # Empty for now since we don't collect address in the form
            'RequestDate': datetime.now().isoformat()
        }
        
        # Insert data into RegistrationRequests table
        response = supabase.table('registration_requests').insert(user_data).execute()
        
        if response.data:
            return {
                'success': True,
                'message': 'User registration request submitted successfully',
                'user_id': response.data[0]['RequestID'] if response.data else None
            }
        else:
            return {
                'success': False,
                'message': 'Failed to submit registration request'
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error creating user: {str(e)}'
        }

def validate_user_input(first_name, last_name, email, dob):
    """
    Validate user input before creating the user.
    
    Args:
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email address
        dob (str): User's date of birth
        
    Returns:
        dict: Validation result with success flag and message
    """
    errors = []
    
    # Check required fields
    if not first_name or not first_name.strip():
        errors.append("First name is required")
    
    if not last_name or not last_name.strip():
        errors.append("Last name is required")
    
    if not email or not email.strip():
        errors.append("Email is required")
    elif '@' not in email or '.' not in email:
        errors.append("Please enter a valid email address")
    
    if not dob:
        errors.append("Date of birth is required")
    else:
        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d')
            # Check if user is at least 16 years old
            today = datetime.now()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
            if age < 16:
                errors.append("You must be at least 16 years old to register")
        except ValueError:
            errors.append("Date of birth must be in YYYY-MM-DD format")
    
    if errors:
        return {
            'success': False,
            'message': '; '.join(errors)
        }
    
    return {
        'success': True,
        'message': 'Validation passed'
    }