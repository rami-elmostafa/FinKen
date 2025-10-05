from SupabaseClient import _sb

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
    # Validate user_id
    if user_id is None:
        return {"success": False, "message": "User ID is required"}
    
    #Attempt to initialize Supabase client
    try:
        # Initialize Supabase client
        sb = sb or _sb()
    except Exception as e:
        return {"success": False, "message": f"Error initializing Supabase client: {str(e)}"}
    
    #Determine which fields to update
    try:
        update_data = {}
        if first_name is not None and first_name.strip():
            update_data['FirstName'] = first_name.strip()
        if last_name is not None and last_name.strip():
            update_data['LastName'] = last_name.strip()
        if email is not None and email.strip():
            update_data['Email'] = email.strip()
        if dob is not None and dob.strip():
            update_data['DOB'] = dob.strip()
        if address is not None:
            update_data['Address'] = address.strip() if address.strip() else None
        if roleid is not None:
            update_data['RoleID'] = roleid
            
        if not update_data:
            return {"success": False, "message": "No fields to update"}
        
        response = sb.table("users").update(update_data).eq("UserID", user_id).execute()
        
        if response.data and len(response.data) > 0:
            return {"success": True, "message": "User updated successfully", "data": response.data[0]}
        else:
            return {"success": False, "message": "User not found or no changes made"}
            
    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}