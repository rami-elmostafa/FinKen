import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from supabase import create_client, Client
from dotenv import load_dotenv  # <-- 1. IMPORT the library
load_dotenv()

def verify_user(email: str, username: str):
    """
    Verify if a user exists in the database by email or username.
    
    Args:
        email (str): The user's email address
        username (str): The user's username
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
        response = supabase.table('users').select('*').eq('Email', email).eq('Username', username).execute()
        
        if response.data:
            return {
                'success': True,
                'message': 'User exists',
                'user': response.data[0]  # Return the first matching user
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
    
    