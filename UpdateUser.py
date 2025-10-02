import os
from supabase import create_client, Client

def update_user(
        user_id: int | None = None, 
        first_name: str | None = None, 
        last_name: str | None = None, 
        email: str | None = None, 
        dob: str | None = None, 
        address: str | None = None, 
        roleid: int | None = None, 
    ):
    """
    Update user information in the Supabase database.

    Args:
        user_id (int): The ID of the user to update.
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email address
        dob (str): User's date of birth (YYYY-MM-DD format)
        address (str): User's address
        roleid (int): User's role ID
    Returns:
        dict: The updated user record or error message.
    """
    #Attemp to initialize Supabase client
    try:
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and API key must be set in environment variables")
        
        supabase: Client = create_client(supabase_url, supabase_key)
    except Exception as e:
        return {"error": f"Error initializing Supabase client: {str(e)}"}
    
    #Determine which fields to update
    try:
        update_data = {}
        if first_name is not None:
            update_data[first_name] = first_name
        if last_name is not None:
            update_data[last_name] = last_name
        if email is not None:
            update_data[email] = email
        if dob is not None:
            update_data[dob] = dob
        if address is not None:
            update_data[address] = address
        if roleid is not None:
            update_data[roleid] = roleid
        if not update_data:
            return {"error": "No fields to update."}
        
        response = supabase.table("Users").update(update_data).eq("UserID", user_id).execute()
        if response.data:
            return {"success": True, "data": response.data[0]}
        else:
            return {"error": "User not found or no changes made."}
    except Exception as e:
        return {"error": str(e)}