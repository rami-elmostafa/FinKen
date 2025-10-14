import contextvars
import os
from supabase import create_client
from dotenv import load_dotenv

# Create a context variable to store current user ID for audit logging
current_user_id = contextvars.ContextVar('current_user_id', default=None)

def set_current_user(user_id):
    """Set the current user for audit logging"""
    current_user_id.set(user_id)

def get_current_user():
    """Get the current user for audit logging"""
    return current_user_id.get()

def _sb():
    # Load environment variables from a .env file if present
    # Many dev setups keep a file named `.env`; this project currently has an `env` file
    # (without the leading dot). Try both so local runs work without renaming files.
    load_dotenv()  # loads .env by default

    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_ANON_KEY')

    # If variables are missing, try loading fallback 'env' file used in this repo
    if (not url or not key) and os.path.exists('env'):
        load_dotenv('env')
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_ANON_KEY')

    if not url or not key:
        raise RuntimeError("Supabase environment is not configured")
    
    client = create_client(url, key)
    
    # Set session variable for audit logging if user context is available
    user_id = get_current_user()
    if user_id:
        try:
            # Use RPC to set session variable for audit logging
            client.rpc('set_audit_user_context', {'user_id': str(user_id)}).execute()
        except Exception as e:
            # If setting the session variable fails, continue without it
            # The triggers will fall back to default user detection
            print(f"Warning: Could not set user context for audit logging: {e}")
    
    return client